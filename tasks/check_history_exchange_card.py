import discord
from discord.ext import commands, tasks
from helpers.api import check_card_status
from helpers.console import add_log
from helpers.helper import get_data_file_yml
from helpers.embeds import (
    card_success_embed,
    card_wrong_amount_embed,
    card_failed_embed,
)
from database.session import SessionLocal
from database.models import HistoryExchangeCard, Card2k


class CheckHistoryExchangeCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = get_data_file_yml()

        if self.config.get("card_status_check", {}).get("type") == "api":
            self.delay_time = int(
                self.config.get("card_status_check", {}).get("delay_time", 60)
            )
            if self.delay_time < 30:
                self.delay_time = 30
            self.check_history_exchange_card.change_interval(seconds=self.delay_time)
            self.check_history_exchange_card.start()
            self.session = SessionLocal()

    def cog_unload(self):
        self.check_history_exchange_card.cancel()
        self.session.close()

    @tasks.loop(seconds=60)
    async def check_history_exchange_card(self):
        await self._validated_setup()
        history_exchange_cards = (
            self.session.query(HistoryExchangeCard)
            .filter(HistoryExchangeCard.status == "pending")
            .all()
        )
        if len(history_exchange_cards) == 0:
            return
        for card_pending in history_exchange_cards:
            response = check_card_status(
                card_pending.telco,
                card_pending.value,
                card_pending.code,
                card_pending.serial,
                card_pending.request_id,
            )
            if response is None:
                continue
            elif response["status"] == 99:
                continue
            elif response["status"] == 4:
                continue
            elif response["status"] == 1:
                card_pending.card_value = response["declared_value"]
                card_pending.status = "success"
                self.session.commit()
                await self._update_discord_message(card_pending, "success")
                continue
            elif response["status"] == 2:
                card_pending.card_value = response["declared_value"]
                card_pending.status = "wrong_amount"
                self.session.commit()
                await self._update_discord_message(card_pending, "wrong_amount")
                continue
            else:
                card_pending.status = "failed"
                self.session.commit()
                await self._update_discord_message(
                    card_pending, "failed", response.get("message")
                )
                continue

    @check_history_exchange_card.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    async def _validated_setup(self):
        """Kiểm tra setup"""
        data = self.session.query(Card2k).first()
        if not data or not data.partner_id or not data.partner_key:
            return add_log(
                "[CHECK_HISTORY_EXCHANGE_CARD] Thiếu dữ liệu database.", "ERROR"
            )

        if not self.config["provider"]:
            return add_log(
                "[CHECK_HISTORY_EXCHANGE_CARD] Thiếu nhà cung cấp (provider) trong file settings.yml.",
                "ERROR",
            )

    async def _update_discord_message(
        self, card_history: HistoryExchangeCard, status: str, error_message: str = None
    ):
        """Cập nhật Discord message khi trạng thái thẻ thay đổi"""
        try:
            message_id = int(card_history.message_discord_id)
            message = None
            if card_history.channel_discord_id:
                try:
                    channel_id = int(card_history.channel_discord_id)
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        message = await channel.fetch_message(message_id)
                except (
                    discord.NotFound,
                    discord.Forbidden,
                    discord.HTTPException,
                    ValueError,
                ) as e:
                    add_log(
                        f"[CHECK_HISTORY_EXCHANGE_CARD] Không thể tìm message trong channel {card_history.channel_discord_id}: {str(e)}",
                        "ERROR",
                    )

            if not message:
                for guild in self.bot.guilds:
                    for channel in guild.text_channels:
                        try:
                            message = await channel.fetch_message(message_id)
                            if message:
                                break
                        except (
                            discord.NotFound,
                            discord.Forbidden,
                            discord.HTTPException,
                        ):
                            continue
                    if message:
                        break

            if not message:
                add_log(
                    f"[CHECK_HISTORY_EXCHANGE_CARD] Không tìm thấy Discord message với ID: {message_id}",
                    "ERROR",
                )
                return

            new_embed = None
            if status == "success":
                new_embed = card_success_embed(
                    card_history.telco,
                    card_history.value,
                    card_history.code,
                    card_history.serial,
                    card_history.transaction_id,
                    card_history.card_value,
                )
            elif status == "wrong_amount":
                new_embed = card_wrong_amount_embed(
                    card_history.telco,
                    card_history.value,
                    card_history.code,
                    card_history.serial,
                    card_history.transaction_id,
                    card_history.card_value,
                )
            elif status == "failed":
                new_embed = card_failed_embed(
                    card_history.telco,
                    card_history.value,
                    card_history.code,
                    card_history.serial,
                    card_history.transaction_id,
                    error_message,
                )

            if new_embed:
                await message.edit(embed=new_embed)

        except Exception as e:
            add_log(
                f"[CHECK_HISTORY_EXCHANGE_CARD] Lỗi khi cập nhật Discord message cho giao dịch {card_history.transaction_id}: {str(e)}",
                "ERROR",
            )


async def setup(bot):
    await bot.add_cog(CheckHistoryExchangeCard(bot))
