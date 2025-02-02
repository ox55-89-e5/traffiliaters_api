from nooklz_api import NooklzInterface
from money_button import MoneyButton
from secret_money_button import SecretMoneyButton

nooklz = NooklzInterface(nooklz_api_key = "450e9c2c0a859bccd215724a8741b2309ee3f208")
nooklz.check_groups()
money_button = SecretMoneyButton(nooklz)
lines = money_button.test_bms()
# lines = money_button.link_bms()
# money_button.export_trash_bms()
# money_button.export_extra_bms()
# money_button.crete_add_accounts(how_many_to_create=2)
# money_button.link_cards()
# result =  [
#                 "<p><span style=\"color: green;\"><b>[2025-01-27 07:49:27]</b> [Profile:Marharyta Shchur] [Bm:1351587042946448] Створено рекламний акаунт: 591239073700926</span></p>",
#                 "<p><span style=\"color: green;\"><b>[2025-01-27 07:49:31]</b> [Profile:Marharyta Shchur] [Bm:1351587042946448] Надано користувачеві права адміністратора</span></p>",
#                 "<p><span style=\"color: green;\"><b>[2025-01-27 07:49:33]</b> [Profile:Marharyta Shchur] [Bm:1059072242897438] Створено рекламний акаунт: 615262017893186</span></p>",
#                 "<p><span style=\"color: green;\"><b>[2025-01-27 07:49:37]</b> [Profile:Marharyta Shchur] [Bm:1059072242897438] Надано користувачеві права адміністратора</span></p>"
#             ]
# print(money_button._parse_djekxa_invites("https://fb.me/1TUVtzEw9JpwteX|business_id=9272230242854133"))
# print(money_button._extract_ad_account_ids(result))

# money_button._write_debug_json(money_button._update_profiles())