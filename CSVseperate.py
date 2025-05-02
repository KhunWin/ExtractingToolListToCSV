# file_name: CSVListProcessor.py

import pandas as pd

class CSVseperate:
    def __init__(self):
        pass
            
    def process_lists(self, input_df):
        self.create_task_list_csv(input_df)
        self.create_tool_list_csv(input_df)
    
    def create_tool_list_csv(self, input_df, remove=True):
        try:
            # Select only the columns for the Tool List
            tool_list_df = input_df[['AMM Task', 'AMM Description', 'Task Revision', 'Part Number', 'QTY', 'Part Description']].copy()

            # Convert 'Part Number' to string
            tool_list_df['Part Number'] = tool_list_df['Part Number'].astype(str)

            if remove:
                # Filter out rows containing 'OR' in 'Part Number'
                tool_list_df = tool_list_df[~tool_list_df['Part Number'].str.contains('OR', na=False)]

                # Replace string 'N/A' with actual NaN
                tool_list_df['QTY'] = tool_list_df['QTY'].replace('N/A', pd.NA)
                # Drop rows where 'QTY' is NaN
                tool_list_df.dropna(subset=['QTY'], inplace=True)

                # Replace '0' with '1' in 'QTY'
                tool_list_df.loc[tool_list_df['QTY'] == '0', 'QTY'] = '1'


            return tool_list_df

        except Exception as e:
            print(f"Error creating Tool List CSV: {e}")

    def create_task_list_csv(self, input_df):
        try:
            # Copy relevant columns for the Task List
            task_list_df = input_df[['Page_Block', 'AMM Task', 'AMM Description', 'Task Revision']].copy()

            # Remove duplicated rows based on 'AMM Task' column
            task_list_df.drop_duplicates(subset=['AMM Task'], inplace=True)


            return task_list_df

        except Exception as e:
            print(f"Error creating Task List CSV: {e}")

    def count_num_tools(self, task_list_df, tool_list_df):
        try:
            tool_list_df.dropna(subset=['QTY'], inplace=True)
            # Count the occurrence of the "AMM Description" column from the Tool List
            occurrence_count = tool_list_df['AMM Task'].value_counts()

            # Map the occurrence count to the "AMM Description" column in the Task List
            task_list_df['Number of Tools'] = task_list_df['AMM Task'].map(occurrence_count).fillna(0)

            return task_list_df 

        except Exception as e:
            print(f"Error counting Number of Tools: {e}")