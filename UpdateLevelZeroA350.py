import pandas as pd
class LevelZeroUpdateA350:
    def __init__(self, mpd_df, reference_df): #reference, tool list, task list
        self.mpd_df = mpd_df
        self.reference_df = reference_df

    # def update_row(self, row):
    #     # matching_rows = self.mpd_df[self.mpd_df['AMM Task'] == row['AMM_ref']]

    #     matching_rows = self.mpd_df[self.mpd_df['AMM Code'] == row['Parent AMM Code']]

    #     if not matching_rows.empty:
    #         row['FC'] = matching_rows['New_FC'].values[0]
    #         row['FH'] = matching_rows['New_FH'].values[0]
    #         row['MO'] = matching_rows['New_MO'].values[0]
    #         row['NOTE'] = matching_rows['New_Note'].values[0]
    #         if len(matching_rows) >= 1:
    #             # row['Involved_MPD'] = ', '.join(matching_rows['Task Number'].values)
    #             row['Involved_MPD'] = ', '.join(matching_rows['MPD Task'].values)
    #     return row
        
    def update_row(self, row):
        # Check if 'Parent AMM Code' exists and use it for comparison
        if 'Parent AMM Code' in row and pd.notna(row['Parent AMM Code']):
            matching_rows = self.mpd_df[self.mpd_df['AMM Code'] == row['Parent AMM Code']]
        # If 'Parent AMM(n)' doesn't exist or is NaN, use 'AMM Code' for comparison
        elif 'AMM Code' in row and pd.notna(row['AMM Code']):
            matching_rows = self.mpd_df[self.mpd_df['AMM Code'] == row['AMM Code']]
        else:
            matching_rows = pd.DataFrame()  # No match if neither column is present or both are NaN

        if not matching_rows.empty:
            row['FC'] = matching_rows['New_FC'].values[0]
            row['FH'] = matching_rows['New_FH'].values[0]
            row['MO'] = matching_rows['New_MO'].values[0]
            row['NOTE'] = matching_rows['New_Note'].values[0]
            if len(matching_rows) >= 1:
                row['Involved_MPD'] = ', '.join(matching_rows['Task Number'].values)
        
        return row

    def update_level_zero(self):
        self.reference_df = self.reference_df.apply(self.update_row, axis=1)
        # print(self.reference_df.columns.tolist())
        return self.reference_df

def main():
    lzero = LevelZeroUpdateA350('MPDA350_Dummy.csv','ReferenceListA350_Dummy.csv').update_level_zero()
    lzero.to_csv('testing_level_zero_reference.csv', index=False)


if __name__ == "__main__":
    main()


