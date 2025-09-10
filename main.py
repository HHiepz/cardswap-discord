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

# Tải dự liệu file env
print("\033[92m[INFO] Tải dự liệu file env...\033[0m")
load_dotenv()
print("\033[92m[INFO] Kết thúc tải dự liệu file env\033[0m")

# Tải dự liệu file settings
print("\033[92m[INFO] Tải dự liệu file settings...\033[0m")
yaml = YAML()
with open("configs/settings.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)
print("\033[92m[INFO] Kết thúc tải dự liệu file settings\033[0m")

# Khởi tạo handler logging
print("\033[92m[INFO] Khởi tạo handler logging...\033[0m")
handler = logging.FileHandler(f"logs/{__title__}.log", encoding="utf-8")
stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
print("\033[92m[INFO] Kết thúc khởi tạo handler logging\033[0m")

# Khởi tạo quyền truy cập discord
print("\033[92m[INFO] Khởi tạo quyền truy cập discord...\033[0m")
intents = discord.Intents.default()
print("\033[92m[INFO] Kết thúc khởi tạo quyền truy cập discord\033[0m")

# Khởi tạo cơ sở dữ liệu
print("\033[92m[INFO] Khởi tạo cơ sở dữ liệu...\033[0m")
Base.metadata.create_all(bind=engine)
print("\033[92m[INFO] Kết thúc khởi tạo cơ sở dữ liệu\033[0m")


class CardSwapBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config["prefix"], intents=intents)

    async def setup_hook(self):
        # Nạp các cog
        print("\033[92m[INFO] Bắt đầu nạp các Cog\033[0m")
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"\033[92m[INFO] Nạp cog: {filename[:-3]}\033[0m")
                except Exception as e:
                    print(f"\033[91m[ERROR] Lỗi khi nạp cog: {e}\033[0m")
                    # Dừng bot khi phát hiện lỗi
                    raise SystemExit(1)
        print("\033[92m[INFO] Kết thúc nạp các Cog\033[0m")

        # Nạp các task
        print("\033[92m[INFO] Bắt đầu nạp các task\033[0m")
        for filename in os.listdir("./tasks"):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    await self.load_extension(f"tasks.{filename[:-3]}")
                    print(f"\033[92m[INFO] Nạp task: {filename[:-3]}\033[0m")
                except Exception as e:
                    print(f"\033[91m[ERROR] Lỗi khi nạp task: {e}\033[0m")
                    # Dừng bot khi phát hiện lỗi
                    raise SystemExit(1)
        print("\033[92m[INFO] Kết thúc nạp các task\033[0m")

        # Đồng bộ app commands
        print("\033[92m[INFO] Bắt đầu đồng bộ app commands...\033[0m")
        guild = discord.Object(id=os.getenv("GUILD_ID"))
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("\033[92m[INFO] Kết thúc đồng bộ app commands\033[0m")

        print("\033[92m[INFO] Khởi tạo bot, vui lòng chờ...\033[0m")

    async def on_ready(self):
        print(f"\033[92m[INFO] Bot đã sẵn sàng\033[0m")
        print_bot_info()


# Khởi tạo bot instance
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
    # Kiểm tra các biến môi trường
    print("\033[92m[INFO] Kiểm tra các biến môi trường...\033[0m")
    if not os.path.exists(".env"):
        os.system("cls" if os.name == "nt" else "clear")
        raise Exception("File .env không tồn tại")
    if not os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_TOKEN") == "":
        os.system("cls" if os.name == "nt" else "clear")
        raise Exception("Trường DISCORD_TOKEN không tồn tại hoặc đang rỗng")
    if not os.getenv("GUILD_ID") or os.getenv("GUILD_ID") == "":
        os.system("cls" if os.name == "nt" else "clear")
        raise Exception("Trường GUILD_ID không tồn tại hoặc đang rỗng")
    print("\033[92m[INFO] Kết thúc kiểm tra các biến môi trường\033[0m")

    await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    try:
        # Setup logging
        logging.basicConfig(level=logging.INFO, handlers=[handler, stream_handler])

        asyncio.run(main())
    except KeyboardInterrupt:
        print("\033[92m[INFO] Bot đã tắt theo yêu cầu.\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Lỗi nghiêm trọng khi khởi động bot: {e}\033[0m")
