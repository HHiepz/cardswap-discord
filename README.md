## Discord Bot Nạp Thẻ Cào [![GitHub Release](https://img.shields.io/github/v/release/HHiepz/cardswap-discord?style=flat)](https://github.com/HHiepz/cardswap-discord/releases) [![Discord](https://img.shields.io/discord/1068941579244539904.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://2k9xteam.shop/discord) 


Bot Discord này giúp tự động hóa việc nạp thẻ cào, tích hợp trực tiếp giữa server Discord của bạn và website đổi thẻ.

**Dịch vụ đang hỗ trợ**: [Card2k](https://card2k.com/)

## Tính năng hiện có
- Nạp thẻ tự động
- Kiểm tra phí (max / min)

## Hướng dẫn cài đặt

**1. Chuẩn bị**:

- Cài đặt [Python](https://www.python.org/downloads/) (phiên bản 3.13 trở lên)
- Tải source bot [tại đây](https://github.com/HHiepz/cardswap/releases), giải nén và truy cập đến thư mục.

**2. Cài đặt các thư viện cần thiết**:

Mở giao diện dòng lệnh (Command Prompt, Terminal, hoặc PowerShell) trong thư mục bạn vừa giải nén.
```bash
pip install -r requirements.txt
cp .\.env.example .env
```

**3. Cấu hình Bot**:
- Mở thư mục `.env` cập nhật các thông tin sau:
  
  - ` BOT_TOKEN ` : token bot Discord, tạo [tại đây](https://discord.com/developers/applications)
  - ` GUILD_ID ` : ID của server discord bạn

- Cấu hình custom bot tại thư mục `configs/settings.yaml`.

**4. Chạy Bot**:
```bash
python main.py
```

## Danh sách lệnh cơ bản

| Lệnh                                                   | Chức năng                             | Permission    |
|--------------------------------------------------------|---------------------------------------|---------------|
| /set-up                                                | Kết nối API với website               | admin         |
| /show-setup                                            | Hiển thị setup đã cài đặt             | admin         |
| /kiem-tra-phi <nhà mạng>                               | Kiểm tra phí từng loại thẻ            | member        |
| /nap-the <nhà mạng> <mệnh giá> <mã thẻ> <serial thẻ>   | Nạp thẻ                               | member        |


## Hình ảnh

![](https://i.ibb.co/HLLHtGr1/awcwac.png)

![](https://i.ibb.co/KxDhf64y/image.png)

![](https://i.ibb.co/hFPVx7hs/image.png)


