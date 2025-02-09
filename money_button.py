import json
from nooklz_api import NooklzInterface
import re

class MoneyButton:
    def __init__(self, NooklzInterface : NooklzInterface):
        self.nooklz = NooklzInterface

    def export_extra_bms(self, BM_limit : int = 20):
        pass
    
    def export_trash_bms(self):
        pass

    def test_bms(self, BM_limit : int = 20):
        pass

    def link_bms(self, BM_limit : int = 20):
        pass

    def _extract_ad_account_ids(self, data):#returns a dictionary with {bm_id :[act_id, act_id2], bm_id2 : [act_id3]} pattern
        business_ad_account_dict = {}
        # Regular expression to find business ID and ad account IDs in both Ukrainian and English versions
        pattern = r"(Bm:(\d+)).*(?:Створено рекламний акаунт:|Created ad account:)\s*(\d+)"
        try:
            # Iterate over each entry in the data
            for entry in data:
                match = re.search(pattern, entry)               
                if match:
                    business_id = match.group(2)  # Extract the business ID
                    ad_account_id = match.group(3)  # Extract the ad account ID                
                    # If the business ID already exists in the dictionary, append the ad account ID
                    if business_id in business_ad_account_dict:
                        business_ad_account_dict[business_id].append(ad_account_id)
                    else:
                        # Otherwise, create a new list for this business ID
                        business_ad_account_dict[business_id] = [ad_account_id]    
            return business_ad_account_dict
        except Exception as e:
            print(f"Error: {e}")
            return None

    def __extract_ad_account_id_list(self, data):
        ad_account_ids = []
        # Regular expression to find ad account IDs in both Ukrainian and English versions
        pattern = r"(?:Створено рекламний акаунт:|Ad account created:)\s*(\d+)"  
        try:
            # Iterate over each entry in the data
            for entry in data:
                match = re.search(pattern, entry)   
                if match:
                    ad_account_ids.append(match.group(1))  # Add the extracted ID to the list                 
            return ad_account_ids
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _parse_djekxa_invites(self, invite_string):
        try:
            pattern = r"(.+)\|business_id=(\d+)"
            match = re.match(pattern, invite_string)
            if not match:
                raise ValueError("Invalid input format")
            return {"invite": match.group(1), "business_id": match.group(2)}
        except Exception as e:
            print(f"Error: {e}")

    def __parse_djekxa_invites_regex(self, invite_string : str):
        try:
            # Regex pattern to match 'invite' and 'business_id'
            pattern = r"(.+)\|business_id=(\d+)"
            match = re.match(pattern, invite_string)
            if not match:
                raise ValueError("Invalid input format")  # Raise an exception if format is incorrect
            # Extract values
            invite = match.group(1)
            business_id = match.group(2)
            return {"invite": invite, "business_id": business_id}
        except Exception as e:
            print(f"Error: {e}")

    def _eat_bm_invites(self, how_many : int, input_file : str = r"BM_invites.txt", output_file : str = r"UsedBM_invites.txt"):
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
                return None

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
    
    def _write_debug_json(self, json_code, file_path : str = "output.json"):
        # Write JSON data to a file with UTF-8 encoding
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json_code, file, indent=4, ensure_ascii=False)

    def __remove_tags(self, text : str):
        return re.sub(r'<.*?>', '', text)

    def _write_cleaned_invites(self, result_with_tags : str, file : str = "./BM_invites/trash_invites.txt"):
        with open(file, "a", encoding="utf-8") as f:
            f.write(self.__remove_tags(result_with_tags) +"\n")

    def _update_profiles(self, group_id : int = 259151): # 259151 Ready to link
        profiles = self.nooklz.get_profiles(groups = {group_id : self.nooklz.groups[group_id]})
        print("Updating profiles:")
        self.nooklz.check_profiles(profile_ids=self.nooklz.get_ids_from_json(profiles))
        return profiles