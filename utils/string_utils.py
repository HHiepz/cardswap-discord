import uuid


def generate_uuid(short: bool = False) -> str:
    """
    Tạo UUID duy nhất
    """
    unique_id = str(uuid.uuid4())
    return unique_id[:8] if short else unique_id
