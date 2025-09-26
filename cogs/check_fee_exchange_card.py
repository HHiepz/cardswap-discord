import discord
import datetime

from discord import app_commands
from discord.ext import commands

from services.card2k.fee_service import FeeService
from utils.embed import error_embed, create_embed, EmbedColor
from utils.config import get_config_value, get_config
from helpers.console import logger


class CheckFeeExchangeCard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.fee_service = FeeService()

    @app_commands.command(name="kiem_tra_phi", description="Kiểm tra phí đổi thẻ cào")
    @app_commands.choices(
        telco=[
            app_commands.Choice(name="Tất cả nhà mạng", value="all"),
            *[
                app_commands.Choice(name=telco_key.capitalize(), value=telco_key)
                for telco_key, enabled in get_config_value("card_types", {}).items()
                if enabled is True
            ],
        ]
    )
    async def kiem_tra_phi_command(self, interaction: discord.Interaction, telco: str):
        """
        Kiểm tra phí đổi thẻ cào
        """

        try:
            if telco == "all":
                # Lấy phí tất cả nhà mạng
                cheapest_telco_rate = self.fee_service.get_cheapest_telco_rate()
                list_min_fees_by_telco = self.fee_service.get_min_fees_by_telco()
                if not cheapest_telco_rate or not list_min_fees_by_telco:
                    raise Exception("Lỗi lấy phí đổi thẻ cào, vui lòng kiểm tra file logs")
                embeds = self._get_fee_min_all_telco(cheapest_telco_rate, list_min_fees_by_telco)
                await interaction.response.send_message(embeds=embeds)
            else:
                # Lấy phí theo nhà mạng
                telco_fee_info = self.fee_service.get_telco_fee_info(telco)
                if not telco_fee_info:
                    raise Exception("Lỗi lấy phí đổi thẻ cào, vui lòng kiểm tra file logs")
                embeds = self._get_fee_min_by_telco(telco_fee_info, telco)
                await interaction.response.send_message(embeds=embeds)
        except Exception as e:
            logger.error(f"[COG: KIEM_TRA_PHI] Lỗi: {e}")
            message_error = error_embed(f"Lỗi khi sử dụng lệnh, vui lòng thử lại sau.")
            await interaction.response.send_message(embed=message_error, ephemeral=True)

    def _get_fee_min_all_telco(self, cheapest_telco_rate: dict, list_min_fees_by_telco: dict) -> list[discord.Embed]:
        """
        Lấy phí đổi thẻ cào tất cả nhà mạng
        """

        embed_main = self.__embed_fee_min_by_telco(cheapest_telco_rate["telco_min"], cheapest_telco_rate["fee_min"])
        embed_sub = self.__embed_fee_min_all_telco(list_min_fees_by_telco)
        return [embed_main, embed_sub]

    def _get_fee_min_by_telco(self, telco_fee_info: dict, telco: str) -> dict:
        """
        Lấy phí đổi thẻ cào theo nhà mạng
        """

        embed_main = self.__embed_amount_min_by_telco(telco_fee_info["amount_min"], telco_fee_info["fee_min"], telco)
        embed_sub = self.__embed_fee_by_telco(telco_fee_info["list_fee"])
        return [embed_main, embed_sub]

    def __embed_fee_min_all_telco(self, list_min_fees_by_telco: dict) -> discord.Embed:
        """
        Tạo embed phí nhỏ nhất đổi thẻ cào tất cả nhà mạng
        """

        config = get_config()
        text_sub = ""
        for telco, fee in list_min_fees_by_telco.items():
            text_sub += f"> ▫️ ` {fee:.1f}% ` {telco} \n"
        embed = discord.Embed(
            description=f"**__Các nhà mạng còn lại:__** \n {text_sub} \n",
            color=discord.Color.from_str("#95afc0"),
        )
        embed.set_image(
            url=config["banner"]["kiem_tra_phi"] or config["banner"]["default"]
        )

        return embed
    
    def __embed_fee_min_by_telco(self, telco_min: str, fee_min: float) -> discord.Embed:
        """
        Tạo embed phí nhỏ nhất
        """

        config = get_config()
        embed = discord.Embed(
            description=f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}] \n\n **__Thông tin chính:__** \n > Nhà mạng phí **thấp nhất** **[{telco_min}]({config['url']['app']})** \n > Chiết khấu **[{fee_min:.1f}%]({config['url']['app']})** \n > vd: *{10000:,.0f} {telco_min} = {int(10000 * (1 - fee_min / 100)):,} vnđ*",
            color=discord.Color.from_str("#ffd154"),
        )
        return embed
    
    def __embed_amount_min_by_telco(self, amount_min: int, fee_min: float, telco: str) -> discord.Embed:
        """
        Tạo embed phí nhỏ nhất của mệnh giá
        """

        config = get_config()
        embed = discord.Embed(
            description=f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}] \n\n **{telco.upper()}** \n\n **__Thông tin chính:__** \n > Mệnh giá **thấp nhất** **[{amount_min:,.0f}]({config['url']['app']})** \n > Chiết khấu **[{fee_min:.1f}%]({config['url']['app']})** \n > vd: *{amount_min:,.0f} VNĐ = {int(amount_min * (1 - fee_min / 100)):,} vnđ*",
            color=discord.Color.from_str("#ffd154"),
        )
        return embed

    def __embed_fee_by_telco(self, list_fees_by_telco: dict) -> discord.Embed:
        """
        Tạo embed phí đổi thẻ cào theo nhà mạng
        """

        config = get_config()
        text_sub = ""
        for amount, fee in list_fees_by_telco.items():
            text_sub += f"> ▫️ ` {int(amount):,} ` -> **{float(fee):.1f}%** \n"
        embed = discord.Embed(
            description=f"**__Các mệnh giá còn lại:__** \n {text_sub} \n",
            color=discord.Color.from_str("#95afc0"),
        )
        embed.set_image(
            url=config["banner"]["kiem_tra_phi"] or config["banner"]["default"]
        )

        return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(CheckFeeExchangeCard(bot))
