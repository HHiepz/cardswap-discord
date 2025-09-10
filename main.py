import asyncio
import discord
import logging
import os
from database.session import SessionLocal, engine
from database.models import Card2k, HistoryExchangeCard
from database.base import Base
from dotenv import load_dotenv
from ruamel.yaml import YAML
from discord.ext import commands
from __init__ import __title__
from helpers.console import print_bot_info, add_log
from helpers.embeds import error_embed
from discord import app_commands

load_dotenv()

yaml = YAML()
with open("configs/settings.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

intents = discord.Intents.default()

Base.metadata.create_all(bind=engine)


class CardSwapBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config["prefix"], intents=intents)

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    print(f"\033[91m[ERROR] Lỗi khi nạp cog: {e}\033[0m")
                    raise SystemExit(1)

        for filename in os.listdir("./tasks"):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    await self.load_extension(f"tasks.{filename[:-3]}")
                except Exception as e:
                    print(f"\033[91m[ERROR] Lỗi khi nạp task: {e}\033[0m")
                    raise SystemExit(1)

        guild = discord.Object(id=os.getenv("GUILD_ID"))
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_ready(self):
        print_bot_info()


bot = CardSwapBot()


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    response_embed = None
    if isinstance(error, app_commands.CheckFailure):
        response_embed = error_embed("Bạn không có quyền sử dụng lệnh này.")
        add_log(
            f"Người dùng: {interaction.user} (ID: {interaction.user.id}) đã sử dụng lệnh: '{interaction.command.name}' thất bại vì không có quyền.",
            "WARNING",
        )
    elif isinstance(error, app_commands.CommandOnCooldown):
        response_embed = error_embed(
            f"Lệnh này đang trong thời gian chờ. Vui lòng thử lại sau {error.retry_after:.2f} giây."
        )
    else:
        response_embed = error_embed("Đã có lỗi xảy ra. Vui lòng liên hệ admin.")
        add_log(
            f"Lỗi không xác định trong lệnh: '{interaction.command.name}'.",
            "ERROR",
        )

    if interaction.response.is_done():
        await interaction.followup.send(embed=response_embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=response_embed, ephemeral=True)


async def main():
    if not os.path.exists(".env"):
        os.system("cls" if os.name == "nt" else "clear")
        raise Exception("File .env không tồn tại")
    if not os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_TOKEN") == "":
        os.system("cls" if os.name == "nt" else "clear")
        raise Exception("Trường DISCORD_TOKEN không tồn tại hoặc đang rỗng")
    if not os.getenv("GUILD_ID") or os.getenv("GUILD_ID") == "":
        os.system("cls" if os.name == "nt" else "clear")
        raise Exception("Trường GUILD_ID không tồn tại hoặc đang rỗng")

    await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)

        asyncio.run(main())
    except KeyboardInterrupt:
        print("\033[92m[INFO] Bot đã tắt theo yêu cầu.\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Lỗi nghiêm trọng khi khởi động bot: {e}\033[0m")
