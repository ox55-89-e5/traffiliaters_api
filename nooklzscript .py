from nooklz_api import NooklzInterface
from money_button import MoneyButton

nooklz = NooklzInterface(nooklz_api_key = "450e9c2c0a859bccd215724a8741b2309ee3f208")
# nooklz.check_groups()
money_button = MoneyButton(nooklz)
lines = money_button.test_bms()