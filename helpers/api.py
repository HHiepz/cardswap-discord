import requests
from database.session import SessionLocal
from database.models import Card2k
from __init__ import (
    __title__,
    __author__,
    __version__,
    __date_created__,
    __last_updated__,
    __support_channel__,
)
from ruamel.yaml import YAML
from helpers.helper import get_data_file_yml, random_string
from helpers.console import add_log
import uuid
import hashlib


# Lấy dữ liệu từ API
def get_fee_api():
    config = get_data_file_yml()
    session = SessionLocal()
    data = session.query(Card2k.partner_id).first()
    if not data or not data.partner_id or not config["provider"]:
        add_log(
            "[FUNC: GET_FEE_API] Thiếu dữ liệu database partner_id hoặc nhà cung cấp (provider) trong file settings.yml.",
            "ERROR",
        )
        return None
    partner_id = data.partner_id
    url = f"{config['provider']}/chargingws/v2/getfee?partner_id={partner_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        add_log(f"[FUNC: GET_FEE_API] Lỗi khi truy cập API: {e}", "ERROR")
        return None
    except Exception as e:
        add_log(f"[FUNC: GET_FEE_API] Lỗi khi truy cập API: {e}", "ERROR")
        return None


# Lấy phí thấp nhất của tất cả nhà mạng
def get_fee_telco_api_min():
    result = {
        "telco_min": None,
        "fee_min": None,
    }
    data = get_fee_api()
    if data is not None and isinstance(data, list) and len(data) > 0:
        min_fee = None
        min_telco = None
        for item in data:
            fee = item.get("fees")
            telco = item.get("telco")
            if fee is not None and telco is not None:
                if (min_fee is None) or (fee < min_fee):
                    min_fee = fee
                    min_telco = telco
        result["fee_min"] = min_fee
        result["telco_min"] = min_telco
    return result


# Lấy phí thấp nhất của tất cả nhà mạng
def get_all_fee_min_telco_api():
    data = get_fee_api()
    telco_fee_min = {}
    if data is not None and isinstance(data, list) and len(data) > 0:
        for item in data:
            telco = item.get("telco")
            fee = item.get("fees")
            if telco is not None and fee is not None:
                if telco not in telco_fee_min or fee < telco_fee_min[telco]:
                    telco_fee_min[telco] = fee
    # Sắp xếp dict theo fee tăng dần
    telco_fee_min_sorted = dict(sorted(telco_fee_min.items(), key=lambda x: x[1]))
    return telco_fee_min_sorted


# Lấy phí của 1 nhà mạng
def get_fee_telco_api(telco: str):
    result = {
        "fee_min": None,
        "amount_min": None,
        "list_fee": None,
    }
    data = get_fee_api()
    fee_dict = {}

    if data is not None and isinstance(data, list) and len(data) > 0:
        for item in data:
            if str(item.get("telco")).upper() == str(telco).upper():
                amount = str(item.get("value"))
                fee = item.get("fees")
                if amount is not None and fee is not None:
                    fee_dict[amount] = fee

        if fee_dict:
            # Tìm fee nhỏ nhất và amount tương ứng
            min_fee = min(fee_dict.values())
            min_amount = None
            for amount, fee in fee_dict.items():
                if fee == min_fee:
                    min_amount = int(amount)
                    break

            result["fee_min"] = min_fee
            result["amount_min"] = min_amount
            result["list_fee"] = fee_dict

    return result


# Gửi thẻ
def exchange_card(telco: str, amount: int, code: str, serial: str):
    config = get_data_file_yml()
    session = SessionLocal()
    data = session.query(Card2k).first()
    partner_id = data.partner_id
    partner_key = data.partner_key
    api_url = config["provider"] or "https://card2k.com"
    request_id = random_string()
    sign = hashlib.md5(f"{partner_key}{code}{serial}".encode()).hexdigest()

    try:
        payload = {
            "telco": telco,
            "code": code,
            "serial": serial,
            "amount": amount,
            "request_id": request_id,
            "partner_id": partner_id,
            "sign": sign,
            "command": "charging",
        }

        url = f"{api_url}/chargingws/v2"
        response = requests.get(url, timeout=10, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        add_log(f"[FUNC: EXCHANGE_CARD] Lỗi khi truy cập API: {e}", "ERROR")
        return None
    except Exception as e:
        add_log(f"[FUNC: EXCHANGE_CARD] Lỗi khi gửi thẻ: {e}", "ERROR")
        return None
    finally:
        session.close()


# Kiểm tra trạng thái thẻ
def check_card_status(telco: str, amount: int, code: str, serial: str, request_id: str):
    config = get_data_file_yml()
    session = SessionLocal()
    data = session.query(Card2k).first()
    partner_id = data.partner_id
    partner_key = data.partner_key
    api_url = config["provider"] or "https://card2k.com"
    sign = hashlib.md5(f"{partner_key}{code}{serial}".encode()).hexdigest()

    try:
        payload = {
            "telco": telco,
            "code": code,
            "serial": serial,
            "amount": amount,
            "request_id": request_id,
            "partner_id": partner_id,
            "sign": sign,
            "command": "check",
        }

        url = f"{api_url}/chargingws/v2"
        response = requests.get(url, timeout=10, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        add_log(f"[FUNC: CHECK_CARD_STATUS] Lỗi khi truy cập API: {e}", "ERROR")
        return None
    except Exception as e:
        add_log(f"[FUNC: CHECK_CARD_STATUS] Lỗi khi gửi thẻ: {e}", "ERROR")
        return None
    finally:
        session.close()
