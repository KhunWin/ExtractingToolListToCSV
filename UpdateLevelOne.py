import pandas as pd
import numpy as np
import concurrent.futures

class DataFrameUpdater:
    #reference_df is a parameter passed to the class to update tool list and task list. reference_df means reference list.  
    def __init__(self, tool_df, reference_df):
        self.tool_df = tool_df
        self.reference_df = reference_df

    #update the Lv1 columns of tool list and task list with the values from the reference list
    def update_new_FC(self, row):
        matching_rows = self.reference_df[self.reference_df['Reference AMM(n+1)'] == row['AMM Task']]
        if not matching_rows.empty:
            row['l1_FC'] = pd.to_numeric(matching_rows['FC'], errors='coerce').min()
            row['l1_FH'] = pd.to_numeric(matching_rows['FH'], errors='coerce').min()
            row['l1_MO'] = pd.to_numeric(matching_rows['MO'], errors='coerce').min()
            row['l1_NOTE'] = 'X' if 'X' in matching_rows['NOTE'].values else ''
        else:
            row['l1_FC'] = np.nan
            row['l1_FH'] = np.nan
            row['l1_MO'] = np.nan
            row['l1_NOTE'] = ''
        return row

    def update_df(self, df):

        try:
            return df.apply(lambda row: self.update_new_FC(row), axis=1)
        except Exception as e:
            print(f"An error occurred: {e}")
            return df

    #This function is for parallel processing of the DataFrame to improve performance
    def split_and_update(self):
        half = len(self.tool_df) // 2
        df1, df2 = self.tool_df.iloc[:half].copy(), self.tool_df.iloc[half:].copy()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future1 = executor.submit(self.update_df, df1)
            future2 = executor.submit(self.update_df, df2)

            df1_updated = future1.result()
            df2_updated = future2.result()

        self.tool_df = pd.concat([df1_updated, df2_updated])

    #updating NOTE column
    def note(self, row):
        note_value = row['NOTE'] if pd.notnull(row['NOTE']) else ''
        l0_note_value = row['l1_NOTE'] if pd.notnull(row['l1_NOTE']) else ''
        row['lv01_NOTE'] = note_value if note_value else l0_note_value
        return row

    def apply_notes(self):
        self.tool_df = self.tool_df.apply(self.note, axis=1)

    def smaller_ignore_nan(self, s1, s2):
        try:
            s1 = pd.to_numeric(s1, errors='coerce')
            s2 = pd.to_numeric(s2, errors='coerce')
        except Exception as e:
            print(f"Error converting to numeric: {e}")
            return s1 if pd.notnull(s1) else s2
        
        if pd.isnull(s1):
            return s2
        elif pd.isnull(s2):
            return s1
        else:
            return min(s1, s2)

    #updating lv01 columns 
    def safe_combine(self, col1, col2):
        if col2 in self.tool_df.columns:
            return self.tool_df[col1].combine(self.tool_df[col2], self.smaller_ignore_nan)
        else:
            return self.tool_df[col1]
    
    #updating lv01 columns
    def apply_combines(self):
        self.tool_df['Lv01_FC'] = self.safe_combine('FC', 'l1_FC')
        self.tool_df['Lv01_FH'] = self.safe_combine('FH', 'l1_FH')
        self.tool_df['Lv01_MO'] = self.safe_combine('MO', 'l1_MO')

    #run all the process above and return the updated DataFrame
    def process(self):
        self.split_and_update()
        self.apply_combines()
        self.apply_notes()
        return self.tool_df

# This function is for testing purposes only. This can be removed. 
def main():
    # Assuming tool_df and reference_df are already defined DataFrames
    tool_df = pd.DataFrame()  # Placeholder, replace with actual DataFrame
    reference_df = pd.DataFrame()  # Placeholder, replace with actual DataFrame
    
    # updater = DataFrameUpdater(tool_df, reference_df)
    updater = DataFrameUpdater('tool_list_withhxstock', 'update_reference_csv_test.csv')
    updated_tool_df = updater.process()
    
    # Print the updated DataFrame for verification
    # print(updated_tool_df.head())

if __name__ == "__main__":
    main()