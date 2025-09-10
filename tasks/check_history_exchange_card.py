# tasks/card_checker.py
import discord
from discord.ext import commands, tasks
import time
from helpers.api import check_card_status
from helpers.console import add_log
from helpers.helper import get_data_file_yml
from helpers.embeds import card_success_embed, card_wrong_amount_embed, card_failed_embed
from database.session import SessionLocal
from database.models import HistoryExchangeCard, Card2k

class CheckHistoryExchangeCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = get_data_file_yml()
        
        if self.config.get("card_status_check", {}).get("type") == "api":
            self.delay_time = int(self.config.get("card_status_check", {}).get("delay_time", 60))

            # Nếu delay_time nhỏ hơn 30 thì set lại thành 30
            if self.delay_time < 30:
                self.delay_time = 30

            # Khởi tạo task loop với delay_time động
            self.check_history_exchange_card.change_interval(seconds=self.delay_time)
            self.check_history_exchange_card.start()
            # Khởi tạo session để xử lý database
            self.session = SessionLocal()
        else:
            add_log("Kiểm tra lịch sử đổi thẻ cào bằng callback.", "INFO")

    def cog_unload(self):
        self.check_history_exchange_card.cancel()
        self.session.close()

    @tasks.loop(seconds=60)
    async def check_history_exchange_card(self):
        await self._validated_setup()

        history_exchange_cards = self.session.query(HistoryExchangeCard).filter(HistoryExchangeCard.status == "pending").all()

        if len(history_exchange_cards) == 0:
            add_log("Không có thẻ đang chờ xử lý.", "INFO")
            return

        for card_pending in history_exchange_cards:
            add_log(f"Phát hiện thẻ đang chờ xử lý: {card_pending.transaction_id}", "INFO")
            response = check_card_status(card_pending.telco, card_pending.value, card_pending.code, card_pending.serial, card_pending.request_id)

            if response is None:
                add_log(f"Lỗi khi kiểm tra trạng thái thẻ: {card_pending.transaction_id}", "ERROR")
                continue
            
            elif response["status"] == 99:
                add_log(f"Thẻ đã được xử lý: #{card_pending.transaction_id}", "INFO")
                continue
            
            elif response["status"] == 4:
                add_log(f"Hệ thống đang bảo trì: #{card_pending.transaction_id}", "INFO")
                continue
            
            elif response["status"] == 1:
                add_log(f"Thẻ thành công - đúng mệnh giá: #{card_pending.transaction_id}", "INFO")
                # Cập nhật trạng thái
                card_pending.card_value = response["declared_value"]
                card_pending.status = "success"
                self.session.commit()
                
                # Cập nhật Discord message
                await self._update_discord_message(card_pending, "success")
                continue

            elif response["status"] == 2:
                add_log(f"Thẻ thành công - sai mệnh giá - trừ 50% giá trị: #{card_pending.transaction_id}", "INFO")
                # Cập nhật trạng thái
                card_pending.card_value = response["declared_value"]
                card_pending.status = "wrong_amount"
                self.session.commit()
                
                # Cập nhật Discord message
                await self._update_discord_message(card_pending, "wrong_amount")
                continue

            else:
                add_log(f"Thẻ lỗi - {response['message']}: #{card_pending.transaction_id}", "ERROR")
                card_pending.status = "failed"
                self.session.commit()
                
                # Cập nhật Discord message
                await self._update_discord_message(card_pending, "failed", response.get("message"))
                continue

    # Hàm này đảm bảo vòng lặp chỉ bắt đầu sau khi bot đã đăng nhập và sẵn sàng
    @check_history_exchange_card.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()
        add_log("Task Check History Exchange Card đã được khởi động.", "INFO")

    # Kiểm tra setup 
    async def _validated_setup(self):
        data = self.session.query(Card2k).first()
        if not data or not data.partner_id or not data.partner_key:
            return add_log("Người dùng cố gắng nạp thẻ cào nhưng database rỗng.", "WARNING")
        
        if not self.config["provider"]:
            return add_log("Người dùng cố gắng nạp thẻ cào nhưng nhà cung cấp (provider) trong file settings.yml bị rỗng.", "WARNING")

    # Cập nhật Discord message khi trạng thái thẻ thay đổi
    async def _update_discord_message(self, card_history: HistoryExchangeCard, status: str, error_message: str = None):
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
                    add_log(f"Không thể tìm message trong channel {card_history.channel_discord_id}: {str(e)}", "WARNING")
            
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
                add_log(f"Không tìm thấy Discord message với ID: {message_id}", "WARNING")
                return
            
            # Tạo embed mới dựa trên trạng thái
            new_embed = None
            if status == "success":
                new_embed = card_success_embed(
                    card_history.telco,
                    card_history.value,
                    card_history.code,
                    card_history.serial,
                    card_history.transaction_id,
                    card_history.card_value
                )
            elif status == "wrong_amount":
                new_embed = card_wrong_amount_embed(
                    card_history.telco,
                    card_history.value,
                    card_history.code,
                    card_history.serial,
                    card_history.transaction_id,
                    card_history.card_value
                )
            elif status == "failed":
                new_embed = card_failed_embed(
                    card_history.telco,
                    card_history.value,
                    card_history.code,
                    card_history.serial,
                    card_history.transaction_id,
                    error_message
                )
            
            if new_embed:
                await message.edit(embed=new_embed)
                add_log(f"Đã cập nhật Discord message cho giao dịch: {card_history.transaction_id}", "INFO")
            
        except Exception as e:
            add_log(f"Lỗi khi cập nhật Discord message cho giao dịch {card_history.transaction_id}: {str(e)}", "ERROR")


# Hàm setup() này là bắt buộc để bot có thể load file này như một Cog
async def setup(bot):
    await bot.add_cog(CheckHistoryExchangeCard(bot))
