"""
Thông tin bot
"""

# Thông tin cơ bản
BOT_NAME = "cardswap discord"
BOT_VERSION = "1.0.1"
BOT_AUTHOR = "HHiepz"
BOT_AUTHOR_URL = "http://hhiepz.github.io/"

# Thời gian
DATE_CREATED = "05/09/2025"
LAST_UPDATED = "26/10/2025"

# Thông tin hỗ trợ
SUPPORT_CHANNEL = "https://2k9xteam.shop/discord"
DOWNLOAD_BOT_URL = "https://github.com/HHiepz/cardswap-discord/releases"

# Build info
BUILD_INFO = {
    "version": BOT_VERSION,
    "author": BOT_AUTHOR,
}


def get_bot_info() -> dict:
    """
    Lấy thông tin bot
    """
    return {
        "name": BOT_NAME,
        "version": BOT_VERSION,
        "author": BOT_AUTHOR,
        "last_updated": LAST_UPDATED,
        "support_channel": SUPPORT_CHANNEL,
        "download_bot_url": DOWNLOAD_BOT_URL,
    }


def get_version_string() -> str:
    """
    Lấy thông tin version
    """
    return f"{BOT_NAME} v{BOT_VERSION}"


def get_footer_text() -> str:
    """
    Lấy thông tin footer
    """
    return f"{BOT_NAME} v{BOT_VERSION} • Created by {BOT_AUTHOR}"


def print_bot_info_panel_no_color(bot_info: dict, status: str):
    header = f"{bot_info.get('name', 'Bot')} v{bot_info.get('version', '0.0.0')}"
    
    lines = {
        "Author": bot_info.get('author', 'N/A'),
        "Version": bot_info.get('version', 'N/A'),
        "Support": bot_info.get('support_channel', 'N/A'),
        "Download": bot_info.get('download_bot_url', 'N/A'),
        "Last Updated": bot_info.get('last_updated', 'N/A'),
    }

    # Tính toán độ rộng của panel
    max_key_len = max(len(k) for k in lines.keys())
    valid_values = [v for v in lines.values() if v is not None]
    max_val_len = max(len(str(v)) for v in valid_values) if valid_values else 10
    
    panel_width = max(len(header), len(status), max_key_len + max_val_len + 5) + 4

    # --- Bắt đầu vẽ panel ---
    # Dòng đầu
    print(f"    ╔{'═' * (panel_width - 2)}╗")
    
    # Header
    padding = " " * ((panel_width - len(header) - 2) // 2)
    print(f"    ║{padding}{header}{padding}{' ' if len(header) % 2 != 0 else ''}║")
    
    # Dấu ngăn cách
    print(f"    ╠{'═' * (panel_width - 2)}╣")

    # Nội dung chính
    for key, value in lines.items():
        key_padding = " " * (max_key_len - len(key))
        line_content = f"{key}{key_padding} : {value}"
        total_padding = " " * (panel_width - len(line_content) - 4)
        print(f"    ║ {line_content}{total_padding} ║")

    # Dấu ngăn cách
    print(f"    ╠{'═' * (panel_width - 2)}╣")
    
    # Status
    padding = " " * ((panel_width - len(status) - 2) // 2)
    print(f"    ║{padding}{status}{padding}{' ' if len(status) % 2 != 0 else ''}║")
    
    # Dòng cuối
    print(f"    ╚{'═' * (panel_width - 2)}╝\n")
