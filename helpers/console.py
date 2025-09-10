import os
import datetime
from __init__ import __title__, __author__, __version__, __date_created__, __last_updated__, __support_channel__

def print_bot_info():
    # Clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[94m========== Thông tin Bot ==========\033[0m")
    print(f"\033[92mTên bot: {__title__}\033[0m")
    print(f"\033[92mTác giả: {__author__}\033[0m")
    print(f"\033[92mPhiên bản: {__version__}\033[0m")
    print(f"\033[92mNgày tạo: {__date_created__}\033[0m")
    print(f"\033[92mNgày cập nhật: {__last_updated__}\033[0m")
    print(f"\033[92mKênh hỗ trợ: {__support_channel__}\033[0m")
    print("\033[94m===================================\033[0m")
    print("\033[96mCảm ơn bạn đã sử dụng bot này!\033[0m")
    print("\033[93mNếu gặp lỗi hoặc cần trợ giúp, vui lòng liên hệ tác giả hoặc kiểm tra lại file cấu hình (.env, settings.yml).\033[0m")
    print("\033[93mBạn cũng có thể xem log trong thư mục 'logs' để biết thêm chi tiết về lỗi.\033[0m")
    print("\033[93mLiên hệ trợ giúp hoặc báo lỗi: vui lòng liên hệ tác giả hoặc kiểm tra file cấu hình. Để đóng bot, nhấn Ctrl + C.\033[0m")
    print("\033[94m===================================\033[0m")
    print("\033[92mBot đã sẵn sàng và đang chạy\033[0m")



def add_log(message: str, level: str = "INFO"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{now}]: [{level.upper()}] {message}\n"
    with open("logs/discord.log", "a", encoding="utf-8") as file:
        file.write(log_line)