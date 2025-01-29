import json
import requests
from nooklz_api import NooklzInterface
import os
class MoneyButton:
    def __init__(self, NooklzInterface : NooklzInterface):
        self.nooklz = NooklzInterface
        pass
    
    def test_bms(self, BM_limit : int = 20):
        profiles = self.nooklz.get_profiles(groups = {258598 : self.nooklz.groups[258598]}) # money button
        # filter profiles which have not more BMs than BM_limit
        profiles = [profile for profile in profiles if len(profile["bms"]) <= BM_limit]
        response = []
        for profile in profiles:
            bm_invites = self.eat_bm_invites(how_many=1)       
            print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} tries to accept invites:")
            print(bm_invites)
            self.nooklz.accept_bm_invites(profile_id=profile["id"], invite_links=bm_invites)
            print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} trying to check profile:")
            self.nooklz.check_profiles(profile_ids={profile['id'] : profile['id']})
            print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} searching for a BM to creat ad account:")
            bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']}, can_create_ad_account=True, is_disabled=False)
            if len(bms) < 1:
                print(f"Not enough active BMs that could create an ad account")
            else:
                print(f"Actives BMs that can create an ad account: {len(bms)}, BM chosen: {bms[0]['bm_name']} ({bms[0]['business_id']})")
                print(f"Creating an ad account for BM chosen: {bms[0]['bm_name']} ({bms[0]['business_id']})")
                self.nooklz.create_ad_accounts(profile['id'], [bms[0]['business_id']], "BarShopBM")
            
        # self.write_debug_json(response)

    def eat_bm_invites(self, how_many : int, input_file : str = r"BM_invites.txt", output_file : str = r"UsedBM_invites.txt"):
        lines_to_transfer = []
        try:
            # Open the input file in read mode
            with open(input_file, 'r', encoding='utf-8') as infile:
                # Read all lines from the input file
                all_lines = infile.readlines()

            # Get the first n lines to transfer
            lines_to_transfer = all_lines[:how_many]
            if how_many > len(lines_to_transfer):
                print(f"requested {how_many} bm invite links, but received only {len(lines_to_transfer)}, buy BMs")

            # Open the output file in append mode to write the lines
            with open(output_file, 'a', encoding='utf-8') as outfile:
                # Write the lines to the output file
                outfile.writelines(lines_to_transfer)

            # Get the remaining lines after the first n lines
            remaining_lines = all_lines[how_many:]

            # Rewrite the remaining lines back into the input file
            with open(input_file, 'w', encoding='utf-8') as infile:
                infile.writelines(remaining_lines)

            # print(f"Successfully wrote the first {how_many} lines to {output_file}.")
        except FileNotFoundError:
            print(f"Error: The file '{input_file}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        return [line.strip() for line in lines_to_transfer]
    
    def write_debug_json(self, json_code, file_path : str = "output.json"):
        # Write JSON data to a file with UTF-8 encoding
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json_code, file, indent=4, ensure_ascii=False)