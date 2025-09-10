import discord
from discord import app_commands
from discord.ext import commands
from database.session import SessionLocal
from database.models import Card2k
from helpers.embeds import error_embed
from helpers.console import add_log
from helpers.helper import get_data_file_yml
from helpers.api import (
    get_fee_telco_api_min,
    get_all_fee_min_telco_api,
    get_fee_telco_api,
    get_fee_api,
)
from helpers.embeds import (list_lowest_fee_telco_embed, lowest_fee_telco_embed)

config = get_data_file_yml()


class KiemTraPhi(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kiem-tra-phi", description="Kiểm tra phí nạp thẻ")
    @app_commands.choices(
        telco=[
            app_commands.Choice(name="Tất cả nhà mạng", value="all"),
            *[
                app_commands.Choice(name=telco_key.capitalize(), value=telco_key)
                for telco_key, enabled in config.get("card_types", {}).items()
                if enabled is True
            ],
        ]
    )
    async def kiem_tra_phi(self, interaction: discord.Interaction, telco: str = "all"):
        session = SessionLocal()
        try:
            data = session.query(Card2k.partner_id).first()
            if not data:
                await interaction.response.send_message(
                    embed=error_embed(
                        "Chưa có dữ liệu cài đặt. Vui lòng chạy lệnh `/setup-bot` trước."
                    ),
                    ephemeral=True,
                )
                return

            if not config["provider"]:
                await interaction.response.send_message(
                    embed=error_embed(
                        "Không được bỏ trống nhà cung cấp (provider) trong file settings.yml."
                    ),
                    ephemeral=True,
                )
                return

            partner_id = data.partner_id
            provider = config["provider"]
        except Exception as e:
            session.rollback()
            await interaction.response.send_message(
                embed=error_embed(f"Đã xảy ra lỗi khi kiểm tra phí nạp thẻ: {e}"),
                ephemeral=True,
            )
            add_log(f"[COG: KIEM_TRA_PHI] Lỗi khi kiểm tra phí nạp thẻ: {e}", "ERROR")
            return
        finally:
            session.close()

        check_fee_api = get_fee_api()
        if check_fee_api is None:
            await interaction.response.send_message(
                embed=error_embed("API lỗi, vui lòng liên hệ admin."),
                ephemeral=True,
            )
            return
        if "status" in check_fee_api and check_fee_api["status"] == 100:
            await interaction.response.send_message(
                embed=error_embed(check_fee_api.get("message")),
                ephemeral=True,
            )
            return

        if telco == "all":
            data_fee_min = get_fee_telco_api_min()
            telco_min = data_fee_min["telco_min"]
            fee_min = data_fee_min["fee_min"]
            list_telco_fee_min = get_all_fee_min_telco_api()
            await interaction.response.send_message(
                embeds=list_lowest_fee_telco_embed(telco_min, fee_min, list_telco_fee_min),
                ephemeral=True,
            )
        else:
            if not (telco in config["card_types"] and config["card_types"][telco] is True):
                await interaction.response.send_message(
                    embed=error_embed("Nhà mạng không hoạt động."),
                    ephemeral=True,
                )
                return

            data_fee = get_fee_telco_api(telco)
            fee_min = data_fee["fee_min"]
            amount_min = data_fee["amount_min"]
            list_fee = data_fee["list_fee"]
            await interaction.response.send_message(
                embeds=lowest_fee_telco_embed(telco, fee_min, amount_min, list_fee),
                ephemeral=True,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(KiemTraPhi(bot))
