import os, calendar
import xml.etree.ElementTree as ET
import pandas as pd

from CSVSeperateA350 import *
from MPDA350 import *

class A350TextExtractor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.file_list = os.listdir(folder_path)
        self.data = []
    def extract_task_from_xml(self, file_contents):
        root = ET.fromstring(file_contents)
        
        # Extract issueDate
        issue_date = root.find(".//dmAddress/dmAddressItems/issueDate")
        day = issue_date.get("day")
        month = issue_date.get("month")
        year = issue_date.get("year")
        
        # Convert month number to month name
        month_name = calendar.month_abbr[int(month)]
        
        # Extract infoName
        info_name = root.find(".//dmAddress/dmAddressItems/dmTitle/infoName").text
        
        # Extract dmCode attributes
        dm_code = root.find(".//dmAddress/dmIdent/dmCode")
        
        # Construct AMM Code
        amm_code = (f"{dm_code.get('systemCode')}{dm_code.get('subSystemCode')}"
                    f"{dm_code.get('subSubSystemCode')}{dm_code.get('assyCode')}"
                    f"{dm_code.get('disassyCode')}{dm_code.get('infoCode')}")
        
        # Construct AMM Task
        amm_task = (f"{dm_code.get('modelIdentCode')}-{dm_code.get('systemDiffCode')}-"
                    f"{dm_code.get('systemCode')}-{dm_code.get('subSystemCode')}"
                    f"{dm_code.get('subSubSystemCode')}-{dm_code.get('assyCode')}-"
                    f"{dm_code.get('disassyCode')}{dm_code.get('disassyCodeVariant')}-"
                    f"{dm_code.get('infoCode')}{dm_code.get('infoCodeVariant')}-"
                    f"{dm_code.get('itemLocationCode')}")
        
        return info_name, f"{day} {month_name} {year}", amm_code, amm_task
    
    def extract_tool(self, file_contents):
        root = ET.fromstring(file_contents)
        support_equips = []

        for equip in root.findall(".//supportEquipDescr"):
            tool_number = equip.find("toolRef").get("toolNumber")
            part_description = equip.find("name").text
            quantity = equip.find("reqQuantity").text

            support_equips.append({
                "Tool Number": tool_number,
                "Part Description": part_description,
                "Qty": quantity
            })

        return support_equips

    def process_tool(self): #this function is to extract tool list only. 
        for file_name in self.file_list:
            file_path = os.path.join(self.folder_path, file_name)
            if file_name.endswith(".XML"):
                with open(file_path, "r") as file:
                    file_contents = file.read()
                    info_name, issue_date, amm_code, amm_task = self.extract_task_from_xml(file_contents)
                    support_equips = self.extract_tool(file_contents)

                    for equip in support_equips:
                        self.data.append({
                            "AMM Code": amm_code,
                            "AMM Task": amm_task,
                            "AMM Description": info_name,
                            "Task Revision": issue_date,
                            "Part Number": equip["Tool Number"],
                            "Part Description": equip["Part Description"],
                            "QTY": equip["Qty"]
                        })

    def process_task(self): #this function is to extract task list only.
        for file_name in self.file_list:
            file_path = os.path.join(self.folder_path, file_name)
            if file_name.endswith(".XML"):
                with open(file_path, "r") as file:
                    file_contents = file.read()
                    info_name, issue_date, amm_code, amm_task = self.extract_task_from_xml(file_contents)

                    self.data.append({
                        "AMM Code": amm_code,
                        "AMM Task": amm_task,
                        "AMM Description": info_name,
                        "Task Revision": issue_date,
                    })


    # def create_dataframe(self):
    #     # df = pd.DataFrame(self.data)
    #     # df.drop_duplicates(subset='AMM Task', keep='first', inplace=True)
    #     # return df
    #     return pd.DataFrame(self.data)

    def create_dataframe(self):
        if not self.data:  # Check if data is empty
            return pd.DataFrame(columns=['AMM Code', 'AMM Task', 'AMM Description', 'Task Revision', 'Part Number', 'QTY', 'Part Description'])
        return pd.DataFrame(self.data)

#this function to test extract task list only. It can be deleted. 
def main():
    folder_path = "/Users/win/Desktop/temp_file_py/UI_A330_320_330_Updated/MP"  # Replace with your actual folder path
    extract_task = A350TextExtractor(folder_path)
    extract_task.process_task()
    task_list = extract_task.create_dataframe()
    print(task_list.head(5))
    # task_list.to_csv("task_list.csv", index=False)
    extract_task.process_tool()
    tool_list = extract_task.create_dataframe()
    tool_list = CSVseperateA350().create_tool_list_csv(tool_list)
    # tool_list.to_csv("tool_list_num.csv", index=False)
    print(tool_list.head(5))
    
    # processor = MPDA350('MPD_a350_copy.csv') ##it is accurate 
    # processor.save_to_csv('mpd_update.csv')
   
    # mpd = processor.mpd_file() #this will give mpd_l0

    # mpd.to_csv('mpd_update_ammcode.csv', index=False)

    


   

if __name__ == "__main__":
    main()