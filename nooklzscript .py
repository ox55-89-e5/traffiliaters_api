from nooklz_api import NooklzInterface
from money_button import MoneyButton
from secret_money_button import SecretMoneyButton
from random_word import RandomWords

r = RandomWords()
print(r.get_random_word())  # Output: Random word from API

nooklz = NooklzInterface(nooklz_api_key = "450e9c2c0a859bccd215724a8741b2309ee3f208")
nooklz.check_groups()
money_button = SecretMoneyButton(nooklz)
# lines = money_button.test_bms()
# lines = money_button.link_bms()
# money_button.export_trash_bms()
# money_button.export_extra_bms()