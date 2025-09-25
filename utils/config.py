import os
from pathlib import Path
from ruamel.yaml import YAML
from typing import Dict, Any
from functools import lru_cache

def load_yaml_config(file_path: str = "configs/settings.yml") -> Dict[str, Any]:
    """
    Load YAML config file với error handling
    
    Tham số:
        file_path: Đường dẫn tới file cấu hình YAML
        
    Trả về:
        Dictionary chứa dữ liệu cấu hình
        
    Ngoại lệ:
        FileNotFoundError: Nếu file cấu hình không tồn tại
        ValueError: Nếu YAML không hợp lệ hoặc rỗng
        RuntimeError: Nếu xảy ra lỗi khác khi tải cấu hình
    """
    try:
        config_file = Path(file_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        if config_file.stat().st_size == 0:
            raise ValueError(f"Config file is empty: {file_path}")
        
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
        
        with open(config_file, "r", encoding="utf-8") as file:
            config = yaml.load(file)
        
        if config is None:
            raise ValueError(f"Config file contains no valid YAML data: {file_path}")
        
        if not isinstance(config, dict):
            raise ValueError(f"Config must be a YAML dictionary, got {type(config).__name__}")
        
        return config
        
    except (FileNotFoundError, ValueError) as e:
        raise e
    except Exception as e:
        raise RuntimeError(f"Failed to load YAML config from {file_path}: {e}")

def load_yaml_config_cached(file_path: str = "configs/settings.yml") -> Dict[str, Any]:
    """
    Load YAML config với caching (chỉ cache trong memory, không check file changes)
    
    Tham số:
        file_path: Đường dẫn tới file cấu hình YAML

    Note: Cache sẽ persist cho đến khi restart application
    """
    @lru_cache(maxsize=1)
    def _cached_loader(path: str) -> Dict[str, Any]:
        return load_yaml_config(path)
    
    return _cached_loader(file_path)

def get_config(file_path: str = "configs/settings.yml", use_cache: bool = True) -> Dict[str, Any]:
    """
    Lấy dictionary chứa dữ liệu cấu hình
    
    Tham số:
        file_path: Đường dẫn tới file cấu hình YAML
        use_cache: Tùy chọn lưu cache
        
    Trả về:
        Dictionary chứa dữ liệu cấu hình
    """
    if use_cache:
        return load_yaml_config_cached(file_path)
    else:
        return load_yaml_config(file_path)

def get_config_value(key: str, default: Any = None, file_path: str = "configs/settings.yml") -> Any:
    """
    Lấy giá trị cụ thể từ cấu hình
    
    Tham số:
        key: Config key (supports nested keys like "database.host")
        default: Default value if key not found
        file_path: Đường dẫn tới file cấu hình YAML
        
    Trả về:
        Config value or default
    """
    try:
        config = get_config(file_path)
        
        # Support nested keys
        keys = key.split(".")
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
        
    except Exception:
        return default
