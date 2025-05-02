# file_name: CSVListProcessor.py

import pandas as pd

class CSVseperateA350:
    def __init__(self):
        pass
            
    def process_lists(self, input_df):
        self.create_tool_list_csv(input_df)
    
    # def create_tool_list_csv(self, input_df, remove=True): 
    #     try:
    #         # Select only the columns for the Tool List
    #         tool_list_df = input_df[['AMM Code','AMM Task', 'AMM Description', 'Task Revision', 'Part Number', 'QTY', 'Part Description']].copy()

    #         # Convert 'Part Number' to string
    #         tool_list_df['Part Number'] = tool_list_df['Part Number'].astype(str)

    #         if remove:
    #             # Filter out rows containing 'OR' in 'Part Number'
    #             tool_list_df = tool_list_df[~tool_list_df['Part Number'].str.contains('OR', na=False)]

    #             # Replace string 'N/A' with actual NaN
    #             tool_list_df['QTY'] = tool_list_df['QTY'].replace('N/A', pd.NA)
    #             # Drop rows where 'QTY' is NaN
    #             tool_list_df.dropna(subset=['QTY'], inplace=True)

    #             # Replace '0' with '1' in 'QTY'
    #             tool_list_df.loc[tool_list_df['QTY'] == '0', 'QTY'] = '1'


    #         return tool_list_df

    #     except Exception as e:
    #         print(f"Error creating Tool List CSV: {e}")

    def create_tool_list_csv(self, input_df, remove=True): 
        try:
            # Check if input_df is None or empty
            if input_df is None or input_df.empty:
                return pd.DataFrame(columns=['AMM Code', 'AMM Task', 'AMM Description', 'Task Revision', 'Part Number', 'QTY', 'Part Description'])

            # Ensure all required columns exist
            required_columns = ['AMM Code', 'AMM Task', 'AMM Description', 'Task Revision', 'Part Number', 'QTY', 'Part Description']
            missing_columns = [col for col in required_columns if col not in input_df.columns]
            
            if missing_columns:
                print(f"Missing columns: {missing_columns}")
                # Add missing columns with empty values
                for col in missing_columns:
                    input_df[col] = ''

            # Select only the columns for the Tool List
            tool_list_df = input_df[required_columns].copy()

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
            return pd.DataFrame(columns=['AMM Code', 'AMM Task', 'AMM Description', 'Task Revision', 'Part Number', 'QTY', 'Part Description'])

    #counting the number of tools and it returns Number of Tools column
    def count_num_tools(self, task_list_df, tool_list_df):
        try:
            # tool_list_df.dropna(subset=['QTY'], inplace=True)
            # Count the occurrence of the "AMM Description" column from the Tool List
            occurrence_count = tool_list_df['AMM Task'].value_counts()

            # Map the occurrence count to the "AMM Description" column in the Task List
            task_list_df['Number of Tools'] = task_list_df['AMM Task'].map(occurrence_count).fillna(0)
            task_list_df.drop_duplicates(subset=['AMM Task'], inplace=True) #only after counting the number of tools, then drop the duplicates so that we can get the correct number of tools

            return task_list_df #return the 'Number of Tools' column

        except Exception as e:
            print(f"Error counting Number of Tools: {e}")


    