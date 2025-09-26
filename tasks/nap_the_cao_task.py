import os
import discord


from discord.ext import commands, tasks
from database.models import HistoryExchangeCard
from database.session import SessionLocal

from api.card2k.exchange_card import ExchangeCard as ExchangeCardAPI
from utils.config import get_config_value, get_config
from utils.env import get_env
from utils.embed import error_embed, _add_footer, success_embed, disabled_command_embed
from helpers.console import logger

class NapTheCaoTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.nap_the_cao_service = ExchangeCardAPI()
        
        if get_config_value("card_status_check", {}).get("type") == "api":
            self.delay_time = int(get_config_value("card_status_check", {}).get("delay_time", 60))

            # Nếu delay_time nhỏ hơn 30 thì set lại thành 30
            if self.delay_time < 30:
                self.delay_time = 30

            # Khởi tạo task loop với delay_time động
            self.check_history_exchange_card.change_interval(seconds=self.delay_time)
            self.check_history_exchange_card.start()
            # Khởi tạo session để xử lý database
            self.session = SessionLocal()
        else:
            logger.info("[TASK: NAP_THE_CAO] Kiểm tra lịch sử đổi thẻ cào bằng callback.")

    def cog_unload(self):
        self.check_history_exchange_card.cancel()
        self.session.close()

    @tasks.loop(seconds=60)
    async def check_history_exchange_card(self):
        await self._validated_setup()

        history_exchange_cards = self.session.query(HistoryExchangeCard).filter(HistoryExchangeCard.status == "pending").all()

        if len(history_exchange_cards) == 0:
            logger.info("[TASK: NAP_THE_CAO] Không có thẻ đang chờ xử lý.")
            return

        for card_pending in history_exchange_cards:
            logger.info(f"[TASK: NAP_THE_CAO] Phát hiện thẻ đang chờ xử lý: {card_pending.transaction_id}")
            data = {
                "telco": card_pending.telco,
                "amount": card_pending.value,
                "code": card_pending.code,
                "serial": card_pending.serial,
                "request_id": card_pending.request_id,
            }
            response = self.nap_the_cao_service.check_exchange_card(data)

            if response is None:
                logger.error(f"[TASK: NAP_THE_CAO] Lỗi khi kiểm tra trạng thái thẻ: {card_pending.transaction_id}")
                continue
            
            elif response["status"] == 99:
                logger.info(f"[TASK: NAP_THE_CAO] Thẻ đã được xử lý: #{card_pending.transaction_id}")
                continue
            
            elif response["status"] == 4:
                logger.info(f"[TASK: NAP_THE_CAO] Hệ thống đang bảo trì: #{card_pending.transaction_id}")
                continue
            
            elif response["status"] == 1:
                logger.info(f"[TASK: NAP_THE_CAO] Thẻ thành công - đúng mệnh giá: #{card_pending.transaction_id}")
                # Cập nhật trạng thái
                card_pending.card_value = response["declared_value"]
                card_pending.status = "success"
                self.session.commit()
                
                # Cập nhật Discord message
                await self._update_discord_message(card_pending, "success")
                continue

            elif response["status"] == 2:
                logger.info(f"[TASK: NAP_THE_CAO] Thẻ thành công - sai mệnh giá - trừ 50% giá trị: #{card_pending.transaction_id}")
                # Cập nhật trạng thái
                card_pending.card_value = response["declared_value"]
                card_pending.status = "wrong_amount"
                self.session.commit()
                
                # Cập nhật Discord message
                await self._update_discord_message(card_pending, "wrong_amount")
                continue

            else:
                logger.error(f"[TASK: NAP_THE_CAO] Thẻ lỗi - {response['message']}: #{card_pending.transaction_id}")
                card_pending.status = "failed"
                self.session.commit()
                
                # Cập nhật Discord message
                await self._update_discord_message(card_pending, "failed", response.get("message"))
                continue

    @check_history_exchange_card.before_loop
    async def before_check(self):
        """
        Đảm bảo vòng lặp chỉ bắt đầu sau khi bot đã đăng nhập và sẵn sàng
        """
        await self.bot.wait_until_ready()
        logger.info("[TASK: NAP_THE_CAO] Task NAP_THE_CAO đã được khởi động.")

    async def _validated_setup(self):
        """
        Kiểm tra các biến môi trường có tồn tại
        """
        required_env = ["DISCORD_TOKEN", "GUILD_ID", "PARTNER_ID", "PARTNER_KEY"]
        missing_env = [env for env in required_env if not get_env(env)]

        # Kiểm tra file .env có tồn tại
        if not os.path.exists(".env"):
            return logger.warning("[TASK: NAP_THE_CAO] File .env không tồn tại.")

        # Kiểm tra các biến môi trường có tồn tại
        if missing_env:
            return logger.warning(f"[TASK: NAP_THE_CAO] Thiếu các biến môi trường: {', '.join(missing_env)}")

    async def _update_discord_message(self, card_history: HistoryExchangeCard, status: str, error_message: str = None):
        """
        Cập nhật Discord message khi trạng thái thẻ thay đổi
        """
        try:
            # Tìm message Discord dựa trên message_discord_id và channel_discord_id
            message_id = int(card_history.message_discord_id)
            
            message = None
            
            # Nếu có channel_discord_id, tìm trực tiếp trong channel đó
            if card_history.channel_discord_id:
                try:
                    channel_id = int(card_history.channel_discord_id)
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        message = await channel.fetch_message(message_id)
                except (discord.NotFound, discord.Forbidden, discord.HTTPException, ValueError) as e:
                    logger.warning(f"[TASK: NAP_THE_CAO] Không thể tìm message trong channel {card_history.channel_discord_id}: {str(e)}")
            
            # Nếu không tìm thấy message bằng channel_id, thử tìm trong tất cả channel
            if not message:
                for guild in self.bot.guilds:
                    for channel in guild.text_channels:
                        try:
                            message = await channel.fetch_message(message_id)
                            if message:
                                break
                        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                            continue
                    if message:
                        break
            
            if not message:
                logger.warning(f"[TASK: NAP_THE_CAO] Không tìm thấy Discord message với ID: {message_id}")
                return
            
            # Tạo embed mới dựa trên trạng thái
            new_embed = None
            if status == "success":
                new_embed = self._success_embed(card_history)
            elif status == "wrong_amount":
                new_embed = self._wrong_amount_embed(card_history)
            elif status == "failed":
                new_embed = self._failed_embed(card_history, error_message)
            
            if new_embed:
                await message.edit(embed=new_embed)
                logger.info(f"[TASK: NAP_THE_CAO] Đã cập nhật Discord message cho giao dịch: {card_history.transaction_id}")
            
        except Exception as e:
            logger.error(f"[TASK: NAP_THE_CAO] Lỗi khi cập nhật Discord message cho giao dịch {card_history.transaction_id}: {str(e)}")

    def _success_embed(self, card_history: HistoryExchangeCard) -> discord.Embed:
        """
        Tạo embed thông báo thành công
        """

        telco = card_history.telco
        amount = card_history.value
        code = card_history.code
        serial = card_history.serial
        order_id = card_history.transaction_id
        card_value = card_history.card_value

        embed = discord.Embed(
            title="✅ Thẻ cào đã được xử lý thành công",
            description="Thẻ cào của bạn đã được xử lý thành công với đúng mệnh giá!",
            color=discord.Color.green(),
        )
        embed.add_field(name="Nhà mạng", value=telco, inline=True)
        embed.add_field(name="Mệnh giá", value=f"{amount:,} VND", inline=True)
        embed.add_field(name="Mã giao dịch", value=f"`{order_id}`", inline=True)
        embed.add_field(name="Mã thẻ", value=f"||{code}||", inline=True)
        embed.add_field(name="Serial", value=f"||{serial}||", inline=True)
        embed.add_field(name="Mệnh giá thực tế", value=f"**{card_value:,} VND**", inline=True)
        embed.add_field(
            name="🎉 Chúc mừng", 
            value="Thẻ cào đã được xử lý thành công với đúng mệnh giá!", 
            inline=False
        )
        embed = _add_footer(embed)
        return embed
    
    def _wrong_amount_embed(self, card_history: HistoryExchangeCard) -> discord.Embed:
        """
        Tạo embed thông báo thành công sai mệnh giá (nhận 50% giá trị)
        """

        telco = card_history.telco
        amount = card_history.value
        code = card_history.code
        serial = card_history.serial
        order_id = card_history.transaction_id
        card_value = card_history.card_value
        
        embed = discord.Embed(
            title="⚠️ Thẻ cào sai mệnh giá",
            description="Thẻ cào đã được xử lý nhưng sai mệnh giá, giá trị sẽ bị trừ 50%.",
            color=discord.Color.orange(),
        )
        embed.add_field(name="Nhà mạng", value=telco, inline=True)
        embed.add_field(name="Mệnh giá khai báo", value=f"{amount:,} VND", inline=True)
        embed.add_field(name="Mã giao dịch", value=f"`{order_id}`", inline=True)
        embed.add_field(name="Mã thẻ", value=f"||{code}||", inline=True)
        embed.add_field(name="Serial", value=f"||{serial}||", inline=True)
        embed.add_field(name="Mệnh giá thực tế", value=f"{card_value:,} VND", inline=True)
        embed.add_field(
            name="⚠️ Lưu ý", 
            value="Do thẻ sai mệnh giá, giá trị đã bị trừ 50% theo quy định.", 
            inline=False
        )
        embed = _add_footer(embed)
        return embed

    def _failed_embed(self, card_history: HistoryExchangeCard, error_message: str = None) -> discord.Embed:
        """
        Tạo embed thông báo thất bại
        """

        telco = card_history.telco
        amount = card_history.value
        code = card_history.code
        serial = card_history.serial
        order_id = card_history.transaction_id
        
        embed = discord.Embed(
            title="❌ Thẻ cào xử lý thất bại",
            description="Rất tiếc, thẻ cào của bạn không thể được xử lý.",
            color=discord.Color.red(),
        )
        embed.add_field(name="Nhà mạng", value=telco, inline=True)
        embed.add_field(name="Mệnh giá", value=f"{amount:,} VND", inline=True)
        embed.add_field(name="Mã giao dịch", value=f"`{order_id}`", inline=True)
        embed.add_field(name="Mã thẻ", value=f"||{code}||", inline=True)
        embed.add_field(name="Serial", value=f"||{serial}||", inline=True)
        embed.add_field(name="⠀", value="⠀", inline=True)  # Spacer
        if error_message:
            embed.add_field(
                name="❌ Lý do", 
                value=f"{error_message}", 
                inline=False
            )
        else:
            embed.add_field(
                name="❌ Lý do", 
                value="Thẻ cào không hợp lệ hoặc đã được sử dụng.", 
                inline=False
            )
        embed = _add_footer(embed)
        return embed



# Hàm setup() này là bắt buộc để bot có thể load file này như một Cog
async def setup(bot):
    await bot.add_cog(NapTheCaoTask(bot))
