from nooklz_api import NooklzInterface
from money_button import MoneyButton
from secret_money_button import SecretMoneyButton

nooklz = NooklzInterface(nooklz_api_key = "450e9c2c0a859bccd215724a8741b2309ee3f208")
# nooklz.check_groups()
money_button = SecretMoneyButton(nooklz)
# lines = money_button.test_bms()

money_button.link_bms()
money_button.crete_add_accounts(how_many_to_create=5)
# lines = money_button.link_bms()
money_button.export_trash_bms()
# money_button.export_extra_bms()
# money_button.crete_add_accounts(how_many_to_create=2)

# money_button.link_cards()

# money_button._write_debug_json(money_button._update_profiles())

