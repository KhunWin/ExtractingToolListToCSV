
import re
class FileProcessorTool:
    def __init__(self, text_processor):
        self.text_processor = text_processor

    def read_and_task_file(self, input_file_path): #modifying code format of the AMM file
        try:
            with open(input_file_path, 'r') as file:
                content = file.read()
            return re.sub(r'<TASK\s+CHAPNBR="(\d+)"', r'\n<TASKCHAPNBR="\1"', content)
        except Exception as e:
            print(e)
            return None

    def read_and_modify_file(self, input_file_path):
        try:
            content_task = self.text_processor.keep_only_taskchapnbr_tables(input_file_path)
            pattern = r'(<TASKCHAPNBR.*?</TABLE></L1ITEM>)'
            content = re.sub(pattern, self.text_processor.replace_revst_effect, content_task, flags=re.DOTALL)
            pattern = r'({})'.format(self.text_processor.scope_text)
            modified_content = re.sub(pattern, self.text_processor.replace_row, content, flags=re.DOTALL)
            modified_content = self.text_processor.delete_specific_tables(modified_content)
            return self.text_processor.replace_zero(modified_content)
        except Exception as e:
            print(e)
            return None