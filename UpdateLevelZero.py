
class LevelZeroUpdate:

    #reference_df is just a parameter that will be passed to the class. So reference_df paratmer will be tool list, task list and reference list. 
    def __init__(self, mpd_df, reference_df):
        self.mpd_df = mpd_df
        self.reference_df = reference_df

    # Update rows with the values of the new cols from the MPD. These values from the MPD won't be shown in the final report.
    # To see the values from the MPD, look at the MPD file. For A320 and A330 group, see UpdateMPD.py. For A350, see MPDA350.py
    def update_row(self, row):
        matching_rows = self.mpd_df[self.mpd_df['AMM Task'] == row['AMM_ref']]
        if not matching_rows.empty:
            row['FC'] = matching_rows['New_FC'].values[0]
            row['FH'] = matching_rows['New_FH'].values[0]
            row['MO'] = matching_rows['New_MO'].values[0]
            row['NOTE'] = matching_rows['New_Note'].values[0]
            if len(matching_rows) >= 1:
                row['Involved_MPD'] = ', '.join(matching_rows['Task Number'].values)
        return row

    #this function will return the update_row function and return the updated reference_df
    def update_level_zero(self):
        self.reference_df = self.reference_df.apply(self.update_row, axis=1)
        # print(self.reference_df.columns.tolist())
        return self.reference_df


