import json
import requests
from nooklz_api import NooklzInterface


def write_debug_json(json_code):
    # File path to save the JSON
    file_path = "output.json"

    # Write JSON data to a file with UTF-8 encoding
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(json_code, file, indent=4, ensure_ascii=False)



nooklz = NooklzInterface(nooklz_api_key = "450e9c2c0a859bccd215724a8741b2309ee3f208")
nooklz.check_groups()
accounts = nooklz.get_accounts(groups = {None : nooklz.groups[None]})
ids = nooklz.get_ids_from_json(accounts)
print(ids)
print(accounts[0]["account_name"])