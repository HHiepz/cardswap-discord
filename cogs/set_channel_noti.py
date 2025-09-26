import discord

from discord import app_commands
from discord.ext import commands

from utils.embed import error_embed, create_embed, EmbedColor, disabled_command_embed
from utils.config import set_config_value, get_config_value
from helpers.console import logger


class SetChannelNoti(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.enabled = get_config_value("commands.kiem_tra_api.enabled", False)
        self.only_admin = get_config_value("commands.kiem_tra_api.only_admin", False)

    @app_commands.command(name="set-channel-noti", description="Cài đặt kênh thông báo")
    @app_commands.describe(channel="Kênh bạn muốn bot gửi thông báo vào.")
    @app_commands.describe(role="Vai trò bạn muốn bot gửi thông báo cho.")
    async def set_channel_noti_command(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        role: discord.Role = None,
    ):
        """
        Cài đặt kênh thông báo
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
            set_config_value("notifications.nap_the_cao.channel_id", channel.id)
            set_config_value(
                "notifications.nap_the_cao.role_id", role.id if role else None
            )
            embed = create_embed(
                title="Cài đặt kênh thông báo",
                description=f"\n**Kênh:** {channel.mention}\n**Vai trò:** {role.mention if role else 'Không có'}",
                color=EmbedColor.SUCCESS,
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"[COG: SET_CHANNEL_NOTI] Lỗi: {e}")
            message_error = error_embed(f"Lỗi khi sử dụng lệnh, vui lòng thử lại sau.")
            await interaction.response.send_message(embed=message_error, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SetChannelNoti(bot))
