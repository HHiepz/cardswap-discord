import discord
from discord import app_commands
from discord.ext import commands
from database.session import SessionLocal
from database.models import Card2k
from helpers.embeds import show_setup_bot_embed, error_embed
from helpers.console import add_log
from ruamel.yaml import YAML

yaml = YAML()
with open("configs/settings.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class ShowSetupBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="show-setup", description="Hiển thị cài đặt bot (Chỉ dành cho Admin)"
    )
    @app_commands.default_permissions(administrator=True)
    async def show_setup(self, interaction: discord.Interaction):
        # Lưu thông tin vào database với try-except để xử lý lỗi
        session = SessionLocal()
        try:
            # Lấy dữ liệu từ bảng card2k
            data = session.query(Card2k).first()

            # Kiểm tra dữ liệu
            if not data:
                await interaction.response.send_message(
                    embed=error_embed("Chưa có dữ liệu cài đặt. Vui lòng chạy lệnh `/setup-bot` trước."),
                    ephemeral=True
                )
                add_log("Người dùng cố gắng xem cài đặt nhưng database rỗng.", "WARNING")
                return 

            if not config["provider"]:
                await interaction.response.send_message(
                    embed=error_embed("Không được bỏ trống nhà cung cấp (provider) trong file settings.yml."),
                    ephemeral=True
                )
                add_log("Người dùng cố gắng xem cài đặt nhưng nhà cung cấp (provider) trong file settings.yml bị rỗng.", "WARNING")
                return 

            # Nếu có dữ liệu, tiếp tục xử lý
            partner_id = data.partner_id
            partner_key = data.partner_key
            provider = config["provider"]

        except Exception as e:
            session.rollback()
            await interaction.response.send_message(
                embed=error_embed(f"Đã xảy ra lỗi khi hiển thị cài đặt bot: {e}"),
                ephemeral=True,
            )
            add_log(f"Lỗi khi hiển thị cài đặt bot: {e}", "ERROR")
            return
        finally:
            session.close()

        # Xuất thông báo
        await interaction.response.send_message(
            embed=show_setup_bot_embed(partner_id, partner_key, provider),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ShowSetupBot(bot))
