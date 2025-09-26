import requests
import hashlib

from helpers.console import logger
from utils.env import get_partner_id, get_partner_key
from utils.config import get_config_value


class ExchangeCard:
    def __init__(self):
        self.partner_id = get_partner_id()
        self.partner_key = get_partner_key()
        self.provider = get_config_value("provider", "https://card2k.com")

    def get_fee_exchange_card(self) -> dict:
        """
        API: Lấy phí đổi thẻ cào
        """

        url = f"{self.provider}/chargingws/v2/getfee?partner_id={self.partner_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"[API Card2K Exchange-Card] Lỗi hàm get_fee: {e}")
            return None
        except Exception as e:
            logger.error(f"[API Card2K Exchange-Card] Lỗi hàm get_fee: {e}")
            return None

    def exchange_card(self, data: dict) -> dict:
        """
        API: Gửi thẻ cào đến nhà cung cấp

        data:
            - telco: str
            - code: str
            - serial: str
            - amount: int
            - request_id: str
        """

        url = f"{self.provider}/chargingws/v2"
        sign = hashlib.md5(
            f"{self.partner_key}{data['code']}{data['serial']}".encode()
        ).hexdigest()
        payload = {
            "telco": data["telco"],
            "code": data["code"],
            "serial": data["serial"],
            "amount": data["amount"],
            "request_id": data["request_id"],
            "partner_id": self.partner_id,
            "sign": sign,
            "command": "charging",
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"[API Card2K Exchange-Card] Lỗi hàm exchange_card: {e}")
            return None
        except Exception as e:
            logger.error(f"[API Card2K Exchange-Card] Lỗi hàm exchange_card: {e}")
            return None

    def check_exchange_card(self, data: dict) -> dict:
        """
        API: Kiểm tra thẻ đã gửi

        data:
            - telco: str
            - code: str
            - serial: str
            - amount: int
            - request_id: str
        """

        url = f"{self.provider}/chargingws/v2"
        sign = hashlib.md5(
            f"{self.partner_key}{data['code']}{data['serial']}".encode()
        ).hexdigest()
        payload = {
            "telco": data["telco"],
            "code": data["code"],
            "serial": data["serial"],
            "amount": data["amount"],
            "request_id": data["request_id"],
            "partner_id": self.partner_id,
            "sign": sign,
            "command": "check",
        }
        try:
            response = requests.get(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"[API Card2K Exchange-Card] Lỗi hàm check_exchange_card: {e}")
            return None
        except Exception as e:
            logger.error(f"[API Card2K Exchange-Card] Lỗi hàm check_exchange_card: {e}")
            return None

    def check_status_api(self) -> bool:
        """
        API: Kiểm tra trạng thái API
        """

        payload = {
            'partner_id': self.partner_id,
            'partner_key': self.partner_key,
        }
        url = f"{self.provider}/chargingws/v2/check-api"
        try:
            response = requests.get(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if 'status' not in data:
                return False
            return data["status"] == 'active'
        except requests.RequestException as e:
            logger.error(f"[API Card2K Exchange-Card] Lỗi hàm get_fee: {e}")
            return None
        except Exception as e:
            logger.error(f"[API Card2K Exchange-Card] Lỗi hàm get_fee: {e}")
            return None
