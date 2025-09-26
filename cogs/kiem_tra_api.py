import discord

from discord import app_commands
from discord.ext import commands

from utils.embed import error_embed, create_embed, EmbedColor
from utils.embed import error_embed, disabled_command_embed
from api.card2k.exchange_card import ExchangeCard as ExchangeCardAPI
from utils.config import get_config_value
from helpers.console import logger


class KiemTraAPI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.exchange_card_api = ExchangeCardAPI()
        self.enabled = get_config_value("commands.kiem_tra_api.enabled", False)
        self.only_admin = get_config_value("commands.kiem_tra_api.only_admin", False)

    @app_commands.command(
        name="kiem_tra_api", 
        description=get_config_value("commands.kiem_tra_api.description", "Kiểm tra trạng thái API")
    )
    async def kiem_tra_api_command(self, interaction: discord.Interaction):
        """
        Kiểm tra trạng thái API
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
            kiem_tra_api_service = self.exchange_card_api.check_status_api()
            description = ""
            if kiem_tra_api_service:
                description = "🟢 API đang `hoạt động`"
                color = EmbedColor.SUCCESS
            else:
                description = "🔴 API đang `không hoạt động`"
                color = EmbedColor.ERROR
            embed = create_embed(
                title="Kiểm tra trạng thái API",
                description=description,
                color=color,
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"[COG: KIEM_TRA_API] Lỗi: {e}")
            message_error = error_embed(f"Lỗi khi sử dụng lệnh, vui lòng thử lại sau.")
            await interaction.response.send_message(embed=message_error, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(KiemTraAPI(bot))
