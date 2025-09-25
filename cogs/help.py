import discord

from discord import app_commands
from discord.ext import commands

from utils.embed import error_embed, create_embed, EmbedColor
from helpers.console import logger


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Hướng dẫn sử dụng")
    async def help_command(self, interaction: discord.Interaction):
        """
        Xem hướng dẫn sử dụng
        """

        try:
            # Danh sách lệnh
            list_commands = [
                {
                    "title": "Lệnh cơ bản",
                    "list": [
                        {"name": "help", "description": "Xem hướng dẫn sử dụng bot"},
                        {"name": "ping", "description": "Kiểm tra ping của bot"},
                    ],
                },
                {
                    "title": "Thẻ cào",
                    "list": [
                        {"name": "kiem-tra-phi", "description": "Kiểm tra phí đổi thẻ cào"},
                        {"name": "nap-the", "description": "Nạp thẻ cào"},
                    ],
                },
                {
                    "title": "Quản trị viên",
                    "list": [
                        {"name": "reload", "description": "Tải lại tất cả các cog"},
                        {"name": "show-setup", "description": "Hiển thị cài đặt bot"},
                        {"name": "setup-bot", "description": "Cài đặt bot"},
                    ],
                },
            ]

            # Format danh sách lệnh thành string
            content = ""
            for item in list_commands:
                content += f"**{item['title']}**\n"
                for item_list in item["list"]:
                    content += f" - `{item_list['name']}`: {item_list['description']}\n"
                content += "\n"
        
            # Tạo embed
            embed = create_embed(title="Hướng dẫn sử dụng bot", description=content, color=EmbedColor.INFO)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"[COG: HELP] Lỗi: {e}")
            message_error = error_embed(f"Lỗi khi sử dụng lệnh, vui lòng thử lại sau.")
            await interaction.response.send_message(embed=message_error, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
