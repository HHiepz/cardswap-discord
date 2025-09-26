import asyncio
import os
import shutil

import discord
from discord.ext import commands

from constants import get_bot_info, print_bot_info_panel_no_color
from database.models import HistoryExchangeCard
from database.base import Base
from database.session import engine
from helpers.console import LogContext, logger
from utils.config import get_config_value
from utils.env import get_env


class CardSwapBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        PREFIX = get_config_value("prefix")
        super().__init__(command_prefix=PREFIX, intents=intents, help_command=None)

    async def on_ready(self):
        logger.success(print_bot_info_panel_no_color(get_bot_info(), "Bot đã sẵn sàng!"))

    async def setup_hook(self):
        with LogContext("Bot Setup"):
            await self._load_extensions()
            await self._sync_commands()

    async def _load_extensions(self):
        extensions = [("./cogs", "cogs"), ("./tasks", "tasks")]

        for dir_name, module_prefix in extensions:
            if not os.path.exists(dir_name):
                logger.error(f"Thư mục {dir_name} không tồn tại")
                continue

            logger.info(f"Tải các extensions từ {dir_name}")
            for filename in os.listdir(dir_name):
                if filename.endswith(".py") and not filename.startswith("__"):
                    try:
                        await self.load_extension(f"{module_prefix}.{filename[:-3]}")
                        logger.info(f"Đã thành công {module_prefix}.{filename[:-3]}")
                    except Exception as e:
                        logger.error(f"Lỗi khi tải {module_prefix}.{filename[:-3]}: {e}")

    async def _sync_commands(self):
        """
        Tải các lệnh slash
        """
        try:
            guild = discord.Object(id=get_env("GUILD_ID"))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        except Exception as e:
            print(f"[ERROR] Lỗi khi sync lệnh slash: {e}")


bot = CardSwapBot()


async def main():
    required_env = ["DISCORD_TOKEN", "GUILD_ID", "PARTNER_ID", "PARTNER_KEY"]
    missing_env = [env for env in required_env if not get_env(env)]

    # Kiểm tra file .env có tồn tại
    if not os.path.exists(".env"):
        shutil.copy(".env.example", ".env")

    # Kiểm tra các biến môi trường có tồn tại
    if missing_env:
        raise ValueError(f"Thiếu các biến môi trường: {', '.join(missing_env)}")

    try:
        async with bot:
            await bot.start(get_env("DISCORD_TOKEN"))
    except discord.LoginFailure:
        raise ValueError("Token Discord không hợp lệ")
    except Exception as e:
        raise


if __name__ == "__main__":
    try:
        Base.metadata.create_all(bind=engine)
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"[INFO] Bot đã dừng theo yêu cầu")
    except Exception as e:
        print(f"[ERROR] Lỗi khi chạy bot: {e}")
