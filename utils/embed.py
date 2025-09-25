import discord
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from constants import get_footer_text as get_footer_text_constant


class EmbedColor(Enum):
    """Màu sắc embed"""

    SUCCESS = 0x2ECC71  # Green
    ERROR = 0xE74C3C  # Red
    WARNING = 0xF39C12  # Orange
    INFO = 0x3498DB  # Blue
    DEBUG = 0x9B59B6  # Purple
    PRIMARY = 0xFFD154  # Gold/Yellow
    SECONDARY = 0x95AFC0  # Light Blue Gray
    PROCESSING = 0xF1C40F  # Yellow


def _get_footer_text(custom_text: Optional[str] = None) -> str:
    """
    Lấy thông tin footer
    """
    if custom_text:
        return custom_text
    return get_footer_text_constant()


def _add_footer(
    embed: discord.Embed, custom_text: Optional[str] = None
) -> discord.Embed:
    """
    Thêm footer vào embed
    """
    embed.set_footer(text=_get_footer_text(custom_text))
    return embed


def create_embed(
    title: str, description: str, color: EmbedColor, footer: Optional[str] = None
) -> discord.Embed:
    """
    Tạo embed
    """
    content = discord.Embed(
        title=title,
        description=description,
        color=color.value,
    )
    content = _add_footer(content, footer)
    return content


def error_embed(description: str) -> discord.Embed:
    """
    Tạo embed lỗi
    """

    content = discord.Embed(
        title="Lỗi",
        description=description,
        color=EmbedColor.ERROR.value,
    )
    embed = _add_footer(content)
    return embed


def success_embed(description: str) -> discord.Embed:
    """
    Tạo embed thành công
    """

    content = discord.Embed(
        title="Thành công",
        description=description,
        color=EmbedColor.SUCCESS.value,
    )
    embed = _add_footer(content)
    return embed
