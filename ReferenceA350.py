import xml.etree.ElementTree as ET
import calendar
import os
import pandas as pd

class A350Reference:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.file_list = os.listdir(folder_path) #list of files in the folder
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
        
        # Extract infoName (Parent AMM Description)
        info_name = root.find(".//dmAddress/dmAddressItems/dmTitle/infoName").text
        
        # Extract dmCode attributes
        dm_code = root.find(".//dmAddress/dmIdent/dmCode")
        
        # Construct AMM Code
        amm_code = (f"{dm_code.get('systemCode')}{dm_code.get('subSystemCode')}"
                    f"{dm_code.get('subSubSystemCode')}{dm_code.get('assyCode')}"
                    f"{dm_code.get('disassyCode')}{dm_code.get('infoCode')}")
        
        # Construct AMM Task (Parent AMM)
        amm_task = (f"{dm_code.get('modelIdentCode')}-{dm_code.get('systemDiffCode')}-"
                    f"{dm_code.get('systemCode')}-{dm_code.get('subSystemCode')}"
                    f"{dm_code.get('subSubSystemCode')}-{dm_code.get('assyCode')}-"
                    f"{dm_code.get('disassyCode')}{dm_code.get('disassyCodeVariant')}-"
                    f"{dm_code.get('infoCode')}{dm_code.get('infoCodeVariant')}-"
                    f"{dm_code.get('itemLocationCode')}")
        
        return info_name, f"{day} {month_name} {year}", amm_code, amm_task

    def extract_reference_info(self, file_contents):
        root = ET.fromstring(file_contents)
        references = []
        
        # Find all dmRef elements
        dm_refs = root.findall(".//refs/dmRef")
        
        for dm_ref in dm_refs:
            ref_dm_code = dm_ref.find("./dmRefIdent/dmCode")
            
            if ref_dm_code is not None:
                # Construct Reference AMM
                reference_amm = (f"{ref_dm_code.get('modelIdentCode')}-{ref_dm_code.get('systemDiffCode')}-"
                                f"{ref_dm_code.get('systemCode')}-{ref_dm_code.get('subSystemCode')}"
                                f"{ref_dm_code.get('subSubSystemCode')}-{ref_dm_code.get('assyCode')}-"
                                f"{ref_dm_code.get('disassyCode')}{ref_dm_code.get('disassyCodeVariant')}-"
                                f"{ref_dm_code.get('infoCode')}{ref_dm_code.get('infoCodeVariant')}-"
                                f"{ref_dm_code.get('itemLocationCode')}")
                
                # Construct Reference AMM Code
                reference_amm_code = (f"{ref_dm_code.get('systemCode')}{ref_dm_code.get('subSystemCode')}"
                                    f"{ref_dm_code.get('subSubSystemCode')}{ref_dm_code.get('assyCode')}"
                                    f"{ref_dm_code.get('disassyCode')}{ref_dm_code.get('infoCode')}")
                
                # Extract Reference AMM Description
                reference_amm_description = dm_ref.find("./dmRefAddressItems/dmTitle/infoName").text
                
                references.append({
                    "Reference AMM": reference_amm,
                    "Reference AMM Description": reference_amm_description,
                    "Reference AMM Code": reference_amm_code
                })
        
        return references

    def process_files(self):
        for file_name in self.file_list: #iterate through the list of files
            file_path = os.path.join(self.folder_path, file_name)
            if file_name.endswith(".XML"): #check if the file is an XML file or not. change the extension to the file type you are working with
                with open(file_path, "r") as file:
                    file_contents = file.read()
                    info_name, issue_date, amm_code, amm_task = self.extract_task_from_xml(file_contents)
                    references = self.extract_reference_info(file_contents)

                    if not references:
                        # If there are no references, add one row with empty reference fields
                        self.add_data_row(amm_task, info_name, amm_code, issue_date, {})
                    else:
                        # If there are references, add a row for each reference
                        for ref in references:
                            self.add_data_row(amm_task, info_name, amm_code, issue_date, ref)

    def add_data_row(self, amm_task, info_name, amm_code, issue_date, reference):
        self.data.append({
            "Parent AMM(n)": amm_task,
            "Parent AMM Description": info_name,
            "Parent AMM Code": amm_code,
            "Reference AMM(n+1)": reference.get("Reference AMM", ""),
            "Reference AMM Description": reference.get("Reference AMM Description", ""),
            "Reference AMM Code": reference.get("Reference AMM Code", ""),
        })
    def create_dataframe(self):
        df = pd.DataFrame(self.data)
        
        # Remove rows where Reference AMM(n+1) is empty
        df = df[df['Reference AMM(n+1)'] != ""]
        # Identify duplicates based on both Parent AMM(n) and Reference AMM(n+1)
        duplicates = df.duplicated(subset=['Parent AMM(n)', 'Reference AMM(n+1)'], keep=False)
        # Keep rows that are either not duplicated or where Parent AMM(n) or Reference AMM(n+1) is unique
        df = df[~duplicates | ~df.duplicated(subset='Parent AMM(n)', keep=False) | ~df.duplicated(subset='Reference AMM(n+1)', keep=False)]
        return df
    
    def filter_dataframe(self, df):
    # Initial filtering to remove rows where Parent AMM Code equals Reference AMM Code
        df_filtered = df[df['Parent AMM Code'] != df['Reference AMM Code']]
        
        return df_filtered #return the filtered dataframe for lv1 processing

# Usage
#This main function is used to text the code and see if the output is correct or not. This can be deleted. 
def main():
    processor = A350Reference("/Users/win/Desktop/temp_file_py/A350/MP") #change the path to the folder where the XML files are stored
    processor.process_files()
    result_df = processor.create_dataframe()
    # result_df.to_csv("reference_l0.csv", index=False)
    level_1 = processor.filter_dataframe(result_df)
    level_1.to_csv("reference_v1_l1_new_v2.csv", index=False)
    # print(level_1.head(5))
    

    print("completed")


if __name__ == "__main__":
    main()