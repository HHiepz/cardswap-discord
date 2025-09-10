import discord
from discord import app_commands
from discord.ext import commands
from database.session import SessionLocal
from database.models import Card2k, HistoryExchangeCard
from helpers.embeds import (
    error_embed,
    waiting_for_processing_embed,
    confirmation_embed,
    success_embed,
)
from helpers.console import add_log
from helpers.helper import get_data_file_yml
from helpers.api import exchange_card

config = get_data_file_yml()


class ConfirmationView(discord.ui.View):
    def __init__(
        self,
        cog,
        telco: str,
        amount: int,
        code: str,
        serial: str,
        original_interaction: discord.Interaction,
    ):
        super().__init__(timeout=300)
        self.cog = cog
        self.telco = telco
        self.amount = amount
        self.code = code
        self.serial = serial
        self.original_interaction = original_interaction

    @discord.ui.button(label="✅ Xác nhận", style=discord.ButtonStyle.green)
    async def confirm_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.original_interaction.user.id:
            await interaction.response.send_message(
                "❌ Chỉ người tạo lệnh mới có thể xác nhận!", ephemeral=True
            )
            return

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            embed=confirmation_embed(self.telco, self.amount, self.code, self.serial),
            view=self,
        )
        await self.cog.process_card_exchange(
            interaction, self.telco, self.amount, self.code, self.serial
        )

    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.red)
    async def cancel_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.original_interaction.user.id:
            await interaction.response.send_message(
                "❌ Chỉ người tạo lệnh mới có thể hủy!", ephemeral=True
            )
            return

        for item in self.children:
            item.disabled = True

        cancel_embed = success_embed("✅ Đã hủy yêu cầu nạp thẻ cào.")
        await interaction.response.edit_message(embed=cancel_embed, view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class NapThe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.session = SessionLocal()
        self.bot = bot

    @app_commands.command(name="nap-the", description="Nạp thẻ cào")
    @app_commands.choices(
        telco=[
            *[
                app_commands.Choice(name=telco_key.capitalize(), value=telco_key)
                for telco_key, enabled in config.get("card_types", {}).items()
                if enabled is True
            ],
        ],
        amount=[
            *[
                app_commands.Choice(name=f"{amount:,} VND", value=amount)
                for amount in [
                    5_000,
                    10_000,
                    20_000,
                    30_000,
                    50_000,
                    100_000,
                    200_000,
                    300_000,
                    500_000,
                    1_000_000,
                ]
            ]
        ],
    )
    async def nap_the(
        self,
        interaction: discord.Interaction,
        telco: str,
        amount: int,
        code: str,
        serial: str,
    ):
        try:
            validated_data = await self._validated_data(telco, amount)
            if validated_data is not None:
                await interaction.response.send_message(
                    embed=validated_data, ephemeral=True
                )
                return
            validated_setup = await self._validated_setup()
            if validated_setup is not None:
                await interaction.response.send_message(
                    embed=validated_setup, ephemeral=True
                )
                return

            view = ConfirmationView(self, telco, amount, code, serial, interaction)
            embed = confirmation_embed(telco, amount, code, serial)

            await interaction.response.send_message(
                embed=embed, view=view, ephemeral=True
            )

        except Exception as e:
            add_log(
                f"[COG: NAP_THE] Lỗi không xác định trong lệnh: 'nap-the'. Chi tiết: {e}",
                "ERROR",
            )

    async def process_card_exchange(
        self,
        interaction: discord.Interaction,
        telco: str,
        amount: int,
        code: str,
        serial: str,
    ):
        session = SessionLocal()
        try:
            response = exchange_card(telco, amount, code, serial)
            if response is None:
                await interaction.followup.send(
                    embed=error_embed("API lỗi, vui lòng liên hệ admin."),
                    ephemeral=True,
                )
                return

            if (
                response["status"] != 99
                and response["status"] != 1
                and response["status"] != 2
            ):
                await interaction.followup.send(
                    embed=error_embed(f"{response['message']} (mã lỗi: {response['status']})"),
                    ephemeral=True,
                )
                return

            followup_message = await interaction.followup.send(
                embed=waiting_for_processing_embed(
                    telco, amount, code, serial, response["trans_id"]
                )
            )

            history_exchange_card = HistoryExchangeCard(
                telco=telco,
                value=amount,
                code=code,
                serial=serial,
                user_discord_id=str(interaction.user.id),
                message_discord_id=str(followup_message.id),
                channel_discord_id=str(interaction.channel.id),
                server=config.get("provider", ""),
                request_id=response["request_id"],
                transaction_id=response["trans_id"],
                status="pending",
            )
            session.add(history_exchange_card)
            session.commit()
        except Exception as e:
            add_log(f"[COG: NAP_THE] Lỗi không xác định khi xử lý API: {e}", "ERROR")
            session.rollback()
            await interaction.followup.send(
                embed=error_embed(f"Có lỗi xảy ra khi xử lý: {str(e)}"), ephemeral=True
            )
        finally:
            session.close()

    async def _validated_data(self, telco: str, amount: int):
        if not config.get("card_types", {}).get(telco, False):
            return error_embed(f"❌ Nhà mạng `{telco}` hiện không được hỗ trợ!")

        telco_amounts = config.get("card_amounts", {}).get(telco, {})
        if amount not in telco_amounts or not telco_amounts[amount]:
            return error_embed(
                f"❌ Mệnh giá `{amount:,} VND` không được hỗ trợ cho nhà mạng `{telco.capitalize()}`!"
            )

        return None

    async def _validated_setup(self):
        data = self.session.query(Card2k).first()
        if not data or not data.partner_id or not data.partner_key:
            return error_embed(
                "Chưa có dữ liệu cài đặt. Vui lòng chạy lệnh `/setup-bot` trước."
            )

        if not config["provider"]:
            return error_embed(
                "Không được bỏ trống nhà cung cấp (provider) trong file settings.yml."
            )

        return None


async def setup(bot: commands.Bot):
    await bot.add_cog(NapThe(bot))
