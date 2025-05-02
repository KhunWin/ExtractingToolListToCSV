import pandas as pd
import numpy as np
import concurrent.futures

class DataFrameUpdaterLevelOneA350:
    def __init__(self, tool_df, reference_df): #tool_df can be tool list and task list
        self.tool_df = tool_df
        self.reference_df = reference_df

    def update_new_FC(self, row): #this function is updating the l1 columns based on Reference AMM Code from the reference list
        matching_rows = self.reference_df[self.reference_df['Reference AMM Code'] == row['AMM Code']] 
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
            print(f"An error occurred in updating level one: {e}")

    # Split the DataFrame into two halves and update them concurrently to save time
    def split_and_update(self):
        try:
            half = len(self.tool_df) // 2
            df1, df2 = self.tool_df.iloc[:half].copy(), self.tool_df.iloc[half:].copy()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future1 = executor.submit(self.update_df, df1)
                future2 = executor.submit(self.update_df, df2)

                df1_updated = future1.result()
                df2_updated = future2.result()

            self.tool_df = pd.concat([df1_updated, df2_updated])
        except Exception as e:
            print(f"An error occurred in splitting and updating: {e}")
    # Apply notes from the 'NOTE' column to the 'l1_NOTE' column if 'l1_NOTE' is empty
    def note(self, row):
        try:
            note_value = row['NOTE'] if pd.notnull(row['NOTE']) else ''
            l0_note_value = row['l1_NOTE'] if pd.notnull(row['l1_NOTE']) else ''
            row['lv01_NOTE'] = note_value if note_value else l0_note_value
            return row
        except Exception as e:
            print(f"An error occurred in applying notes: {e}")


    def apply_notes(self):
        self.tool_df = self.tool_df.apply(self.note, axis=1)

    # Combine two columns, ignoring NaN values
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
            return min(s1, s2) # Return the smaller value
    
    def safe_combine(self, col1, col2):
        if col2 in self.tool_df.columns:
            return self.tool_df[col1].combine(self.tool_df[col2], self.smaller_ignore_nan)
        else:
            return self.tool_df[col1]

    def apply_combines(self): # this function is to update lv01 columns based on the values of l1 columns and lv0 columns
        self.tool_df['Lv01_FC'] = self.safe_combine('FC', 'l1_FC')
        self.tool_df['Lv01_FH'] = self.safe_combine('FH', 'l1_FH')
        self.tool_df['Lv01_MO'] = self.safe_combine('MO', 'l1_MO')

    def process(self): #this fucntion must be in order
        self.split_and_update()
        self.apply_combines()
        self.apply_notes()
        return self.tool_df

# Usage
def main():
    # Assuming tool_df and reference_df are already defined DataFrames
    tool_df = pd.DataFrame()  # Placeholder, replace with actual DataFrame
    reference_df = pd.DataFrame()  # Placeholder, replace with actual DataFrame
    
    # updater = DataFrameUpdater(tool_df, reference_df)
    updater = DataFrameUpdaterLevelOneA350('tool_list_withhxstock', 'update_reference_csv_test.csv')
    updated_tool_df = updater.process()
    
    # Print the updated DataFrame for verification
    # print(updated_tool_df.head())

if __name__ == "__main__":
    main()