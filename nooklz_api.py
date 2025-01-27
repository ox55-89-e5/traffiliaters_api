import requests
import json
from typing import Collection, TypeVar
from typing import List, Optional

T = TypeVar("T")  # Generic type  

class NooklzInterface:          
    def __init__(self, nooklz_api_key : str):
        self.headers = {
            "Authorization": f"Token {nooklz_api_key}"
        }
        self.update()
    
    def get_ids_from_json(self, json_collection : Collection[T]) -> {int}:
        ids = {}
        for element in json_collection:
            ids[element["id"]] = [element["id"]]
        return ids

    # additional filters: credit cards, created at, statu, BM ids, can create ad account, page count, users, pending users,
    # invite count, main page, information filled
    def get_ad_accounts(self, nooklz_profile_ids : {T} = None, groups : {T} = None) -> Collection:
        bms = self.get_bms(nooklz_profile_ids, groups)  
        ad_accounts = [ad_account for bm in bms for ad_account in bm["acts"]]
        return ad_accounts

    # additional filters: credit cards, created at, statu, BM ids, can create ad account, page count, users, pending users,
    # invite count, main page, information filled
    def get_bms(self, nooklz_profile_ids : {T} = None, groups : {T} = None) -> Collection:
        profiles = self.get_profiles(nooklz_profile_ids, groups)  
        bms = [bm for profile in profiles for bm in profile["bms"]]
        return bms

    # additional filters: main ad account status, appeal status, status, added date, proffesional mode, page count, BM count,
    # email
    def get_profiles(self, nooklz_profile_ids : {T} = None, groups : {T} = None) -> Collection:
        url = "https://nooklz.com/api/accounts?format=json"
        request_data = {"format" : "json"}
        profiles = requests.get(url, json=request_data, headers=self.headers).json()
        if nooklz_profile_ids != None:
            profiles = [profile for profile in profiles if profile["id"] in nooklz_profile_ids]
        if groups:
            profiles = [profile for profile in profiles if profile["label"] is not None and profile["label"]["id"] in groups
                        or profile["label"] is None and None in groups]    
        return profiles

    def update(self):
        self.update_accounts()
        self.update_groups()

    def update_accounts(self):
        try:
            url = 'https://nooklz.com/api/accounts?format=json&exclude=profile'
            # Send GET request
            self.request_data = {
                    "format" : "json",
                    "exclude" : "profile"
                }
            response = requests.get(url, json=self.request_data, headers=self.headers)
            if response.status_code != 200:
                print(f"An error occured, status code {response.status_code}")
            # Parse the JSON string into a Python list
            self.accounts = response.json()
            # Create dictionary to store labels
                   
        except requests.RequestException as e:
            print(f"An error occurred while requesting profiles: {e}")
        pass

    def update_groups(self):
        self.groups = {None : {"id" : "None", "label_name" : "None", "account_ids" : []}}
        # Process each account in the JSON data
        for account in self.accounts:
            if account["label"] is not None:
                if account["label"]["id"] not in self.groups:
                    self.groups[account["label"]["id"]] = account["label"]
                    self.groups[account["label"]["id"]]["account_ids"] = []
                self.groups[account["label"]["id"]]["account_ids"].append(account["id"])

    def check_groups(self):
        for group_ in self.groups:
            group = self.groups[group_]
            print(f"Name: {group['label_name']:<25} Id:{group['id']:<10} Accounts: {len(group['account_ids'])}")

