import discord
import requests
import datetime
import random
import string
import time
import uuid
from __init__ import (
    __title__,
    __author__,
    __version__,
    __date_created__,
    __last_updated__,
    __support_channel__,
)
from ruamel.yaml import YAML

# Lấy dữ liệu từ file settings
def get_data_file_yml(file_name: str = "settings"):
    yaml = YAML()
    with open(f"configs/{file_name}.yml", "r", encoding="utf-8") as file:
        config = yaml.load(file)

    return config


# Hàm random string 
def random_string(length: int = 32, extra: str = ""):
    """
    Sử dụng UUID để tạo chuỗi duy nhất.
    """
    unique_id = str(uuid.uuid4())
    
    if extra:
        return f"{unique_id[:length]}_{extra}"
    return unique_id[:length]