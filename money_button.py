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

    def __eat_bm_invites(self, how_many : int, input_file : str = r"BM_invites.txt", output_file : str = r"UsedBM_invites.txt"):
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
    
    def __write_debug_json(self, json_code, file_path : str = "output.json"):
        # Write JSON data to a file with UTF-8 encoding
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json_code, file, indent=4, ensure_ascii=False)

    def __remove_tags(self, text : str):
        return re.sub(r'<.*?>', '', text)

    def __write_cleaned_invites(self, result_with_tags : str, file : str = "./BM_invites/trash_invites.txt"):
        with open(file, "a", encoding="utf-8") as f:
            f.write(self.__remove_tags(result_with_tags) +"\n")

    def _update_profiles(self, group_id : int = 259151): # 259151 Ready to link
        profiles = self.nooklz.get_profiles(groups = {group_id : self.nooklz.groups[group_id]})
        print("Updating profiles:")
        for profile in profiles:
            self.nooklz.check_profiles(profile_ids={profile['id'] : profile['id']})
        return profiles