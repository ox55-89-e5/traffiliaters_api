from nooklz_api import NooklzInterface
from money_button import MoneyButton
import time
import json
import requests
import os
from facebook_api import disable_reason


class SecretMoneyButton(MoneyButton):
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
                    self.__write_cleaned_invites(f'{{"link":"{result}", "business_id":{bm["business_id"]}, "nooklz_profile_id": {profile["id"]}}}', file = "./BM_invites/Internal.txt")

        # Accept invites
        print("Accepting invites:")
        profiles = self.nooklz.get_profiles(groups = {259151 : self.nooklz.groups[259151]}) # Ready to link
        # filter profiles which have not more BMs than BM_limit
        profiles = [profile for profile in profiles if len(profile["bms"]) <= BM_limit]
        print(f"Accepting invites for {len(profiles)} profiles, limit is {BM_limit}.")
        for profile in profiles:
            print(f"{BM_limit - len(profile['bms'])}, {len(profile['bms'])}")
            for n in range (BM_limit - len(profile["bms"])):
                bm_invites = self.__eat_bm_invites(how_many=1, input_file=r"./BM_invites/Internal.txt", output_file=r"./BM_invites/Internal_used.txt")
                if bm_invites == None:
                    break 
                bm_invite = json.loads(bm_invites[0])["link"]
                print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} tries to accept invites:")
                print(bm_invite)
                self.nooklz.accept_bm_invites(profile_id=profile["id"], invite_links=[bm_invite])

        # Leave business managers
        print("Leaving BMs:")
        bm_invites = self.__eat_bm_invites(how_many=1, input_file=r"./BM_invites/Internal_used.txt", output_file=r"./BM_invites/Internal_released.txt")
        while bm_invites != None:
            invite_json = json.loads(bm_invites[0])
            self.nooklz.leave_bms(profile_id=invite_json["nooklz_profile_id"], bm_ids=[invite_json["business_id"]])
            bm_invites = self.__eat_bm_invites(how_many=1, input_file=r"./BM_invites/Internal_used.txt", output_file=r"./BM_invites/Internal_released.txt")

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
                    self.__write_cleaned_invites(result)

        # Accept invites
        print("Accepting invites:")
        profile = self._update_profiles(group_id=259225) # BM Trash 259225
        trash_bm_invites = self.__eat_bm_invites(how_many=1, input_file=r"./BM_invites/trash_invites.txt", output_file=r"./BM_invites/trash_invites_used.txt")
        while trash_bm_invites != None:
            print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} tries to accept invites:")
            print(trash_bm_invites)
            self.nooklz.accept_bm_invites(profile_id=profile["id"], invite_links=trash_bm_invites)
            trash_bm_invites = self.__eat_bm_invites(how_many=1, input_file=r"./BM_invites/trash_invites.txt", output_file=r"./BM_invites/trash_invites_used.txt")
            
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
        profiles = self._update_profiles(258598) #258598 money button
        # profiles = self._update_profiles() #258598 money 

        # filter profiles which have not more BMs than BM_limit
        profiles = [profile for profile in profiles if len(profile["bms"]) <= BM_limit]
        for profile in profiles:
            bm_invites = self.__eat_bm_invites(how_many=1, input_file=r"./BM_invites/djekxa.txt", output_file=r"./BM_invites/djekxa_used.txt")       
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
                self.nooklz.create_ad_accounts(profile['id'], [bms[0]['business_id']], "Premiumpro arm")

    def link_bms(self, BM_limit : int = 20):
        profiles = self.nooklz.get_profiles(groups = {259151 : self.nooklz.groups[259151]}) # Ready to link
        for profile in profiles:
            self.nooklz.check_profiles(profile_ids={profile['id'] : profile['id']})
        # filter profiles which have not more BMs than BM_limit
        profiles = [profile for profile in profiles if len(profile["bms"]) <= BM_limit]
        print(f"Accepting invites for {len(profiles)} profiles, limit is {BM_limit}.")
        for profile in profiles:
            print(f"{BM_limit - len(profile['bms'])}, {len(profile['bms'])}")
            for n in range (BM_limit - len(profile["bms"])):
                bm_invites = self.__eat_bm_invites(how_many=1, input_file=r"./BM_invites/djekxa.txt", output_file=r"./BM_invites/djekxa_used.txt")       
                print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} tries to accept invites:")
                print(bm_invites)
                self.nooklz.accept_bm_invites(profile_id=profile["id"], invite_links=bm_invites)
            
        # wait between account link        
        time_to_sleep = 30
        print(f"All invites accepted, sleeping {time_to_sleep}min.")
        for index in range(int(time_to_sleep/5)):
            print(f"{time_to_sleep - index * 5} min left to sleep.")
            time.sleep(60 * 5)
                
            
        for profile in profiles:
            print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} trying to check profile:")
            self.nooklz.check_profiles(profile_ids={profile['id'] : profile['id']})              
                        
            print(f"facebook profile: {profile['account_name']} profile id: {profile['id']} searching for a BM to creat ad account:")    
            bms = self.nooklz.get_bms(nooklz_profile_ids={profile['id'] : profile['id']}, can_create_ad_account=True, is_disabled=False)
            if len(bms) < 1:
                print(f"Not enough active BMs that could create an ad account")
            else:
                print(f"Actives BMs that can create an ad account: {len(bms)}.")
                print(f"Creating ad accounts:")
                self.nooklz.create_ad_accounts(profile['id'], self.nooklz.get_business_ids_from_json(bms), "Djekxa")