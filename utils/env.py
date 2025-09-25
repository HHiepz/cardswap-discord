import os
from dotenv import load_dotenv
from typing import Optional

# Load env một lần khi import module
_ENV_LOADED = False


def _ensure_env_loaded() -> bool:
    """
    Đảm bảo env đã được load
    """
    global _ENV_LOADED
    if not _ENV_LOADED:
        if os.path.exists(".env"):
            load_dotenv(".env")
            _ENV_LOADED = True
            return True
        return False
    return True


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Lấy giá trị env variable
    """
    _ensure_env_loaded()
    return os.getenv(key, default)


def get_required_env(key: str) -> str:
    """
    Lấy env variable bắt buộc, raise error nếu không có
    """
    value = get_env(key)
    if value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value


def get_discord_token() -> str:
    """
    Lấy Discord token
    """
    return get_required_env("DISCORD_TOKEN")


def get_partner_id() -> str:
    """
    Lấy partner id
    """
    return get_required_env("PARTNER_ID")


def get_partner_key() -> str:
    """
    Lấy partner key
    """
    return get_required_env("PARTNER_KEY")
