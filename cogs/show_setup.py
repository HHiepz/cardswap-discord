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

    @app_commands.command(name="show-setup", description="Hiển thị cài đặt bot")
    @app_commands.default_permissions(administrator=True)
    async def show_setup(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            data = session.query(Card2k).first()
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
            partner_key = data.partner_key
            provider = config["provider"]
            await interaction.response.send_message(
                embed=show_setup_bot_embed(partner_id, partner_key, provider),
                ephemeral=True,
            )
        except Exception as e:
            session.rollback()
            await interaction.response.send_message(
                embed=error_embed(f"Đã xảy ra lỗi khi hiển thị cài đặt bot: {e}"),
                ephemeral=True,
            )
            add_log(f"[COG: SHOW_SETUP_BOT] Lỗi khi hiển thị cài đặt bot: {e}", "ERROR")
            return
        finally:
            session.close()


async def setup(bot: commands.Bot):
    await bot.add_cog(ShowSetupBot(bot))
