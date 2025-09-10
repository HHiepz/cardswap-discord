import discord
from discord import app_commands
from discord.ext import commands
from helpers.embeds import ping_embed
from helpers.console import add_log


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Kiểm tra ping của bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=ping_embed(self.bot.latency * 1000)
        )
        add_log(f"Ping của bot là {self.bot.latency * 1000:.2f}ms", "INFO")


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))
