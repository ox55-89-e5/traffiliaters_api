import requests
import json
from typing import Collection, TypeVar
from typing import List, Optional
import time
from functools import wraps
from facebook_api import facebook_timezones

T = TypeVar("T")  # Generic type  


class NooklzInterface:          
    def __init__(self, nooklz_api_key : str):
        self.headers = {
            "Authorization": f"Token {nooklz_api_key}"
        }
        self.update()
    
    
    def __wait_result(self, url, json_payload):
         # Track start time
        start_time = time.time()
        timeout = 25  # Timeout in seconds
        attempts = 0
        response = json_payload
        while "log" not in response:
            attempts += 1
            # Check for timeout
            if time.time() - start_time > timeout:
                print(f"Timeout reached. Exiting loop. Attempts:{attempts}")
                return response
            response = make_post_request(url, json=json_payload, headers=self.headers).json()
            time.sleep(1)
            
        for task in response["log"]:
            print(task["result"])
        return response

    def check_profiles(self, profile_ids : {int}) -> Collection[T]:
        url = "https://nooklz.com/api/accounts/check"
        request_data = {
            "format" : "json",
            "account_ids" : [profile_id for profile_id in profile_ids]
        }
        response = make_post_request(url, json=request_data, headers=self.headers).json()
        response = self.__wait_result(url="https://nooklz.com/api/accounts/result?exclude=profiles", json_payload=response)      
        return response

    def create_ad_accounts(self, profile_id : int, bm_ids: Collection[int],
                           name_pattern : str, 
                           currency : str = "USD",
                           timezone : str = "TZ_AMERICA_LOS_ANGELES") -> Collection[T]:
        url = "https://nooklz.com/api/tasks/create"
        request_data = {
            "format" : "json",
            "task" : "create_bm_ad_account",
            "data" : [
                {
                    "account_id" : profile_id,
                    "bm_ids" : [
                                {
                                    "bm_id": bm_id,
                                    "currency": currency,
                                    "timezone": str(facebook_timezones[timezone]),
                                    "name": f"{name_pattern} {index}"
                                }
                                for index, bm_id in enumerate(bm_ids)
                            ]
                }
            ]
        }
        response = make_post_request(url, json=request_data, headers=self.headers).json()
        response = self.__wait_result(url="https://nooklz.com/api/accounts/result?exclude=bms", json_payload=response)      
        return response


    def accept_bm_invites(self, profile_id : int, invite_links : Collection[str]) -> Collection[T]:
        url = "https://nooklz.com/api/tasks/create"
        request_data = {
            "format" : "json",
            "task": "accept_bm_invite",
            "data": [{"account_id": profile_id, "invites": [link]} for link in invite_links]
        }
        response = make_post_request(url, json=request_data, headers=self.headers).json()
        response = self.__wait_result(url="https://nooklz.com/api/accounts/result?exclude=profiles", json_payload=response)    
        return response

    def get_ids_from_json(self, json_collection : Collection[T]) -> {int}:
        ids = {}
        for element in json_collection:
            ids[element["id"]] = element["id"]
        return ids

    # additional filters: credit cards, created at, statu, BM ids, can create ad account, page count, users, pending users,
    # invite count, main page, information filled
    def get_ad_accounts(self, nooklz_profile_ids : {T} = None, groups : {T} = None) -> Collection:
        bms = self.get_bms(nooklz_profile_ids, groups)  
        ad_accounts = [ad_account for bm in bms for ad_account in bm["acts"]]
        return ad_accounts

    # additional filters: credit cards, created at, statu, BM ids, can create ad account, page count, users, pending users,
    # invite count, main page, information filled
    def get_bms(self, nooklz_profile_ids : {T} = None, groups : {T} = None,
                 can_create_ad_account : bool = None,
                   is_disabled : bool = None) -> Collection:
        profiles = self.get_profiles(nooklz_profile_ids, groups)  
        bms = [bm for profile in profiles for bm in profile["bms"]]
        if can_create_ad_account != None:
            bms = [bm for bm in bms if bm["can_create_ad_account"] == can_create_ad_account]
        if is_disabled != None:
            bms = [bm for bm in bms if bm["is_disabled_for_integrity_reasons"] == is_disabled]
        return bms

    # additional filters: main ad account status, appeal status, status, added date, proffesional mode, page count, BM count,
    # email
    def get_profiles(self, nooklz_profile_ids : {T} = None, groups : {T} = None) -> Collection:
        url = "https://nooklz.com/api/accounts?format=json"
        request_data = {"format" : "json"}
        profiles = make_get_request(url, json=request_data, headers=self.headers).json()
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


def log_requests(log_file="requests_log.txt"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract the URL from args or kwargs
            url = kwargs.get('url')  # Check if URL is passed as a keyword argument
            if not url and len(args) > 0:  # If not, try to extract it from positional arguments
                url = args[0]

            # Execute the original function and log the details
            try:
                response = func(*args, **kwargs)
                with open(log_file, "a", encoding="utf-8") as log:
                    # log.write(f"URL: {kwargs.get('url', 'N/A')}\n")
                    log.write(f"URL: {url if url else 'N/A'}\n")
                    log.write(f"Payload: {json.dumps(kwargs.get('json', {}), indent=2)}\n")
                    log.write(f"Response Code: {response.status_code}\n")
                    # Log response content (truncate if too long)
                    try:
                        response_content = response.json()  # Attempt to parse as JSON
                        log.write(f"Response Content (JSON): {json.dumps(response_content, indent=2)}\n")
                    except ValueError:  # If not JSON, fallback to plain text
                        response_content = response.text
                        log.write(f"Response Content (Text): {response_content[:500]}...\n")  # Limit to 500 chars

                    log.write("=" * 50 + "\n")
                return response
            except Exception as e:
                # Log any errors during execution
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"Error: {e}\n")
                    log.write("=" * 50 + "\n")
                raise
        return wrapper
    return decorator

# Example Usage
@log_requests(log_file="requests_log.txt")
def make_post_request(url, json=None, headers=None):
    response = requests.post(url, json=json, headers=headers)
    return response

# @log_requests(log_file="requests_log.txt")
def make_get_request(url, json=None, headers=None):
    response = requests.get(url, json=json, headers=headers)
    return response