import json
import requests
from nooklz_api import NooklzInterface


def write_debug_json(json_code):
    # File path to save the JSON
    file_path = "output.json"

    # Write JSON data to a file with UTF-8 encoding
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(json_code, file, indent=4, ensure_ascii=False)


class MoneyButton:
    def __init__(self):
        pass