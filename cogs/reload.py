# cogs/reload.py
import discord
import os
from discord import app_commands
from discord.ext import commands
from helpers.embeds import success_embed, error_embed
import logging


class Reload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reload", description="Tải lại tất cả các cog")
    @app_commands.default_permissions(administrator=True)
    async def reload(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        reloaded_cogs = []
        failed_cogs = []

        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                extension_name = f"cogs.{filename[:-3]}"
                try:
                    await self.bot.reload_extension(extension_name)
                    reloaded_cogs.append(f"✅ {filename}")
                except commands.ExtensionNotLoaded:
                    try:
                        await self.bot.load_extension(extension_name)
                        reloaded_cogs.append(f"🆕 {filename} (mới)")
                    except Exception as e:
                        failed_cogs.append(f"❌ {filename}: {e}")
                except Exception as e:
                    failed_cogs.append(f"❌ {filename}: {e}")

        description = ""
        if reloaded_cogs:
            description += "**Đã tải lại thành công:**\n" + "\n".join(reloaded_cogs)
        if failed_cogs:
            description += "\n\n**Tải lại thất bại:**\n" + "\n".join(failed_cogs)

        embed = success_embed(description)
        await interaction.followup.send(embed=embed, ephemeral=True)
        logging.info(f"Cogs reloaded by {interaction.user}.")

    @reload.error
    async def on_reload_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.NotOwner):
            await interaction.response.send_message(
                embed=error_embed("Bạn không phải là chủ bot để dùng lệnh này."),
                ephemeral=True,
            )
        else:
            raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(Reload(bot))
