import pandas as pd
import re

class MPDProcessor:
    def __init__(self, input_file):
        self.df = pd.read_csv(input_file)
        self.check_columns()
        self.process() #process the data, 
        self.update_mpd() #then update the MPD

    def check_columns(self):
        self.multi_thresholds = all(col in self.df.columns for col in ['Threshold1', 'Threshold2', 'Threshold3'])
        self.multi_intervals = all(col in self.df.columns for col in ['Interval1', 'Interval2', 'Interval3'])

    def process(self):
        self.add_mpd_description()
        self.add_amm_task()
        self.drop_columns()
        self.clean_threshold_interval()
        self.update_note_column()
        self.process_threshold_interval()

    def add_mpd_description(self):
        self.df.insert(2, "MPD Description", self.df["Description"].str[:50])

    def add_amm_task(self):
        self.df.insert(self.df.columns.get_loc("Reference") + 1, "AMM Task", 
                       self.df["Reference"].str[:2] + "-" + self.df["Reference"].str[2:4] + "-" + 
                       self.df["Reference"].str[4:6] + self.df["Reference"].str[6:])

    def drop_columns(self):
        self.df.drop(columns=["Description", "Reference"], inplace=True)

    def clean_threshold_interval(self): #remove ACT from the threshold and interval columns
        if self.multi_thresholds and self.multi_intervals:
            for i in range(1, 4):
                self.df[f"Threshold{i}"] = self.df[f"Threshold{i}"].str.replace("ACT", "")
                self.df[f"Interval{i}"] = self.df[f"Interval{i}"].str.replace("ACT", "")
        else:
            self.df["Threshold"] = self.df["Threshold"].str.replace("ACT", "")
            self.df["Interval"] = self.df["Interval"].str.replace("ACT", "")

    def update_note_column(self):
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

    #this extract digits from the text and convert it to float like 2.5 YE-> 2.5, 5 FH -> 5.0
    def extract_value(self, text, unit): 
        if pd.isna(text):
            return None
        pattern = rf'(\d+(\.\d+)?)\s*{unit}'
        match = re.search(pattern, str(text))
        return float(match.group(1)) if match else None

    #this function convert the value to month. if more units are found, they can be added in converstion. those units must be added in line:87 for value conversion. 
    def update_mo(self, value, unit):
        conversion = {'YE': 12, 'MO': 1, 'DY': 1/30, 'HR': 1/730}
        return value * conversion.get(unit, 0)

    def process_row(self, row):
        result = {'FH': None, 'FC': None, 'MO': None}

        if self.multi_thresholds and self.multi_intervals: #if there are multiple thresholds and intervals
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

        for unit in ['YE', 'MO', 'DY', 'HR']:#if more units are found, add them here.
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

    def update_mpd(self): #this function will created new columns and update the values of the new columns. These new columns are created to store the minimum values of FC, FH, MO and Note.
        self.add_new_columns()
        self.update_new_columns()
        self.clean_zero_values()
        self.order_columns()

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

    def order_columns(self):
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

    def clean_zero_values(self):
        self.df.loc[self.df['New_MO'] == 0, 'New_MO'] = ''

    def save_to_dataframe(self): #this return whatever the data is processed so far. 
        return self.df


#this main function is only for testing MPD list. It can be deleted.
def main():
    mpd = MPDProcessor('MPD.csv').save_to_dataframe()
    
    mpd.to_csv('MPD_2cols.csv', index=False)
    # print(mpd.head(10))
    # print(mpd['New_FC'])

# Usage
if __name__ == "__main__":
    main()
    
    
