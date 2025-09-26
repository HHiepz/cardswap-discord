import discord

from discord import app_commands
from discord.ext import commands

from database.models import HistoryExchangeCard
from database.session import SessionLocal

from utils.embed import error_embed, _add_footer, success_embed, disabled_command_embed
from utils.config import get_config_value
from api.card2k.exchange_card import ExchangeCard as ExchangeCardAPI
from helpers.console import logger
from utils.string_utils import generate_uuid


class NapTheCao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.nap_the_cao_service = ExchangeCardAPI()
        self.enabled = get_config_value("commands.nap_the_cao.enabled", False)
        self.only_admin = get_config_value("commands.nap_the_cao.only_admin", False)
        self.session = SessionLocal()

    @app_commands.command(
        name="nap_the_cao",
        description=get_config_value("commands.nap_the_cao.description", "Nạp thẻ cào"),
    )
    @app_commands.choices(
        telco=[
            *[
                app_commands.Choice(name=telco_key.capitalize(), value=telco_key)
                for telco_key, enabled in get_config_value("card_types", {}).items()
                if enabled is True
            ],
        ],
        amount=[
            *[
                app_commands.Choice(name=f"{amount:,} VND", value=amount)
                for amount in [
                    5_000,
                    10_000,
                    20_000,
                    30_000,
                    50_000,
                    100_000,
                    200_000,
                    300_000,
                    500_000,
                    1_000_000,
                ]
            ]
        ],
    )
    async def nap_the_cao_command(
        self,
        interaction: discord.Interaction,
        telco: str,
        amount: int,
        code: str,
        serial: str,
    ):
        """
        Nạp thẻ cào
        """

        # Kiểm tra chức năng đã bị tắt
        if not self.enabled:
            embed = disabled_command_embed("Chức năng đã bị tắt")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Kiểm tra quyền admin nếu cần
        if self.only_admin and not interaction.user.guild_permissions.administrator:
            embed = disabled_command_embed("Lệnh này chỉ dành cho quản trị viên")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            # Kiểm tra nhà mạng
            if not self._check_telco(telco):
                embed = error_embed(f"❌ Nhà mạng `{telco}` hiện không được hỗ trợ!")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            # Kiểm tra mệnh giá
            if not self._check_amount(telco, amount):
                embed = error_embed(f"❌ Mệnh giá `{amount:,} VND` không được hỗ trợ!")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            # Kiểm tra code và serial
            if not self._check_code_serial(telco, code, serial):
                embed = error_embed(f"❌ Độ dài mã thẻ hoặc serial không hợp lệ!")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Tạo embed xác nhận
            embed = self._embed_confirm_nap_the_cao(telco, amount, code, serial)
            view = ConfirmationView(self, telco, amount, code, serial, interaction)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"[COG: NAP_THE_CAO] Lỗi: {e}")
            message_error = error_embed(f"Lỗi khi sử dụng lệnh, vui lòng thử lại sau.")
            await interaction.response.send_message(embed=message_error, ephemeral=True)

    def _check_telco(self, telco: str) -> bool:
        """
        Kiểm tra nhà mạng có hợp lệ không
        """

        if not get_config_value("card_types", {}).get(telco, False):
            return False
        return True

    def _check_amount(self, telco: str, amount: int) -> bool:
        """
        Kiểm tra mệnh giá có hợp lệ không
        """

        telco_amounts = get_config_value("card_amounts", {}).get(telco, {})
        if amount not in telco_amounts or not telco_amounts[amount]:
            return False
        return True

    def _check_code_serial(self, telco: str, code: str, serial: str) -> bool:
        """
        Kiểm tra code và serial có hợp lệ không
        """

        telco_upper = telco.upper()
        length_seri = len(serial)
        length_pin = len(code)
        format_dict = {
            "VIETTEL": {"seri": [11, 14], "pin": [13, 15]},
            "MOBIFONE": {"seri": [15], "pin": [12]},
            "VINAPHONE": {"seri": [14], "pin": [14]},
            "VNMOBI": {"seri": [16], "pin": [12]},
            "VNMB": {"seri": [16], "pin": [12]},
            "VIETNAMOBILE": {"seri": [16], "pin": [12]},
            "GARENA": {"seri": [9], "pin": [16]},
            "GARENA2": {"seri": [9], "pin": [16]},
            "ZING": {"seri": [12], "pin": [9]},
            "VCOIN": {"seri": [12], "pin": [12]},
            "GATE": {"seri": [10], "pin": [10]},
            "APPOTA": {"seri": [12], "pin": [12]},
        }

        if telco_upper not in format_dict:
            return False

        if not (serial.isalnum() and code.isalnum()):
            return False

        seri_valid = length_seri in format_dict[telco_upper]["seri"]
        pin_valid = length_pin in format_dict[telco_upper]["pin"]

        if not (seri_valid and pin_valid):
            return False

        return True
    
    def _embed_confirm_nap_the_cao(self, telco: str, amount: int, code: str, serial: str) -> discord.Embed:
        """
        Tạo embed xác nhận nạp thẻ cào
        """
        
        embed = discord.Embed(
            title="🔍 Xác nhận thông tin thẻ cào",
            description="Vui lòng kiểm tra kỹ thông tin trước khi xác nhận:",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Nhà mạng", value=telco.capitalize(), inline=True)
        embed.add_field(name="Mệnh giá", value=f"{amount:,} VND", inline=True)
        embed.add_field(name="⠀", value="⠀", inline=True)  # Spacer
        embed.add_field(name="Mã thẻ", value=f"||{code}||", inline=True)
        embed.add_field(name="Serial", value=f"||{serial}||", inline=True)
        embed.add_field(name="⠀", value="⠀", inline=True)  # Spacer
        embed.add_field(
            name="⚠️ Lưu ý", 
            value="• Vui lòng kiểm tra kỹ thông tin trước khi xác nhận\n• Nhấn **Xác nhận** để tiếp tục hoặc **Hủy** để dừng lại", 
            inline=False
        )
        embed = _add_footer(embed)
        return embed

    def _embed_waiting_for_processing(self, telco: str, amount: int, code: str, serial: str, trans_id: str) -> discord.Embed:
        """
        Tạo embed thông báo đang xử lý thẻ cào
        """
        
        embed = discord.Embed(
            title="⏳ Thẻ cào đang được xử lý",
            description="Hệ thống đã tiếp nhận yêu cầu của bạn và đang xử lý...",
            color=discord.Color.yellow(),
        )
        embed.add_field(name="Nhà mạng", value=telco, inline=True)
        embed.add_field(name="Mệnh giá", value=f"{amount:,} VND", inline=True)
        embed.add_field(name="Mã giao dịch", value=f"`{trans_id}`", inline=True)
        # embed.add_field(name="Mã thẻ", value=f"||{code}||", inline=True)
        embed.add_field(name="Serial", value=f"||{serial}||", inline=True)
        embed = _add_footer(embed)
        return embed

    async def process_card_exchange(self, interaction: discord.Interaction, telco: str, amount: int, code: str, serial: str):
        """
        Xử lý thẻ cào
        """

        try:
            # Gửi thẻ lên API
            data = {
                "telco": telco,
                "code": code,
                "serial": serial,
                "amount": amount,
                "request_id": generate_uuid(True),
            }
            response = self.nap_the_cao_service.exchange_card(data)

            # Kiểm tra kết quả
            if response is None:
                await interaction.followup.send(embed=error_embed("API lỗi, vui lòng liên hệ admin."), ephemeral=True)
                return
            if response["status"] != 99 and response["status"] != 1 and response["status"] != 2:
                await interaction.followup.send(embed=error_embed(f"{response['message']} (mã lỗi: {response['status']})"), ephemeral=True)
                logger.error(f"[COG: NAP_THE_CAO] Kết quả API: {response}")
                return

            # Xuất thông tin và lấy message ID
            followup_message = await interaction.followup.send(embed=self._embed_waiting_for_processing(telco, amount, code, serial, response["trans_id"]))

            # Cập nhật message ID vào database
            history_exchange_card = HistoryExchangeCard(
                telco=telco,
                value=amount,
                code=code,
                serial=serial,
                user_discord_id=str(interaction.user.id),
                message_discord_id=str(followup_message.id),
                channel_discord_id=str(interaction.channel.id),
                server=get_config_value("provider", "https://card2k.com"),
                request_id=response["request_id"],
                transaction_id=response["trans_id"],
                status="pending",
            )
            self.session.add(history_exchange_card)
            self.session.commit()
            logger.info(f"[COG: NAP_THE_CAO] Lưu thông tin vào database: {history_exchange_card}")

        except Exception as e:
            logger.error(f"[COG: NAP_THE_CAO] Lỗi: {e}")
            self.session.rollback()
            return

class ConfirmationView(discord.ui.View):
    def __init__(self, cog, telco: str, amount: int, code: str, serial: str, original_interaction: discord.Interaction):
        super().__init__(timeout=300)  # 5 phút timeout
        self.cog = cog
        self.telco = telco
        self.amount = amount
        self.code = code
        self.serial = serial
        self.original_interaction = original_interaction

    @discord.ui.button(label="✅ Xác nhận", style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.original_interaction.user.id:
            await interaction.response.send_message("❌ Chỉ người tạo lệnh mới có thể xác nhận!", ephemeral=True)
            return

        # Disable tất cả buttons
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=self.cog._embed_confirm_nap_the_cao(self.telco, self.amount, self.code, self.serial), view=self)
        
        # Gọi API xử lý thẻ cào
        await self.cog.process_card_exchange(interaction, self.telco, self.amount, self.code, self.serial)

    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.original_interaction.user.id:
            await interaction.response.send_message("❌ Chỉ người tạo lệnh mới có thể hủy!", ephemeral=True)
            return

        # Disable tất cả buttons
        for item in self.children:
            item.disabled = True

        cancel_embed = success_embed("✅ Đã hủy yêu cầu nạp thẻ cào.")
        await interaction.response.edit_message(embed=cancel_embed, view=self)

    async def on_timeout(self):
        # Disable tất cả buttons khi timeout
        for item in self.children:
            item.disabled = True



async def setup(bot: commands.Bot):
    await bot.add_cog(NapTheCao(bot))
