import discord
from discord import app_commands
from discord.ext import commands
from database.session import SessionLocal
from database.models import Card2k
from helpers.embeds import setup_bot_embed, error_embed
from helpers.console import add_log


class SetUpBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="setup-bot", description="Cài đặt bot (Chỉ dành cho Admin)"
    )
    @app_commands.describe(partner_id="ID của đối tác", partner_key="Key của đối tác")
    @app_commands.default_permissions(administrator=True)
    async def setup_bot(
        self, interaction: discord.Interaction, partner_id: str, partner_key: str
    ):
        # Validated
        if len(partner_id) > 255 or len(partner_key) > 255:
            await interaction.response.send_message(
                embed=error_embed("ID và Key không được vượt quá 255 ký tự"),
                ephemeral=True,
            )
            add_log(
                f"ID và Key không được vượt quá 255 ký tự: {partner_id} - {partner_key}",
                "ERROR",
            )
            return

        # Lưu thông tin vào database với try-except để xử lý lỗi
        session = SessionLocal()
        try:
            # Xóa tất cả dữ liệu trong bảng card2k
            session.query(Card2k).delete()
            session.commit()
            # Lưu dữ liệu mới
            session.add(Card2k(partner_id=partner_id, partner_key=partner_key))
            session.commit()
        except Exception as e:
            session.rollback()
            await interaction.response.send_message(
                embed=error_embed(f"Đã xảy ra lỗi khi lưu thông tin: {e}"),
                ephemeral=True,
            )
            add_log(f"Lỗi khi cài đặt bot: {e}", "ERROR")
            return
        finally:
            session.close()

        # Xuất thông báo
        await interaction.response.send_message(
            embed=setup_bot_embed(partner_id, partner_key), ephemeral=True
        )
        add_log(f"Cài đặt bot hoàn tất: {partner_id} ", "INFO")


async def setup(bot: commands.Bot):
    await bot.add_cog(SetUpBot(bot))
