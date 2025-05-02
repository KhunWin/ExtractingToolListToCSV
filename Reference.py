
import re
import pandas as pd
from UpdateLevelZero import *
from UpdateMPD import *

class ReferenceProcessor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.content = ""
        self.formatted_content = ""

    def read_file(self):
        with open(self.input_file, 'r') as file:
            self.content = file.read()

    def modify_content(self):
        self.content = self.content.replace("<PARA>Referenced Information", "\n<PARA>Referenced Information")
        self.content = self.content.replace("<TASK", "\n<TASKCHAPNBR")

    def extract_content(self):
        pattern = r'(<TASKCHAPNBR.*?</TITLE>).*?(<PARA>Referenced Information</PARA><TABLE>.*?</TABLE></L1ITEM>)'
        return re.findall(pattern, self.content, re.DOTALL)

    @staticmethod
    def format_content(content):
        content = content.replace("<ROW>", "\n<ROW>")
        content = content.replace("<PARA>", "\n<PARA>")
        content = content.replace("<TABLE>", "\n<TABLE>")
        content = content.replace("<TASKCHAPNBR", "\n\n<TASKCHAPNBR")
        return content

    @staticmethod
    def clean_table(table_content):
        table_content = re.sub(r'<THEAD>.*?</THEAD>', '', table_content, flags=re.DOTALL)
        table_content = re.sub(r'<ROW><ENTRY SPANNAME="WHOLE">.*?</ROW>', '', table_content, flags=re.DOTALL)
        table_content = re.sub(r'<PARA><REFEXT REFLOC.*?</PARA></ENTRY></ROW>', '', table_content, flags=re.DOTALL)
        return table_content

    @staticmethod #this one is removing the hyphen between the digit and the letter from the end 
    def remove_hyphen_if_needed(reference):
        # Check if the last two characters are digits
        if re.match(r".*[A-Z]-\d\d$", reference):
            # Find the last hyphen before the last two digits and remove it
            return re.sub(r'-(\d\d)$', r'\1', reference)
        return reference
    
    #this function is for adding new lines and removing unnecessary texts from the files
    def process(self):
        sections = self.extract_content()
        
        self.formatted_content = ""
        for i, (header, ref_info) in enumerate(sections, 1):
            formatted_header = self.format_content(header)
            ref_info_without_header = self.clean_table(ref_info)
            formatted_ref_info = self.format_content(ref_info_without_header)
            self.formatted_content += f"{formatted_header}\n{formatted_ref_info}"

        return self.formatted_content

    def initial_processing(self):
        self.read_file()
        self.modify_content()
        return self.content
    
    @staticmethod
    def extract_first_title(text):
        match = re.search(r'<TITLE>(.*?)</TITLE>', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    @staticmethod
    def clean_tags(text):
        text = re.sub(r'<REFINT[^>]*>(.*?)</REFINT>', r'\1', text)
        text = re.sub(r'<REVST>(.*?)<REVEND>', r'\1', text)
        text = re.sub(r'</?REVST>|</?REVEND>', '', text)
        return text.strip()

    #this function needs to run after the process function
    def process_file(self, content):
        tasks = re.split(r'<TASKCHAPNBR', content)[1:]

        data_reference = []

        for task in tasks:
            key_match = re.search(r'KEY="([^"]+)"', task)
            confltr_match = re.search(r'CONFLTR="([^"]+)"', task)
            varnbr_match = re.search(r'VARNBR="([^"]+)"', task)
            sectnbr_match = re.search(r'SECTNBR="([^"]+)"', task)
            func_match = re.search(r'FUNC="([^"]+)"', task)
            seq_match = re.search(r'SEQ="([^"]+)"', task)
            subjnbr_match = re.search(r'SUBJNBR="([^"]+)"', task)
            
            if all([key_match, confltr_match, sectnbr_match, func_match, seq_match, subjnbr_match]):
                key = key_match.group(1)[2:-12]
                confltr = confltr_match.group(1)
                sectnbr = sectnbr_match.group(1)
                func = func_match.group(1)
                seq = seq_match.group(1)
                subjnbr = subjnbr_match.group(1)

                modified_key = f"{key}-{sectnbr}-{subjnbr}-{func}-{seq}-{confltr}"

                if varnbr_match:
                    varnbr = varnbr_match.group(1)
                    modified_key = f"{modified_key}{varnbr}"
                
                description = self.extract_first_title(task)

                table_match = re.search(r'<PARA>Referenced Information</PARA>\s*<TABLE>(.*?)</TABLE>', task, re.DOTALL)
                if table_match:
                    table = table_match.group(1)
                    rows = re.findall(r'<ROW>(.*?)</ROW>', table, re.DOTALL)
                    for row in rows:
                        col1_match = re.search(r'<ENTRY COLNAME="COL1">\s*<PARA>(.*?)</PARA>\s*</ENTRY>', row, re.DOTALL)
                        col2_match = re.search(r'<ENTRY COLNAME="COL2">\s*<PARA>(.*?)</PARA>\s*</ENTRY>', row, re.DOTALL)
                        if col1_match and col2_match:
                            col1 = self.clean_tags(col1_match.group(1))
                            col2 = self.clean_tags(col2_match.group(1))
                            col1 = self.remove_hyphen_if_needed(col1)

                            data_reference.append([modified_key, description, col1, col2])
        
        df = pd.DataFrame(data_reference, columns=['Parent AMM(n)', 'Parent AMM Description', 'Reference AMM(n+1)', 'Reference AMM Description']) #this columns can be modified without any problem
        return df

#this main function is only for testing reference list. It can be deleted.
def main():

    #get the reference file
    initial_processor = ReferenceProcessor("amm.sgm")
    initial_processor.initial_processing()
    
    processed_content = initial_processor.process()
    data_reference = initial_processor.process_file(processed_content)
    
    #get updated mpd file
    mpd = MPDProcessor('MPD.csv').save_to_dataframe()

    #update level zero, the reference file
    data_reference['FC'] = ''
    data_reference['FH'] = ''
    data_reference['MO'] = ''
    data_reference['NOTE'] = ''
    data_reference['Involved_MPD'] = ''

    data_reference['AMM_ref'] = data_reference['Parent AMM(n)'].str[:16]
    reference_update = LevelZeroUpdate(mpd, data_reference).update_level_zero()
    # tool_update = LevelZeroUpdate(mpd, data_reference).update_reference()
    # reference_update = ReferenceUpdate(mpd, data_reference).update_row()

    #end of reference list
    reference_update.drop(columns=['AMM_ref'], inplace=True) #do this at the end
    reference_update.to_csv('update_reference_csv_newcol.csv', index=False)
    print(reference_update.head())

if __name__ == "__main__":
    main()






