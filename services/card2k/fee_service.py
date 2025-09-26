from api.card2k.exchange_card import ExchangeCard as ExchangeCardAPI
from helpers.console import logger


class FeeService:
    def __init__(self):
        self.api = ExchangeCardAPI()
        self.data_api = self.api.get_fee_exchange_card()

    def get_cheapest_telco_rate(self) -> dict:
        """
        Lấy thông tin phí đổi thẻ cào nhỏ nhất

        Trả về dict: {telco_min: str, fee_min: float}
        Nếu không tìm thấy trả về None
        """

        data_api = self.data_api
        if not self._validated_data_api():
            return None

        valid_items = [item for item in data_api if item.get("fees") is not None]
        if not valid_items:
            return None
        min_item = min(valid_items, key=lambda item: item["fees"])
        raw_fee = min_item.get("fees")
        truncated_fee = int(raw_fee * 10) / 10
        return {
            "telco_min": min_item.get("telco"),
            "fee_min": truncated_fee,
        }

    def get_min_fees_by_telco(self) -> dict:
        """
        Lấy phí nhỏ nhất của từng nhà mạng

        Trả về dict: {telco: fee_min, ...}
        Nếu không tìm thấy trả về None
        """
        data_api = self.data_api
        if not self._validated_data_api():
            return None

        telco_min_fees = {}
        for item in data_api:
            telco = item.get("telco")
            fee = item.get("fees")
            if telco is None or fee is None:
                continue
            if telco not in telco_min_fees or fee < telco_min_fees[telco]:
                truncated_fee = int(fee * 10) / 10
                telco_min_fees[telco] = truncated_fee
        telco_min_fees = dict(sorted(telco_min_fees.items(), key=lambda item: item[1]))

        return telco_min_fees if telco_min_fees else None

    def get_telco_fee_info(self, telco: str) -> dict:
        """
        Lấy thông tin phí thấp nhất và danh sách phí của một nhà mạng

        Trả về dict:
        {
            "telco": str,
            "fee_min": float,
            "fees": List[float]
        }
        Nếu không tìm thấy trả về None
        """

        data_api = self.data_api
        if not self._validated_data_api():
            return None

        result = {
            "fee_min": None,
            "amount_min": None,
            "list_fee": None,
        }
        fee_dict = {}
        for item in data_api:
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

    def _validated_data_api(self) -> bool:
        """
        Kiểm tra dữ liệu API có hợp lệ không
        """

        if not self.data_api:
            return False
        if len(self.data_api) == 0:
            return False
        if any("status" in item for item in self.data_api):
            logger.error(f"[Service Card2K Fee] Kết quả API: " + str(self.data_api))
            return False

        return True
