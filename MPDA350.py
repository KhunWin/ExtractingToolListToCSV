import pandas as pd
import re

class MPDA350:
    def __init__(self, input_file):
        self.df = pd.read_csv(input_file)
        self.check_columns()
        self.process()
        self.update_mpd()

    #this is just grouping all the functions that will be used to process the MPD file
    #all the fucntion in this function should be called in order. Otherwise, it will not give the result. 
    def process(self):
        self.add_mpd_description()
        self.add_amm_task()
        self.drop_columns()
        self.clean_threshold_interval()
        self.update_note_column()
        self.process_threshold_interval()
    
    def check_columns(self): #this is to check if multiples Threshold and Interval are present in the MPD file
        self.multi_thresholds = all(col in self.df.columns for col in ['Threshold1', 'Threshold2', 'Threshold3'])
        self.multi_intervals = all(col in self.df.columns for col in ['Interval1', 'Interval2', 'Interval3'])
        
    def add_mpd_description(self):
        self.df.insert(2, "MPD Description", self.df["Description"].str[:50])
        
    def add_amm_task(self):
        # Always remove "MP " from "Threshold"
        if self.multi_thresholds and self.multi_intervals:
            # Remove "MP " from Threshold1, Threshold2, and Threshold3 if they exist
            for col in ['Threshold1', 'Threshold2', 'Threshold3']:
                self.df[col] = self.df[col].str.replace("MP ", "")
        
        # Create the "AMM Task" column based on the "Reference" column
        self.df["AMM Task"] = self.df["Reference"].str[2:4] + self.df["Reference"].str[4:6] + self.df["Reference"].str[6:]
        
        # Insert the "AMM Task" column immediately after the "Reference" column
        self.df.insert(self.df.columns.get_loc("Reference") + 1, "AMM Task", self.df.pop("AMM Task"))

    def drop_columns(self):
        self.df.drop(columns=["Description", "Reference"], inplace=True)


    def clean_threshold_interval(self): #This is to remove the ACT from the Threshold and Interval columns
        if self.multi_thresholds and self.multi_intervals:
            for i in range(1, 4):
                self.df[f"Threshold{i}"] = self.df[f"Threshold{i}"].str.replace("ACT", "")
                self.df[f"Interval{i}"] = self.df[f"Interval{i}"].str.replace("ACT", "")
        else:
            self.df["Threshold"] = self.df["Threshold"].str.replace("ACT", "")
            self.df["Interval"] = self.df["Interval"].str.replace("ACT", "")

    def add_columns(self):
        note_loc = self.df.columns.get_loc('Interval')
        self.df.insert(note_loc, 'FC', value='')
        self.df.insert(note_loc, 'FH', value='')
        self.df.insert(note_loc, 'MO', value='')
        self.df.insert(note_loc, 'Note', value='')

    def update_note_column(self): #this is to update the Note column in the MPD file
        if self.multi_thresholds and self.multi_intervals:
            self.df['Note'] = self.df.apply(
                lambda row: 'X' if any('NOTE' in str(row[f'Threshold{i}']) or 'NOTE' in str(row[f'Interval{i}']) for i in range(1, 4)) else '',
                axis=1
            )
        else:
            self.df['Note'] = self.df.apply(
                lambda row: 'X' if 'NOTE' in str(row['Threshold']) or 'NOTE' in str(row['Interval']) else '',
                axis=1
            )

    def extract_value(self, text, unit):
        if pd.isna(text):
            return None
        pattern = rf'(\d+(\.\d+)?)\s*{unit}'
        match = re.search(pattern, str(text))
        # return int(match.group(1)) if match else None
        return float(match.group(1)) if match else None #this is to return float instead of int since there are float values in the MPD file

    def update_mo(self, value, unit): #This is how the MO column is updated. conversion method can be changed if needed
        conversion = {'YE': 12, 'MO': 1, 'DY': 1/30, 'HR': 1/730}
        return value * conversion.get(unit, 0)

    def process_row(self, row):
        result = {'FH': None, 'FC': None, 'MO': None}

        if self.multi_thresholds and self.multi_intervals:
            thresholds = [row[f'Threshold{i}'] for i in range(1, 4)]
            intervals = [row[f'Interval{i}'] for i in range(1, 4)]
            
            sources = [t for t in thresholds if not pd.isna(t) and t.strip()]
            if not sources:
                sources = [i for i in intervals if not pd.isna(i) and i.strip()]
        else:
            sources = [row['Threshold']] if not pd.isna(row['Threshold']) and row['Threshold'].strip() else [row['Interval']]

        for unit in ['FH', 'FC']:
            values = [self.extract_value(source, unit) for source in sources]
            values = [v for v in values if v is not None]
            if values:
                result[unit] = min(values)

        for unit in ['YE', 'MO', 'DY', 'HR']:
            values = [self.extract_value(source, unit) for source in sources]
            values = [v for v in values if v is not None]
            if values:
                result['MO'] = min(self.update_mo(v, unit) for v in values)
                break

        for key, value in result.items():
            if value is not None:
                row[key] = value
        return row

    def process_threshold_interval(self):
        self.df = self.df.apply(self.process_row, axis=1)

    #this is just grouping all the functions that to update the MPD file for A350
    #all these functions should be called in order. Otherwise, it will not give the result.
    def update_mpd(self):
        self.add_new_columns()
        self.update_new_columns()
        self.clean_zero_values()
        self.order_columns()
        self.add_amm_code_column()

    def add_new_columns(self):
        note_loc = self.df.columns.get_loc('Note')
        self.df.insert(note_loc, 'New_FC', value='')
        self.df.insert(note_loc, 'New_FH', value='')
        self.df.insert(note_loc, 'New_MO', value='')
        self.df.insert(note_loc + 1, 'New_Note', value='')

    def update_new_columns(self):
        for col in ['MO', 'FC', 'FH']:
            self.df[col] = self.df[col].astype(float)
            self.df[f'New_{col}'] = self.df.groupby('AMM Task')[col].transform('min')

        self.df['New_Note'] = self.df.groupby('AMM Task')['Note'].transform(self.fill_x_or_first_non_empty)

    @staticmethod
    def fill_x_or_first_non_empty(series):
        if (series == 'X').any():
            return 'X'
        else:
            non_empty = series[series.notna() & (series != '')]
            return non_empty.iloc[0] if not non_empty.empty else ''

    def clean_zero_values(self):
        self.df.loc[self.df['New_MO'] == 0, 'New_MO'] = ''

    def mpd_file(self):
        return self.df
    
    def order_columns(self): #this is to order the columns in the MPD file
        if self.multi_thresholds and self.multi_intervals:
            cols_order = [
                'Task Number', 'MPD Description', 'AMM Task',
                'Threshold1', 'Interval1', 'Threshold2', 'Interval2', 'Threshold3', 'Interval3',
                'FC', 'FH', 'MO', 'Note', 'New_FC', 'New_FH', 'New_MO', 'New_Note'
            ]
        else:
            cols_order = [
                'Task Number', 'MPD Description', 'AMM Task',
                'Threshold', 'Interval',
                'FC', 'FH', 'MO', 'Note', 'New_FC', 'New_FH', 'New_MO', 'New_Note'
            ]
        self.df = self.df[cols_order]

    def add_amm_code_column(self):
        # Insert the 'AMM Code' column right after 'AMM Task'
        amm_task_loc = self.df.columns.get_loc('AMM Task')
        self.df.insert(amm_task_loc + 1, 'AMM Code', '')

        # Update 'AMM Code' column based on the 'AMM Task' values
        self.df['AMM Code'] = self.df['AMM Task'].apply(self.extract_code)

    @staticmethod
    def extract_code(amm_task): #this is extracting AMM Code from AMM Task
        # Assuming the format is consistent and extracting parts as specified
        if pd.isna(amm_task):
            return ''
        else:
            # return parts[2] + parts[3] + parts[:3] + parts[4][3:] + parts[5][2:]
            return amm_task[8:10] + amm_task[11:13] + amm_task[14:16]+ amm_task[17:19] + amm_task[23:26]


    def drop_to_newcols(self):
        # Create a copy of the DataFrame without the new columns
        output_df = self.df.drop(columns=['New_FC', 'New_FH', 'New_MO', 'New_Note'])
        return output_df

    def save_to_dataframe(self): #this will return the final dataframe after calculating the MO, FC, FH and Note columns
        return self.df

# this is for testing the MPDA350 classs specifically
# the follow codes shows how to test the MPD file and see if the output is correct or not
if __name__ == "__main__":
    # processor = MPDA350('MPD_a350_copy.csv') ##it is accurate 
    processor = MPDA350('MPD_A350.csv')
    # processor.save_to_csv('mpd_update.csv')
    mpd = processor.mpd_file()
    # mpd.to_csv('mpd_update_todelete.csv', index=False)
    print(mpd.head())
    mpd.to_csv('delete2.csv', index=False)



    