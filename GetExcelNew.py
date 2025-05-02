#this is the main program that runs the whole process
import pandas as pd
from XMLProcessor import XMLProcessor
from CSVseperate import CSVseperate
from UpdateMPD import MPDProcessor
from Reference import ReferenceProcessor
from ReferenceA350 import *
from TEM import ToolStockAnalyzer
from UpdateLevelZeroA350 import LevelZeroUpdateA350
from UpdateLevelOneA350 import DataFrameUpdaterLevelOneA350
from UpdateLevelZero import LevelZeroUpdate
from UpdateLevelOne import DataFrameUpdater
from CSVSeperateA350 import *
from MPDA350 import *
from TaskToolA350 import *


class CapabilityAutomationToolNew:
    def __init__(self, amm_file, mpd_file, tem_file, hxstock_file):
        self.amm_file = amm_file
        self.mpd_file = mpd_file
        self.tem_file = tem_file
        self.hxstock_file = hxstock_file
        self.A320 = False
        self.A330 = False
        self.A350 = False

    ## Checking aircraft type
    def check_aircraft_type(self):
        print('checking aircraft type')
        try:
            if os.path.isfile(self.amm_file):
                # If the input is a file, set A320 and A330 to True, A350 to False
                self.A320 = True
                self.A330 = True
                self.A350 = False
            elif os.path.isdir(self.amm_file):
                # If the input is a directory, set A350 to True, A320 and A330 to False
                self.A320 = False
                self.A330 = False
                self.A350 = True
            else:
                # If the input is neither a file nor a directory, raise an error
                raise ValueError("Input is neither a valid file nor a directory.")
        except ValueError as e:
            print("There is an error in checking the aircraft type input.")
            return
    #this process run non-A350 aircraft type
    def process_a320_a330(self, processor, csv_list_processor, output_file):
        print("'It's A320 or A330'")

        data_frame = processor.process_file()  # this is the data frame that will be used to create the task list and the tool list

        if data_frame is None:
            print("Error processing the input file.")
            return

        # Process the task list and tool list
        print("Processing tool list...")
        a320_tool_list = csv_list_processor.create_tool_list_csv(data_frame, True) #go to CSVseperate.py file for detailed calculation
        # a320_tool_list.to_csv("a330_tool_list_v4.csv", index=False)

        # Add hxstock
        print("Calculating HX Stock and TEM Equivalent...") #for detailed calculation go to TEM.py file
        hxstock = ToolStockAnalyzer(a320_tool_list, self.hxstock_file) ##a320_tool_list is the tool list that we just generated from line:60 and hxstock_file is the hxstock file we input.
        a320_tool_list['HX Stock'] = hxstock.add_hxstock()
        

        # Add TEM Equivalent
        tem = ToolStockAnalyzer(a320_tool_list, self.tem_file)

        a320_tool_list['TEM Equivalent'] = tem.update_tem()
        # a320_tool_list.to_csv("a320TestingSTD.csv", index=False) #this is to save the tool list to a csv file for checking TEM and HX stock calculation

        print("Processing task list...")
        a320_task_list = csv_list_processor.create_task_list_csv(data_frame) #go to CSVseperate.py file for detailed calculation
        if a320_task_list is None:
            print("Error creating Task List dataframe.")
            return

        print("Updating number of tools in task list...")
        # Update number of tools in task list sheet
        csv_list_processor.count_num_tools(a320_task_list, a320_tool_list) #go to CSVseperate.py file for detailed calculation

        print("Processing reference file...")
        # Process reference file
        initial_processor = ReferenceProcessor(self.amm_file) #go to Reference.py file for detailed calculation
        initial_processor.initial_processing()
        processed_content = initial_processor.process()
        reference_result = initial_processor.process_file(processed_content)

        print("Getting updated MPD file...")
        # Get updated MPD file
        mpd = MPDProcessor(self.mpd_file).save_to_dataframe() #this if for MPD calculation
        mpd_drop_newcols = mpd.drop(columns=['New_FC', 'New_FH', 'New_MO', 'New_Note']) #this is removing the new columns that we added in the MPD file so that they don't appear in the excel document.

        print("Updating zero level...") #go to UpdateLevelZero.py file for detailed calculation
        # Update zero level for reference file, tool list, and task list
        reference_result = self.update_zero_level(reference_result, mpd,'Parent AMM(n)')
        a320_tool_list = self.update_zero_level(a320_tool_list, mpd,'AMM Task')
        a320_task_list = self.update_zero_level(a320_task_list, mpd,'AMM Task')

        print("Updating level one...")
        # Update level one
        updated_tool_level_one = DataFrameUpdater(a320_tool_list, reference_result).process()
        updated_task_level_one = DataFrameUpdater(a320_task_list, reference_result).process()

        print("Writing to excel file...")
        # Write to all dataframes to an excel file
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            updated_task_level_one.to_excel(writer, sheet_name='Task List', index=False)
            updated_tool_level_one.to_excel(writer, sheet_name='Tool List', index=False)
            reference_result.to_excel(writer, sheet_name='Reference List', index=False)
            mpd_drop_newcols.to_excel(writer, sheet_name='MPD', index=False)

    #this process run A350 aircraft type only
    def process_a350(self, output_file):
        print('It is A350')
        csv_list_processor = CSVseperateA350() #refers to CSVseperateA350.py file

        # Process the task list and tool list
        # Process task list
        a350_extract = A350TextExtractor(self.amm_file) #refers to TaskToolA350.py file

        a350_extract.process_task() #refers to TaskToolA350.py file
        a350_task_list = a350_extract.create_dataframe() #refers to TaskToolA350.py file
        if a350_task_list is None:
            print("Error creating Task List dataframe.")
            return
        
        # Process tool list
        a350_extract.process_tool() #refers to TaskToolA350.py file
        a350_tool_list = a350_extract.create_dataframe()#refers to TaskToolA350.py file
        a350_tool_list = CSVseperateA350().create_tool_list_csv(a350_tool_list) #refers to CSVseperateA350.py file

        print("Calculating HX Stock and TEM Equivalent...")
        # Add hxstock
        hxstock = ToolStockAnalyzer(a350_tool_list, self.hxstock_file) #go to TEM.py file for detailed calculation
        a350_tool_list['HX Stock'] = hxstock.add_hxstock() #go to TEM.py file for detailed calculation

        # Add TEM Equivalent
        tem = ToolStockAnalyzer(a350_tool_list, self.tem_file) #go to TEM.py file for detailed calculation
        a350_tool_list['TEM Equivalent'] = tem.update_tem() #go to TEM.py file for detailed calculation
        # a350_tool_list.to_csv("a350TestingSTD.csv", index=False)   

        print("Updating number of tools in task list...")
        # Update number of tools in task list sheet
        csv_list_processor.count_num_tools(a350_task_list, a350_tool_list) #go to CSVSeperateA350.py file for detailed calculation

        print("Processing reference file...")
        # Process reference file
        reference_processor = A350Reference(self.amm_file)
        reference_processor.process_files()
        reference_result = reference_processor.create_dataframe()

        print("Getting updated MPD file...")
        # Get updated MPD file
        mpd = MPDA350(self.mpd_file).save_to_dataframe() #go to MPDA350.py file for detailed calculation
        mpd_drop_newcols = mpd.drop(columns=['New_FC', 'New_FH', 'New_MO', 'New_Note'])

        print("Updating zero level...")
        # Update zero level for reference list, tool list, and task list
        reference_result = self.update_zero_level_a350(reference_result, mpd) #go to line:192 file for detailed calculation
        a350_tool_list = self.update_zero_level_a350(a350_tool_list, mpd) #go to line:192 for detailed calculation
        a350_task_list = self.update_zero_level_a350(a350_task_list, mpd)

        print("Updating level one...")
        # Update level one
        reference_l1 = reference_processor.filter_dataframe(reference_result) #go to ReferenceA350.py file for detailed calculation
        updated_tool_level_one = DataFrameUpdaterLevelOneA350(a350_tool_list, reference_l1).process()
        updated_task_level_one = DataFrameUpdaterLevelOneA350(a350_task_list, reference_l1).process()
        print("Writing to excel file...")
        # Write to output file
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            updated_task_level_one.to_excel(writer, sheet_name='Task List', index=False)
            updated_tool_level_one.to_excel(writer, sheet_name='Tool List', index=False)
            reference_result.to_excel(writer, sheet_name='Reference List', index=False)
            mpd_drop_newcols.to_excel(writer, sheet_name='MPD', index=False)


    def update_zero_level(self, df, mpd, amm_column):
        df['FC'] = ''
        df['FH'] = ''
        df['MO'] = ''
        df['NOTE'] = ''
        df['Involved_MPD'] = ''
        df['AMM_ref'] = df[amm_column].str[:16]
        updated_df = LevelZeroUpdate(mpd, df).update_level_zero() #go to LevelZeroUpdate.py file for detailed calculation 
        updated_df.drop(columns=['AMM_ref'], inplace=True)
        return updated_df
    

    def update_zero_level_a350(self, df, mpd):
        df['FC'] = ''
        df['FH'] = ''
        df['MO'] = ''
        df['NOTE'] = ''
        df['Involved_MPD'] = ''
        updated_df = LevelZeroUpdateA350(mpd, df).update_level_zero() #go to UpdateLevelZeroA350.py file for detailed calculation
        return updated_df

    def run(self, output_file): #this function is called in line:398 in RunUiNew.py file
        print('running')
        self.check_aircraft_type()
        processor = XMLProcessor(self.amm_file) #to go to XMLProcessor.py file for detailed calculation
        
        if self.A320 or self.A330:
            self.process_a320_a330(processor, CSVseperate(), output_file)
        
        if self.A350:
            self.process_a350(output_file)

##this main function is to test the whole process without UI. This can be deleted. 
def main():
    amm_file = "AMM_330.sgm"
    mpd_file = "MPDA330_CSV.csv"
    tem_file = "TEM_A330.csv"
    hxstock_file = "hxstock.csv"
    excel_file = "A330ToolList.xlsx"
    all_excel = CapabilityAutomationToolNew(amm_file, mpd_file, tem_file, hxstock_file)
    all_excel.run(excel_file)
    print('done')

    # amm_path = "/Users/win/Desktop/temp_file_py/UI_A330_320_330_Updated/MP"  # Replace with your actual folder path
    # extract_task = TextExtractor(amm_path)
    # extract_task.process_task()
    # a350_task_list = extract_task.create_dataframe()
    # a350_task_list.to_csv("a350_task_list.csv", index=False)
    # extract_task.process_tool()
    # a350_tool_list = extract_task.create_dataframe()
    # a350_tool_list = CSVseperate().create_tool_list_csv(a350_tool_list)

    # a350_tool_list.to_csv("a350_tool_list.csv", index=False)
    
    # processor = MPDA350('MPD_a350_copy.csv') ##it is accurate 
    # processor.save_to_csv('mpd_update.csv')

    # get_excel = CapabilityAutomationToolNew(amm_path,'MPD_A350.csv','TEM_A350.csv','hxstock.csv')
    ##testing the mpd again "Descrption error is given". MPD is already updated, just need to run the code

    # get_excel.run('testing_a350_again_excel.xlsx')
    print('done')

   
    # mpd = processor.mpd_file() #this will give mpd_l0
if __name__ == "__main__":
    main()