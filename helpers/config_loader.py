from ruamel.yaml import YAML


def get_yaml_config(file_path: str) -> dict[str, any]:
    """
    Tải cấu hình từ file yaml
    """
    yaml = YAML()
    with open(file_path, "r", encoding="utf-8") as file:
        config = yaml.load(file)
    return config
