import discord
from discord import app_commands
from discord.ext import commands
from helpers.embeds import help_embed
from helpers.console import add_log

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Xem hướng dẫn sử dụng bot")
    async def help_command(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message(embed=help_embed(), ephemeral=True)
            add_log("Hướng dẫn sử dụng bot", "INFO")
        except Exception as e:
            add_log(f"Lỗi không xác định trong lệnh: 'help'. Chi tiết: {e}", "ERROR")

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
