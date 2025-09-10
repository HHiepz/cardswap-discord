import discord
from discord import app_commands
from discord.ext import commands
from database.session import SessionLocal
from database.models import Card2k
from helpers.embeds import error_embed
from helpers.console import add_log
from helpers.helper import get_data_file_yml
from helpers.api import get_fee_telco_api_min, get_all_fee_min_telco_api, get_fee_telco_api, get_fee_api
from helpers.embeds import list_lowest_fee_telco_embed, lowest_fee_telco_embed

config = get_data_file_yml()


class KiemTraPhi(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kiem-tra-phi", description="Kiểm tra phí đổi thẻ cào")
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
        # Lưu thông tin vào database với try-except để xử lý lỗi
        session = SessionLocal()
        try:
            # Lấy dữ liệu từ bảng card2k
            data = session.query(Card2k.partner_id).first()

            # Kiểm tra dữ liệu
            if not data:
                await interaction.response.send_message(
                    embed=error_embed(
                        "Chưa có dữ liệu cài đặt. Vui lòng chạy lệnh `/setup-bot` trước."
                    ),
                    ephemeral=True,
                )
                add_log(
                    "Người dùng cố gắng kiểm tra phí đổi thẻ cào nhưng database rỗng.",
                    "WARNING",
                )
                return

            if not config["provider"]:
                await interaction.response.send_message(
                    embed=error_embed(
                        "Không được bỏ trống nhà cung cấp (provider) trong file settings.yml."
                    ),
                    ephemeral=True,
                )
                add_log(
                    "Người dùng cố gắng kiểm tra phí đổi thẻ cào nhưng nhà cung cấp (provider) trong file settings.yml bị rỗng.",
                    "WARNING",
                )
                return

            # Nếu có dữ liệu, tiếp tục xử lý
            partner_id = data.partner_id
            provider = config["provider"]

            add_log(
                f"Kiểm tra phí đổi thẻ cào: {partner_id} - {provider}",
                "INFO",
            )
        except Exception as e:
            session.rollback()
            await interaction.response.send_message(
                embed=error_embed(f"Đã xảy ra lỗi khi kiểm tra phí đổi thẻ cào: {e}"),
                ephemeral=True,
            )
            add_log(f"Lỗi khi kiểm tra phí đổi thẻ cào: {e}", "ERROR")
            return
        finally:
            session.close()

        # Kiểm tra dữ liệu API
        check_fee_api = get_fee_api()

        # Nếu API lỗi
        if check_fee_api is None:
            await interaction.response.send_message(
                embed=error_embed("API lỗi, vui lòng liên hệ admin."),
                ephemeral=True,
            )
            return

        # Nếu API hoạt động và có status
        if "status" in check_fee_api and check_fee_api["status"] == 100:
            await interaction.response.send_message(
                embed=error_embed(check_fee_api.get("message")),
                ephemeral=True,
            )
            return

        # Xuất thông tin
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
            # Chỉ cho phép nhà mạng có giá trị true trong settings.yml
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
            
        add_log(
            f"Xuất thông tin kiểm tra phí đổi thẻ cào hoàn tất: {partner_id} - {provider}",
            "INFO",
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(KiemTraPhi(bot))
