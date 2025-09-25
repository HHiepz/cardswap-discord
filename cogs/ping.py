import discord

from discord import app_commands
from discord.ext import commands

from utils.embed import error_embed, create_embed, EmbedColor
from helpers.console import logger


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Kiểm tra ping của bot")
    async def ping_command(self, interaction: discord.Interaction):
        """
        Kiểm tra ping của bot
        """

        try:
            ping = self.bot.latency * 1000
            embed = create_embed(
                title="Kiểm tra ping của bot",
                description=f"Ping của bot là `{ping:.2f}ms`",
                color=EmbedColor.INFO,
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"[COG: PING] Lỗi: {e}")
            message_error = error_embed(f"Lỗi khi sử dụng lệnh, vui lòng thử lại sau.")
            await interaction.response.send_message(embed=message_error, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))
