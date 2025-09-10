import discord
import datetime
from __init__ import (
    __title__,
    __author__,
    __version__,
    __date_created__,
    __last_updated__,
    __support_channel__,
)
from ruamel.yaml import YAML
from helpers.helper import get_data_file_yml


def _footer(embed: discord.Embed):
    embed.set_footer(text=f"© Author: {__support_channel__}")


# Ping embed (kiểm tra độ trễ)
def ping_embed(ping: float) -> discord.Embed:
    embed = discord.Embed(
        title="Xem độ trễ của bot",
        description=f" - Độ trễ của bot là: **{ping:.2f}ms**",
        color=discord.Color.green(),
    )
    _footer(embed)
    return embed


# Setup bot embed (cài đặt bot)
def setup_bot_embed(partner_id: str, partner_key: str) -> discord.Embed:
    embed = discord.Embed(
        title="Cài đặt bot",
        description=f"Thông tin đã được lưu: \n - Partner_id: **{partner_id}**\n - Partner_key: **||{partner_key}||**",
        color=discord.Color.blue(),
    )
    _footer(embed)
    return embed


# Error embed (lỗi)
def error_embed(description: str) -> discord.Embed:
    embed = discord.Embed(
        title="Lỗi",
        description=description,
        color=discord.Color.red(),
    )
    _footer(embed)
    return embed


# Success embed (thành công)
def success_embed(description: str) -> discord.Embed:
    embed = discord.Embed(
        title="Thành công",
        description=description,
        color=discord.Color.green(),
    )
    _footer(embed)
    return embed


# Show setup bot embed (hiển thị cài đặt bot)
def show_setup_bot_embed(
    partner_id: str, partner_key: str, provider: str
) -> discord.Embed:
    embed = discord.Embed(
        title="Cài đặt bot",
        description=f"Thông tin đã được lưu: \n - Partner_id: **{partner_id}**\n - Partner_key: **||{partner_key}||** \n - Nhà cung cấp: **{provider}**",
        color=discord.Color.blue(),
    )
    _footer(embed)
    return embed


# Debug embed (debug)
def debug_embed(description: str) -> discord.Embed:
    embed = discord.Embed(
        title="Debug",
        description=description,
        color=discord.Color.red(),
    )
    _footer(embed)
    return embed


# Danh sách phí thấp nhất (tất cả nhà mạng)
def list_lowest_fee_telco_embed(
    telco_min: str, fee_min: float, list_telco_fee_min: list
) -> list[discord.Embed]:
    config = get_data_file_yml()

    embed_main = discord.Embed(
        description=f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}] \n\n **__Thông tin chính:__** \n > Nhà mạng phí **thấp nhất** **[{telco_min}]({config['url']['app']})** \n > Chiết khấu **[{fee_min:,}%]({config['url']['app']})** \n > vd: *{10000:,.0f} {telco_min} = {int(10000 * (1 - fee_min / 100)):,} vnđ*",
        color=discord.Color.from_str("#ffd154"),
    )

    text_sub = ""
    for telco, fee in list_telco_fee_min.items():
        text_sub += f"> ▫️ ` {fee:.1f}% ` {telco} \n"

    embed_sub = discord.Embed(
        description=f"**__Các nhà mạng còn lại:__** \n {text_sub} \n",
        color=discord.Color.from_str("#95afc0"),
    )

    embed_sub.set_image(
        url=config["banner"]["kiem_tra_phi"] or config["banner"]["default"]
    )

    _footer(embed_main)
    _footer(embed_sub)
    return [embed_main, embed_sub]


# Danh sách phí thấp nhất (tất cả nhà mạng)
def lowest_fee_telco_embed(
    telco: str, fee_min: str, amount_min: float, list_fee: list
) -> list[discord.Embed]:
    config = get_data_file_yml()

    embed_main = discord.Embed(
        description=f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}] \n\n **{telco.upper()}** \n\n **__Thông tin chính:__** \n > Mệnh giá **thấp nhất** **[{amount_min:,.0f}]({config['url']['app']})** \n > Chiết khấu **[{fee_min:,}%]({config['url']['app']})** \n > vd: *{amount_min:,.0f} VNĐ = {int(amount_min * (1 - fee_min / 100)):,} vnđ*",
        color=discord.Color.from_str("#ffd154"),
    )

    text_sub = ""
    for amount, fee in list_fee.items():
        text_sub += f"> ▫️ ` {int(amount):,} ` -> **{float(fee):.1f}%** \n"

    embed_sub = discord.Embed(
        description=f"**__Các mệnh giá còn lại:__** \n {text_sub} \n",
        color=discord.Color.from_str("#95afc0"),
    )

    embed_sub.set_image(
        url=config["banner"]["kiem_tra_phi"] or config["banner"]["default"]
    )

    _footer(embed_main)
    _footer(embed_sub)
    return [embed_main, embed_sub]


# Hướng dẫn sử dụng bot
def help_embed() -> discord.Embed:
    data = [
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

    text = ""
    for item in data:
        text += f"**{item['title']}**\n"
        for item_list in item["list"]:
            text += f" - `{item_list['name']}`: {item_list['description']}\n"
        text += "\n"

    embed = discord.Embed(
        title="Hướng dẫn sử dụng bot",
        description=text,
        color=discord.Color.blue(),
    )
    _footer(embed)
    return embed


# Nạp thẻ cào embed - XÁC NHẬN (xác nhận thông tin trước khi nạp)
def confirmation_embed(telco: str, amount: int, code: str, serial: str) -> discord.Embed:
    embed = discord.Embed(
        title="🔍 Xác nhận thông tin thẻ cào",
        description="Vui lòng kiểm tra kỹ thông tin trước khi xác nhận:",
        color=discord.Color.blue(),
    )

    embed.add_field(name="Nhà mạng", value=telco.capitalize(), inline=True)
    embed.add_field(name="Mệnh giá", value=f"{amount:,} VND", inline=True)
    embed.add_field(name="⠀", value="⠀", inline=True)  # Spacer
    embed.add_field(name="Mã thẻ", value=f"||{code}||", inline=True)
    embed.add_field(name="Serial", value=f"||{serial}||", inline=True)
    embed.add_field(name="⠀", value="⠀", inline=True)  # Spacer

    embed.add_field(
        name="⚠️ Lưu ý", 
        value="• Vui lòng kiểm tra kỹ thông tin trước khi xác nhận\n• Nhấn **Xác nhận** để tiếp tục hoặc **Hủy** để dừng lại", 
        inline=False
    )

    _footer(embed)
    return embed


# Nạp thẻ cào embed - CHỜ XỬ LÝ (chờ xử lý nạp thẻ cào)
def waiting_for_processing_embed(telco: str, amount: int, code: str, serial: str, order_id: str) -> discord.Embed:
    embed = discord.Embed(
        title="⏳ Thẻ cào đang được xử lý",
        description="Hệ thống đã tiếp nhận yêu cầu của bạn và đang xử lý...",
        color=discord.Color.yellow(),
    )

    embed.add_field(name="Nhà mạng", value=telco, inline=True)
    embed.add_field(name="Mệnh giá", value=f"{amount:,} VND", inline=True)
    embed.add_field(name="Mã giao dịch", value=f"`{order_id}`", inline=True)
    embed.add_field(name="Mã thẻ", value=f"||{code}||", inline=True)
    embed.add_field(name="Serial", value=f"||{serial}||", inline=True)

    _footer(embed)
    return embed


# Nạp thẻ cào embed - THÀNH CÔNG (thẻ đúng mệnh giá)
def card_success_embed(telco: str, amount: int, code: str, serial: str, order_id: str, card_value: int) -> discord.Embed:
    embed = discord.Embed(
        title="✅ Thẻ cào đã được xử lý thành công",
        description="Thẻ cào của bạn đã được xử lý thành công với đúng mệnh giá!",
        color=discord.Color.green(),
    )

    embed.add_field(name="Nhà mạng", value=telco, inline=True)
    embed.add_field(name="Mệnh giá", value=f"{amount:,} VND", inline=True)
    embed.add_field(name="Mã giao dịch", value=f"`{order_id}`", inline=True)
    embed.add_field(name="Mã thẻ", value=f"||{code}||", inline=True)
    embed.add_field(name="Serial", value=f"||{serial}||", inline=True)
    embed.add_field(name="Mệnh giá thực tế", value=f"**{card_value:,} VND**", inline=True)

    embed.add_field(
        name="🎉 Chúc mừng", 
        value="Thẻ cào đã được xử lý thành công với đúng mệnh giá!", 
        inline=False
    )

    _footer(embed)
    return embed


# Nạp thẻ cào embed - SAI MỆNH GIÁ (trừ 50% giá trị)
def card_wrong_amount_embed(telco: str, amount: int, code: str, serial: str, order_id: str, card_value: int) -> discord.Embed:
    embed = discord.Embed(
        title="⚠️ Thẻ cào sai mệnh giá",
        description="Thẻ cào đã được xử lý nhưng sai mệnh giá, giá trị sẽ bị trừ 50%.",
        color=discord.Color.orange(),
    )

    embed.add_field(name="Nhà mạng", value=telco, inline=True)
    embed.add_field(name="Mệnh giá khai báo", value=f"{amount:,} VND", inline=True)
    embed.add_field(name="Mã giao dịch", value=f"`{order_id}`", inline=True)
    embed.add_field(name="Mã thẻ", value=f"||{code}||", inline=True)
    embed.add_field(name="Serial", value=f"||{serial}||", inline=True)
    embed.add_field(name="Mệnh giá thực tế", value=f"{card_value:,} VND", inline=True)

    embed.add_field(
        name="⚠️ Lưu ý", 
        value="Do thẻ sai mệnh giá, giá trị đã bị trừ 50% theo quy định.", 
        inline=False
    )

    _footer(embed)
    return embed


# Nạp thẻ cào embed - THẤT BẠI (thẻ lỗi)
def card_failed_embed(telco: str, amount: int, code: str, serial: str, order_id: str, error_message: str = None) -> discord.Embed:
    embed = discord.Embed(
        title="❌ Thẻ cào xử lý thất bại",
        description="Rất tiếc, thẻ cào của bạn không thể được xử lý.",
        color=discord.Color.red(),
    )

    embed.add_field(name="Nhà mạng", value=telco, inline=True)
    embed.add_field(name="Mệnh giá", value=f"{amount:,} VND", inline=True)
    embed.add_field(name="Mã giao dịch", value=f"`{order_id}`", inline=True)
    embed.add_field(name="Mã thẻ", value=f"||{code}||", inline=True)
    embed.add_field(name="Serial", value=f"||{serial}||", inline=True)
    embed.add_field(name="⠀", value="⠀", inline=True)  # Spacer

    if error_message:
        embed.add_field(
            name="❌ Lý do", 
            value=f"{error_message}", 
            inline=False
        )
    else:
        embed.add_field(
            name="❌ Lý do", 
            value="Thẻ cào không hợp lệ hoặc đã được sử dụng.", 
            inline=False
        )

    _footer(embed)
    return embed