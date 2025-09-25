import discord

from discord import app_commands
from discord.ext import commands

from services.card2k.fee_service import FeeService
from utils.embed import error_embed, create_embed, EmbedColor
from helpers.console import logger


class ExchangeCard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="nap_the_cao", description="Nạp thẻ cào")
    async def nap_the_cao_command(self, interaction: discord.Interaction):
        """
        Nạp thẻ cào
        """

        try:
            fee = FeeService().get_min_fees_by_telco()
            logger.info(f"[Debug] get_fee_exchange_card: {fee}")

            embed = create_embed(
                title="Nạp thẻ cào",
                description=f"Run !!",
                color=EmbedColor.INFO,
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"[COG: NAP_THE_CAO] Lỗi: {e}")
            message_error = error_embed(f"Lỗi khi sử dụng lệnh, vui lòng thử lại sau.")
            await interaction.response.send_message(embed=message_error, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ExchangeCard(bot))
