import re
import pandas as pd
from datetime import datetime

class XMLProcessor: #this class is for extracting task list only. This returns a dataframe. Then, use CSVseperate.py to get tool list
    def __init__(self, input_file):
        self.input_file = input_file
        # self.output_file = output_file
        self.scope_text = r'(<PARA>Fixtures, Tools, Test and Support Equipment</PARA><TABLE>.*?</TABLE>)'
        self.text_replacements = {
            "<ROW>": "\n<ROW>",
            "<PARA>": "\n<PARA>",
            "<TABLE>": "\n<TABLE>",
            "<L1ITEM>": "\n<L1ITEM>"
        }

    def read_and_task_file(self):
        try:
            with open(self.input_file, 'r') as file:
                content = file.read()
                modified_content = re.sub(r'<TASK\s+CHAPNBR="(\d+)"', r'\n<TASKCHAPNBR="\1"', content)
            return modified_content
        except Exception as e:
            print(e)
            return None

    def keep_only_taskchapnbr_tables(self, text):
        pattern = r'(<TASKCHAPNBR.*?</TABLE></L1ITEM>)'
        matches = re.findall(pattern, text, flags=re.DOTALL)
        if matches:
            text = '\n'.join(matches)
            text = re.sub(r'(<TASKCHAPNBR)', r'\n\1', text) 
        return text

    def replace_row(self, match):
        text = match.group()
        text = text.replace("<PARA>Fixtures","\n<PARA>Fixtures")
        for old, new in self.text_replacements.items():
            text = text.replace(old, new)
        text = text.replace("<TASKCHAPNBR", "\n<TASKCHAPNBR")
        text = self.add_newline_at_effect(text)
        return text

    def add_newline_at_effect(self, text):
        pattern = r'(<EFFECT)'
        return re.sub(pattern, r'\n\1', text)

    def remove_revend_tags(self, text):
        pattern = re.compile(r'(<ROW><ENTRY COLNAME="COL1">\s*<PARA>.*?</PARA></ENTRY>)(<REVEND>)?(<ENTRY COLNAME="COL3">\s*<PARA>.*?<TOR><TORVALUE MAX="[\d.]+" MIN="[\d.]+" UNIT="[^"]+"><TORVALUE MAX="[\d.]+" MIN="[\d.]+" UNIT="[^"]+"></TOR></PARA></ENTRY>)(<REVEND>)?(</ROW>)(<REVEND>)*', re.DOTALL)
        replacement = r'\1\3\5'
        return pattern.sub(replacement, text)

    def delete_specific_tables(self, text):
        patterns = [
            r'<TASKCHAPNBR="70".*?<TITLE>Consumable Products for Engine</TITLE>.*?</PARA></ENTRY></ROW><REVEND></TBODY></TGROUP></TABLE></L1ITEM>',
            r'<TASKCHAPNBR="70".*?<TITLE>Vendor Code, Name and Address</TITLE>.*?</TABLE></L2ITEM></LIST2></L1ITEM></LIST1></SUBTASK></TOPIC></TASK>',
            r'<PARA>Work Zones and Access Panels</PARA><TABLE>.*?</TABLE>',
            r'<PARA><REVST>Work Zones and Access Panels.*?</L1ITEM>',
            r'<PARA><REVST>Consumable Materials<REVEND></PARA><TABLE>.*?</TABLE>',
            r'<TITLE>Procedure</TITLE>.*?(?=<TASKCHAPNBR)',
            r'<PARA>Consumable Materials</PARA><TABLE>.*?</TABLE>',
            r'<PARA><REVST>Consumable Materials<REVEND></PARA><REVST><TABLE>.*?</TABLE>',
            r'<PARA>Referenced Information</PARA><TABLE>.*?</TABLE>',
            r'<L1ITEM><PARA>Expendable Parts</PARA><TABLE>.*?</TABLE></L1ITEM>',
            r'<ENTRY COLNAME="COL1">\s*<PARA>REFERENCE</PARA>\s*</ENTRY>',
            r'<ROW><ENTRY COLNAME="COL2"><PARA><REVST>QTY<REVEND></PARA></ENTRY><REVST><REVEND></ROW>',
            r'<ENTRY COLNAME="COL3">\s*<PARA>DESIGNATION</PARA>\s*</ENTRY>',
            r'<ENTRY SPANNAME="WHOLE">.*?</ENTRY>',
            r'<PARA><REVST>QTY<REVEND></PARA>',
            r'<PARA>QTY</PARA>',
            r'<ENTRY COLNAME="COL2">\s*<PARA>QTY</PARA>\s*</ENTRY>',
            r'<ROW><ENTRY COLNAME="COL2"><PARA><REVST>QTY<REVEND></PARA></ENTRY><REVST><REVEND></ROW>',
            r'<THEAD><ROW><ENTRY COLNAME="COL2"></ENTRY></ROW></THEAD>',
            r'<COLSPEC COLNAME="COL1" COLWIDTH="22\*"><COLSPEC COLNAME="COL2" COLWIDTH="4\*"><COLSPEC COLNAME="COL3" COLWIDTH="53\*"><SPANSPEC NAMEEND="COL3" NAMEST="COL1" SPANNAME="WHOLE"><THEAD>\n<ROW><ENTRY COLNAME="COL2">\n</ENTRY></ROW></THEAD>',
            r'<ROW><ENTRY SPANNAME="WHOLE">\s*<PARA>.*?<EIN TYPE="EXACT">.*?</EIN>.*?</PARA>\s*</ENTRY></ROW>',
            r'<REVST>\s*<EFFECT EFFRG="[\d\s]+"></EFFECT><REVEND><ENTRY SPANNAME="WHOLE">\s*<PARA>.*?<EIN TYPE="EXACT">.*?</EIN>.*?</PARA></ENTRY></ROW>\s*(?:<ROW>)?<REVST>\s*<EFFECT EFFRG="[\d\s]+"></EFFECT><REVEND>',
            r'<REVST>\s*<EFFECT EFFRG="[\d\s]+"></EFFECT><REVEND>(?:</ROW>)?\s*(?:<ROW>)?',
            r'<REVST>\s*<ROW>\s*<EFFECT EFFRG="[\d\s]+"></EFFECT><ENTRY COLNAME="COL1">.*?</ENTRY></ROW>',
            r'<REVST>\s*(?:<ROW>)?\s*'
        ]
        for pattern in patterns:
            # if pattern.startswith(r'(<TITLE>Procedure</TITLE>'):
            # # For the Procedure pattern, we want to keep the content before the table
            #     text = re.sub(pattern, r'\1', text, flags=re.DOTALL)
            # else:
                # text = re.sub(pattern, '', text, flags=re.DOTALL)
            text = re.sub(pattern, '', text, flags=re.DOTALL)
        text = self.remove_revend_tags(text)
        return text

    def replace_revst_effect(self, match):
        text = match.group(0)
        text = re.sub(r'<REVST>\s*<EFFECT EFFRG="[\d\s]+"></EFFECT><REVEND>', '<ROW>', text)
        text = re.sub(r'<EFFECT EFFRG="[\d\s]+"></EFFECT>', '<ROW>', text)
        text = re.sub(r'</ROW>\s*<ROW>\s*<ROW>', '</ROW>\n<ROW>', text)
        return text

    def read_and_modify_file(self):
        try:
            content_task = self.keep_only_taskchapnbr_tables(self.read_and_task_file())
            pattern = r'(<TASKCHAPNBR.*?</TABLE></L1ITEM>)'
            content = re.sub(pattern, self.replace_revst_effect, content_task, flags=re.DOTALL)
            pattern = r'({})'.format(self.scope_text)
            modified_content = re.sub(pattern, self.replace_row, content, flags=re.DOTALL)
            modified_content = self.delete_specific_tables(modified_content)
            add_zero = self.replace_zero(modified_content)

            # for testing txt
            # with open('testingZero_1.txt', 'w') as file:
            #          file.write(add_zero)


            return add_zero
        except Exception as e:
            print(e)
            return None

    def replace_zero(self, input):
        # First, remove <REVEND> in the specified format
        revend_pattern = re.compile(r'(<ROW><ENTRY COLNAME="COL1">\n<PARA>.*?</PARA></ENTRY>)<REVEND>(<ENTRY COLNAME="COL3">)')
        input = revend_pattern.sub(r'\1\2', input)
        
        # Then perform the original replacement
        pattern1 = re.compile(r'(<ENTRY COLNAME="COL1">\n<PARA>(.*?)</PARA></ENTRY>)(<ENTRY COLNAME="COL3">)')
        add_zero1 = r'\1<ENTRY COLNAME="COL2">\n<PARA>0</PARA></ENTRY>\3'
        text1 = pattern1.sub(add_zero1, input)
        
        return text1

    @staticmethod
    def format_revdate(revdate):
        date_obj = datetime.strptime(revdate, '%Y%m%d')
        return date_obj.strftime('%d-%b-%Y')

    @staticmethod
    def extract_first_title(text):
        match = re.search(r'<TITLE>(.*?)</TITLE>', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    #this function combines all the functions above to extract the data from the input file and return as dataframe
    def process_file(self):
        try:
            input_file = self.read_and_modify_file()
            tasks = re.split(r'<TASKCHAPNBR=', input_file)[1:]
            csv_data = []

            for task in tasks:
                key_match = re.search(r'KEY="([^"]+)"', task)
                confltr_match = re.search(r'CONFLTR="([^"]+)"', task)
                varnbr_match = re.search(r'VARNBR="([^"]+)"', task)
                sectnbr_match = re.search(r'SECTNBR="([^"]+)"', task)
                func_match = re.search(r'FUNC="([^"]+)"', task)
                seq_match = re.search(r'SEQ="([^"]+)"', task)
                subjnbr_match = re.search(r'SUBJNBR="([^"]+)"', task)
                revdate_match = re.search(r'REVDATE="([^"]+)"', task)
                taskchapnbr_match = re.search(r'^"(\d+)"', task)
                pgblknbr_match = re.search(r'PGBLKNBR="([^"]+)"', task)
                
                if (key_match and confltr_match and sectnbr_match and func_match and seq_match and 
                    subjnbr_match and revdate_match and taskchapnbr_match and pgblknbr_match):
                    key = key_match.group(1)[2:-12]
                    confltr = confltr_match.group(1)
                    sectnbr = sectnbr_match.group(1)
                    func = func_match.group(1)
                    seq = seq_match.group(1)
                    subjnbr = subjnbr_match.group(1)
                    revdate = revdate_match.group(1)
                    taskchapnbr = taskchapnbr_match.group(1)
                    pgblknbr = pgblknbr_match.group(1)
                    formatted_revdate = self.format_revdate(revdate)

                    modified_key = f"{key}-{sectnbr}-{subjnbr}-{func}-{seq}-{confltr}"
                    page_block = f"{taskchapnbr}-{sectnbr}-{subjnbr}-{pgblknbr}"

                    if varnbr_match:
                        varnbr = varnbr_match.group(1)
                        modified_key = f"{modified_key}{varnbr}"
                    
                    description = self.extract_first_title(task)

                    if '<TABLE>' not in task:
                        csv_data.append([page_block, modified_key, description, formatted_revdate, '', 'N/A', ''])
                        continue

                    tables = re.findall(r'<TABLE>.*?</TABLE>', task, re.DOTALL)

                    for table in tables:
                        if "<PARA>Fixtures, Tools, Test and Support Equipment</PARA>" in table:
                            continue

                        # rows = re.findall(r'<ROW>(.*?)</ROW>', table, re.DOTALL)
                        rows = re.findall(r'<ENTRY.*?</ENTRY>.*?<ENTRY.*?</ENTRY>.*?<ENTRY.*?</ENTRY>', table, re.DOTALL)
                        for row in rows:
                            entries = re.findall(r'<ENTRY.*?>(.*?)</ENTRY>', row, re.DOTALL)
                            if len(entries) == 3:
                                row_data = [page_block, modified_key, description, formatted_revdate]
                                for i, entry in enumerate(entries):
                                    para_content = re.search(r'<PARA>(.*?)</PARA>', entry)
                                    if para_content:
                                        content = para_content.group(1)
                                        # if i == 2:  # Special handling for the third entry
                                        content = re.sub(r'<TOR><TORVALUE MAX="(.*?)" MIN="(.*?)" UNIT="(.*?)"><TORVALUE MAX="(.*?)" MIN="(.*?)" UNIT="(.*?)">', r"Torque wrench: range between \2 and \1 \3 (\6 and \5 \4)", content)
                                        content_without_tags = re.sub(r'<.*?>', '', content)
                                        row_data.append(content_without_tags.strip())
                                    else:
                                        # row_data.append("None")
                                        # If no <PARA> tag is found, read the next entry
                                        if i + 1 < len(entries):
                                            i += 1
                                            entry = entries[i]
                                        else:
                                            # If there are no more entries, break the loop
                                            row_data.append("None")

                                csv_data.append(row_data[:7])
            # Create DataFrame instead of writing to CSV
            df = pd.DataFrame(csv_data, columns=['Page_Block', 'AMM Task', 'AMM Description', 'Task Revision', 'Part Number', 'QTY', 'Part Description'])
            return df

        except Exception as e:
            print(e)
            return None

def main():
    input_file = "AMM_330.SGM"
    processor = XMLProcessor(input_file)
    processor.read_and_modify_file()


if __name__ == "__main__":
    main()
    