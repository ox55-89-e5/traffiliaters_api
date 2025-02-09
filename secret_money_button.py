from nooklz_api import NooklzInterface
from money_button import MoneyButton
import time
import json
import requests
import os
from facebook_api import disable_reason

# used card :Libby Thornton 4288030279922944;02/29;331
class SecretMoneyButton(MoneyButton):
    def link_cards(self):
        profiles = self._update_profiles()
        print("linking cards:")
        # find accounts without any attached card 
        for profile in profiles:
            acts = []
            
            # bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']}, can_create_ad_account=False, is_disabled=False)
            bms = self.nooklz.get_bms(nooklz_profile_ids={18326411 : 18326411}, can_create_ad_account=False, is_disabled=False)
            for bm in bms:
                acts.extend(bm['acts'])
            acts = [act for act in acts if act["funding_sources"] == "[]" and act["disable_reason"] == disable_reason["ACCOUNT_ENABLED"]]
            # self.nooklz.link_pudge_for_UA_farms(profile_id=18326411, card="4288030279231114;01;29;790", acts=acts[:1])
            self.nooklz.link_pudge_for_UA_farms(profile_id=18326411, card="4288030279231114;02;29;247", acts=acts[:1])
            return

    # exports all active bms without locked ad accounts if BM count exceeds the limit
    # accepts invites with other profiles not to exceed the limit
    # leaves from previous accounts
    def export_extra_bms(self, BM_limit : int = 20):
        profiles = self._update_profiles()
            
        # Export bms
        print("Exporting BMs:")
        profiles = [profile for profile in profiles if len(profile["bms"]) > BM_limit]
        for profile in profiles:
            active_bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']}, can_create_ad_account=True, is_disabled=False)
            active_bms_to_export = active_bms[-(len(profile["bms"])-BM_limit):]
            for bm in active_bms_to_export:
                response = self.nooklz.export_bm_invites(profile_id=profile["id"], bm_ids=[bm["business_id"]])
                results = self.nooklz.get_results(response)
                for result in results:
                    self._write_cleaned_invites(f'{{"link":"{result}", "business_id":{bm["business_id"]}, "nooklz_profile_id": {profile["id"]}}}', file = "./BM_invites/Internal.txt")

        # Accept invites
        print("Accepting invites:")
        profiles = self.nooklz.get_profiles(groups = {259151 : self.nooklz.groups[259151]}) # Ready to link
        # filter profiles which have not more BMs than BM_limit
        profiles = [profile for profile in profiles if len(profile["bms"]) <= BM_limit]
        print(f"Accepting invites for {len(profiles)} profiles, limit is {BM_limit}.")
        for profile in profiles:
            print(f"{BM_limit - len(profile['bms'])}, {len(profile['bms'])}")
            for n in range (BM_limit - len(profile["bms"])):
                bm_invites = self._eat_bm_invites(how_many=1, input_file=r"./BM_invites/Internal.txt", output_file=r"./BM_invites/Internal_used.txt")
                if bm_invites == None:
                    break 
                bm_invite = json.loads(bm_invites[0])["link"]
                print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} tries to accept invites:")
                print(bm_invite)
                self.nooklz.accept_bm_invites(profile_id=profile["id"], invite_links=[bm_invite])

        # Leave business managers
        print("Leaving BMs:")
        bm_invites = self._eat_bm_invites(how_many=1, input_file=r"./BM_invites/Internal_used.txt", output_file=r"./BM_invites/Internal_released.txt")
        while bm_invites != None:
            invite_json = json.loads(bm_invites[0])
            self.nooklz.leave_bms(profile_id=invite_json["nooklz_profile_id"], bm_ids=[invite_json["business_id"]])
            bm_invites = self._eat_bm_invites(how_many=1, input_file=r"./BM_invites/Internal_used.txt", output_file=r"./BM_invites/Internal_released.txt")

        self._update_profiles()

    # exports disabled BMs or BMs with first add account with on Risk or Policy
    def export_trash_bms(self):
        profiles = self._update_profiles()
            
        # Export bms
        print("Exporting BMs:")
        for profile in profiles:
            disabled_bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']}, can_create_ad_account=False, is_disabled=True)
            active_bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']}, can_create_ad_account=False, is_disabled=False)
            bms_wih_disabled_acts = [bm for bm in active_bms if bm["acts"][0]["disable_reason"] == disable_reason["ADS_INTEGRITY_POLICY"]
                                    or bm["acts"][0]["disable_reason"] == disable_reason["RISK_PAYMENT"]]
            for bm in bms_wih_disabled_acts + disabled_bms:
                response = self.nooklz.export_bm_invites(profile_id=profile["id"], bm_ids=[bm["business_id"]])
                results = self.nooklz.get_results(response)
                for result in results:
                    self._write_cleaned_invites(result)

        # Accept invites
        print("Accepting invites:")
        profile = self._update_profiles(group_id=259225)[0] # BM Trash 259225
        trash_bm_invites = self._eat_bm_invites(how_many=1, input_file=r"./BM_invites/trash_invites.txt", output_file=r"./BM_invites/trash_invites_used.txt")
        while trash_bm_invites != None:
            print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} tries to accept invites:")
            print(trash_bm_invites)
            self.nooklz.accept_bm_invites(profile_id=profile["id"], invite_links=trash_bm_invites)
            trash_bm_invites = self._eat_bm_invites(how_many=1, input_file=r"./BM_invites/trash_invites.txt", output_file=r"./BM_invites/trash_invites_used.txt")
            
        # Leave business managers
        print("Leaving BMs:")
        for profile in profiles:
            disabled_bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']}, can_create_ad_account=False, is_disabled=True)
            active_bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']}, can_create_ad_account=False, is_disabled=False)
            bms_wih_disabled_acts = [bm for bm in active_bms if bm["acts"][0]["disable_reason"] == disable_reason["ADS_INTEGRITY_POLICY"]
                                    or bm["acts"][0]["disable_reason"] == disable_reason["RISK_PAYMENT"]]
            for bm in bms_wih_disabled_acts + disabled_bms:
                response = self.nooklz.leave_bms(profile_id=profile["id"], bm_ids=[bm["business_id"]])

        # Update profiles after cleaning
        self._update_profiles()

    def test_bms(self, BM_limit : int = 20):
        try:
            profiles = self._update_profiles(258598) #258598 money button

            # filter profiles which have not more BMs than BM_limit
            profiles = [profile for profile in profiles if len(profile["bms"]) <= BM_limit]
            total_samples = 0
            succesful_samples = 0
            for profile in profiles:
                try:
                    total_samples = total_samples + 1
                    bm_invites = self._eat_bm_invites(how_many=1, input_file=r"./BM_invites/djekxa.txt", output_file=r"./BM_invites/djekxa_used.txt")
                    invite = self._parse_djekxa_invites(bm_invites[0])
                    print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} tries to accept invites:")
                    print(invite)
                    business_id = invite["business_id"]
                    invite = invite["invite"]
                    self.nooklz.accept_bm_invites(profile_id=profile["id"], invite_links=[invite])

                    print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} trying to check the profile:")
                    self.nooklz.check_profiles(profile_ids={profile['id'] : profile['id']})

                    print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} searching for the BM to create an ad account:")
                    bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']})
                    bm = next((bm for bm in bms if bm["business_id"] == business_id), None)
                    if bm != None:
                        # Check BM status
                        invalid = False
                        if bm["is_disabled_for_integrity_reasons"] == True:
                            print(f"A BM {['bm_name']} {business_id} is disabled")
                            invalid = True
                        if bm["can_create_ad_account"] == False:
                            print(f"A BM {['bm_name']} {business_id} can't create ad accounts")
                            invalid = True
                        if invalid:
                            return
                        print(f"Creating an ad account for a BM {bm['bm_name']} {business_id}:")
                        response = self.nooklz.create_ad_accounts(profile_id=profile['id'],bm_ids= [business_id],name_pattern= "Djekxa", timezone="TZ_EUROPE_SOFIA")
                        accounts_created = self._extract_ad_account_ids(self.nooklz.get_results(response))
                        if accounts_created != None and accounts_created: #also checke whether accounts_created!={} 
                            # check ad account status
                            print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} trying to check the profile:")
                            self.nooklz.check_profiles(profile_ids={profile['id'] : profile['id']})
                            bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']})
                            bm = next((bm for bm in bms if bm["business_id"] == business_id), None)
                            act = next((act for act in bm['acts'] if act["act_id"] == accounts_created[business_id][0]), None)
                            if act["disable_reason"] == disable_reason["ACCOUNT_ENABLED"]:
                                succesful_samples = succesful_samples + 1
                                print(f"act {act['act_name']} {accounts_created[business_id][0]} created on BM {bm['bm_name']} {business_id} is alive")
                            elif act["disable_reason"] == disable_reason["ADS_INTEGRITY_POLICY"]:
                                print("Policy")
                            elif act["disable_reason"] == disable_reason["RISK_PAYMENT"]:
                                print("Risk")
                            else:
                                print("Something is wrong with ad account")
                        else:
                            print(f"Can't access account information")
                            
                    else:
                        print(f"Couldn't get access to BM with id {business_id}")
                except Exception as e:
                    print(f"Error: {e}")

            print(f"\n Bm check finished: {succesful_samples} out of {total_samples} were successful")
        except Exception as e:
                print(f"Error: {e}")
                

    def crete_add_accounts(self, BM_limit : int = 30, how_many_to_create : int = 2):
        profiles = self._update_profiles()
        profiles = [profile for profile in profiles if len(profile["bms"]) <= BM_limit]
        for profile in profiles:                        
            print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} searching for BMs to creat ad accounts:")    
            bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']}, can_create_ad_account=True, is_disabled=False)
            if len(bms) < how_many_to_create:
                print(f"Not enough active BMs that could create {how_many_to_create} ad accounts")
            else:
                # bms = bms[:how_many_to_create]
                print(f"Active BMs that can create an ad account: {len(bms)}.")
                print(f"Creating ad accounts:")
                self.nooklz.create_ad_accounts(profile['id'], self.nooklz.get_business_ids_from_json(bms),name_pattern = "Djekxa", timezone="TZ_EUROPE_SOFIA")

    def link_bms(self, BM_limit : int = 30):
        profiles = self.nooklz.get_profiles(groups = {259151 : self.nooklz.groups[259151]}) # Ready to link
        for profile in profiles:
            self.nooklz.check_profiles(profile_ids={profile['id'] : profile['id']})
        # filter profiles which have not more BMs than BM_limit
        profiles = [profile for profile in profiles if len(profile["bms"]) <= BM_limit]
        print(f"Accepting invites for {len(profiles)} profiles, limit is {BM_limit}.")
        for profile in profiles:
            print(f"{BM_limit - len(profile['bms'])}, {len(profile['bms'])}")
            for n in range (BM_limit - len(profile["bms"])):
                bm_invites = self._eat_bm_invites(how_many=1, input_file=r"./BM_invites/djekxa.txt", output_file=r"./BM_invites/djekxa_used.txt")
                invite = self._parse_djekxa_invites(bm_invites[0])
                invite = invite["invite"]          
                print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} tries to accept invites:")
                print(bm_invites)
                self.nooklz.accept_bm_invites(profile_id=profile["id"], invite_links=[invite])
            
        # wait between account link        
        time_to_sleep = 30
        print(f"All invites accepted, sleeping {time_to_sleep}min.")
        for index in range(int(time_to_sleep/5)):
            print(f"{time_to_sleep - index * 5} min left to sleep.")
            time.sleep(60 * 5)