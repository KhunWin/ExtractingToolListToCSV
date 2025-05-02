import pandas as pd

class ToolStockAnalyzer:
    def __init__(self, tool_csv, part_csv):
        self.part_no_df = pd.read_csv(part_csv)
        self.tool_list_df = tool_csv
        self.tool_list_df = self.tool_list_df[['Part Number']].copy()

    def clean_part_number(self, df, column): #replace O with 0, I with 1, and remove special characters
        df.loc[:, column] = (df[column]
                             .str.replace('O', '0', regex=False)
                             .str.replace('I', '1', regex=False)
                             .str.replace('[^a-zA-Z0-9]', '', regex=True))

    def add_hxstock(self):
        self.clean_part_number(self.tool_list_df, 'Part Number')
        self.clean_part_number(self.part_no_df, 'partno')
        
        self.tool_list_df['HX Stock'] = '0'

        # Update 'Nospecific' entries
        # no_specific_mask = self.tool_list_df['Part Number'] == 'Nospecific'
        no_specific_mask = self.tool_list_df['Part Number'].isin(['Nospecific', 'NoSpecific']) #check for 'Nospecific' or 'NoSpecific'
        self.tool_list_df.loc[no_specific_mask, 'HX Stock'] = 'STD'

        for i, row in self.tool_list_df.iterrows(): #iterate through the rows of the tool list and compare with the part number list to get the stock count
            if row['Part Number'] != 'Nospecific': 
                filtered_df = self.part_no_df[self.part_no_df['partno'] == row['Part Number']]
                if not filtered_df.empty:
                    hk_count = len(filtered_df[(filtered_df['owner'] == 'HX') & (filtered_df['condition'] == 'S')])
                    us_count = len(filtered_df[(filtered_df['owner'] == 'HX') & (filtered_df['condition'] == 'US')])
                    nonhx_count = len(filtered_df[filtered_df['owner'] == 'CUST'])
                    
                    counts = []
                    if hk_count > 0:
                        counts.append(f'{hk_count}@HX')
                    if us_count > 0:
                        counts.append(f'{us_count}@US')
                    if nonhx_count > 0:
                        counts.append(f'{nonhx_count}@nonHX')
                    
                    if counts:
                        self.tool_list_df.at[i, 'HX Stock'] = ', '.join(counts) if counts else '0' #if there are counts, join them with a comma, else return 0

        return self.tool_list_df['HX Stock'] #return the 'HX Stock' column
    
    def update_tem(self):
        self.tool_list_df['TEM Equivalent'] = ''  # Initialize the new column with empty strings
        
        for i, row in self.tool_list_df.iterrows():
            matching_rows = self.part_no_df[self.part_no_df['Part Number'] == row['Part Number']]
            if not matching_rows.empty:
                self.tool_list_df.loc[i, 'TEM Equivalent'] = matching_rows['Replaced by PN'].values[0] #get the value of the 'Replaced by PN' column from the matching row
        
        return self.tool_list_df['TEM Equivalent'] #return the 'TEM Equivalent' column


