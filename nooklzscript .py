import json
import requests
from nooklz_api import NooklzInterface





nooklz = NooklzInterface(nooklz_api_key = "450e9c2c0a859bccd215724a8741b2309ee3f208")
nooklz.check_groups()
accounts = nooklz.get_profiles(groups = {255025 : nooklz.groups[255025]})
acts = nooklz.get_ad_accounts(groups = {None : nooklz.groups[None]})


# ids = nooklz.get_ids_from_json(accounts)
# print(ids)
# print(type(bms[0]))

# write_debug_json(accounts)

# get accounts from a certain group
# check bm qua