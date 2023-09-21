print('-'*80)
print("""
First Health 5200 to 4800 formatting code
Created on Fri Dec 17 09:06:08 2021
@author: Jim Cheairs

This code creates a 4800 formatted file from the 5200 layout.
The 5200 file is a legacy NC State PDS format submitted by First Health.
Note that the 5200 file is submitted w/o headers. Since only specific columns
from the 5200 are loaded, see the file, NC5200_to_4800_mapping_doc.xlsx, for
this mapping if interested. This file is on the P drive:
P:/StrategicServices/First Health/Monthly Submission Downloads 

These major procedures are accomplished:
1. Imports relavant columns from the 5200 file
2. Adds 4800 column headers to imported data
3. Performs a few field specific edits
4. Adds additional required 4800 fields with nulls and reorders the columns 
   to match 4800 requirements
5. Remove dups, review stats and output final 4800 pipe-delimited file

""")

import pandas as pd
import time as time
import os
import datetime
import numpy as np

# From tshlapp0852:>/consulting/code/python_dev/v4  by Riley 2019
# from log_helper_scripts import printTimeSince

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.options.display.float_format = '{:.4f}'.format
 
### Start off with some good log information...
def printLogHeader():
    """Report session information to be used at top of run log."""
    print("---------------------------------------------------------------")
    print(f"Username: {os.getlogin()}",
          f"PID: {os.getpid()}",
          f"Run start time: {datetime.datetime.now():%a %b %d, %Y %I:%M%p %Z}",
          sep="\n")
    print("---------------------------------------------------------------")
 
start_time = time.time()
printLogHeader()

# set the working directory, import file and export file
path_src = 'C:/PHI/Projects/FirstHealth/MonthlyFiles'
path_out = 'C:/PHI/Projects/FirstHealth/16th Refresh 202310/Client Data'
file_src = 'firsthealth-clinical_quality_dashboard-20230915_2023_07_08.txt'
file_4800 = 'FirstHealth_4800_20230701_20230831.txt'

# print the variables for logging
print('Variable Assignments:')
print(f'Source data directory: {path_src}')
print(f"5200 import file:  {file_src}")
print(f'Output data directory: {path_out}')
print(f'4800 export file:  {file_4800}.','',sep='\n')


# 1. Read in the client submitted file as the dataframe df
print('-'*80)
print(f'1. Reading in {path_src}/{file_src} into df.','',sep='\n')

df = pd.read_csv(f"{path_src}/{file_src}",  sep='|', header=None,
                 usecols=[1, 3, 7, 8, 9, 11, 13, 14, 16, 17, 18, 19, 30,
                          336, 337, 338, 339, 340, 341, 342, 343, 344, 345,
                          346, 347, 348, 349, 350, 351, 352, 353, 354, 355,
                          356, 357, 358, 359, 360, 361, 362, 363, 364, 365,
                          366, 367, 368, 369, 370, 371, 372, 373, 374, 375,
                          376, 377, 378, 379, 380, 381, 382, 383, 384, 385,
                          386, 387, 388, 389, 390, 391, 392, 393, 394, 395,
                          396, 397,
                          411, 412, 414, 415, 417, 418, 420, 421, 423, 424,
                          426, 427, 429, 430, 432, 433, 435, 436, 438, 439,
                          441, 442, 444, 445, 447, 448, 450, 451, 453, 454,
                          456, 457, 459, 460, 462, 463, 465, 466, 468, 469,
                          471, 472, 474, 475, 477, 478, 480, 481, 483, 484,
                          486, 487, 489, 490, 492, 493, 495, 496, 498, 499,
                          501, 502,
                          505, 507, 509, 510, 511, 520],
                 dtype=str, encoding='windows-1252')

# print the record count in the dataframe extract
print(f'Total records imported into df from client file = {df.shape[0]:,g}')
print()


# 2. Rename column indexes to 4800 field names
print('-'*80)
print('2.Add 4800 column names to the dataframe (df) to match index values.')
print()
df.columns = ['PCN', 'PROVNUM', 'DOB', 'ADMDATE', 'MRN', 'ZIP', 'SEX', 'RACE',
              'ADMTYPE', 'ADMSRC', 'STATUS', 'DISDATE', 'TOTALCLM',
              'PRDIAG', 'PRDIAGPOA', 'SECDX1', 'SECDX1POA',
              'SECDX2', 'SECDX2POA', 'SECDX3', 'SECDX3POA',
              'SECDX4', 'SECDX4POA', 'SECDX5', 'SECDX5POA',
              'SECDX6', 'SECDX6POA', 'SECDX7', 'SECDX7POA',
              'SECDX8', 'SECDX8POA', 'SECDX9', 'SECDX9POA',
              'SECDX10', 'SECDX10POA', 'SECDX11', 'SECDX11POA',
              'SECDX12', 'SECDX12POA', 'SECDX13', 'SECDX13POA',
              'SECDX14', 'SECDX14POA', 'SECDX15', 'SECDX15POA',
              'SECDX16', 'SECDX16POA', 'SECDX17', 'SECDX17POA',
              'SECDX18', 'SECDX18POA', 'SECDX19', 'SECDX19POA',
              'SECDX20', 'SECDX20POA', 'SECDX21', 'SECDX21POA',
              'SECDX22', 'SECDX22POA', 'SECDX23', 'SECDX23POA',
              'SECDX24', 'SECDX24POA', 'SECDX25', 'SECDX25POA',
              'SECDX26', 'SECDX26POA', 'SECDX27', 'SECDX27POA',
              'SECDX28', 'SECDX28POA', 'SECDX29', 'SECDX29POA',
              'SECDX30', 'SECDX30POA',
              'PRPROC', 'PRPRDATE', 'SECPRC1', 'SECDAT1', 'SECPRC2', 'SECDAT2',
              'SECPRC3', 'SECDAT3', 'SECPRC4', 'SECDAT4', 'SECPRC5', 'SECDAT5',
              'SECPRC6', 'SECDAT6', 'SECPRC7', 'SECDAT7', 'SECPRC8', 'SECDAT8',
              'SECPRC9', 'SECDAT9', 'SECPRC10', 'SECDAT10',
              'SECPRC11', 'SECDAT11', 'SECPRC12', 'SECDAT12',
              'SECPRC13', 'SECDAT13', 'SECPRC14', 'SECDAT14',
              'SECPRC15', 'SECDAT15', 'SECPRC16', 'SECDAT16',
              'SECPRC17', 'SECDAT17', 'SECPRC18', 'SECDAT18',
              'SECPRC19', 'SECDAT19', 'SECPRC20', 'SECDAT20',
              'SECPRC21', 'SECDAT21', 'SECPRC22', 'SECDAT22',
              'SECPRC23', 'SECDAT23', 'SECPRC24', 'SECDAT24',
              'SECPRC25', 'SECDAT25', 'SECPRC26', 'SECDAT26',
              'SECPRC27', 'SECDAT27', 'SECPRC28', 'SECDAT28',
              'SECPRC29', 'SECDAT29', 'SECPRC30', 'SECDAT30',
              'ATTMD', 'OPERMD', 'CONMD1', 'CONMD2', 'CONMD3', 'PAYCODE1']

# List the column names for log and checking
print('After adding 4800 column names, df info includes:')
print(df.info(verbose=True, show_counts=True),'',sep='\n')

# 3. formatting specific fields.
print('-'*80)
print('3. Now formatting several fields to meet 4800 requirements','', sep='\n')
# Updating the PROVNUM to appropriate value
print('Updating the submitted PROVNUM to the proper MPN.','',sep='\n')
print('We are only expecting one PROVNUM value in this dataframe.')
print('The number of records by the submitted PROVNUM is:')
print(df.groupby(['PROVNUM'])['PCN'].count(),'',sep='\n')

# Edit PROVNUM field from supplied value to client MPN - 340115
print("Change PROVNUM NPI 561936354 to client's MPN of 340115.")
df = df.replace({'PROVNUM': {'561936354': '340115'}}, regex=True)
# Check count by updated value
print()
print('The number of records by updated PROVNUM is:')
print(df.groupby(['PROVNUM'])['PCN'].count(),'', sep='\n')

# Update the SEX field with 4800 standard values
print()
print('Decoding the submitted SEX values to 4800 codes.')
print( 'by changing Female to F and Male to M','',sep='\n')
print('The number of records by submitted SEX values is:')
print(df.groupby(['SEX'])['PCN'].count(),'',sep='\n')

# Edit SEX field to contain the expected values of M, F or U
print('Change the SEX field to contain the appropriate 4800 values.')
print('Replace Female with F and Male with M.','',sep='\n')
df = df.replace({'SEX': {'Female': 'F', 'Male': 'M', 'Unknown': 'U'}}, regex=True)

# Check count by current SEX values
print("The number of records by updated SEX values is:")
print(df.groupby(['SEX'])['PCN'].count(),'',sep='\n')

# Edit the 10 character ZIP field to the first 5 characters
print()
print('Modify the ZIP values to the first 5 characters.','',sep='\n')
df['ZIP'] = df.ZIP.str.slice(0, 5)

# Check count by reformated ZIP values
print('The number of records by updated ZIP values is:')
print(df.groupby(['ZIP'])['PCN'].count(),'',sep='\n')

# Update Race codes: change null and 6 to 9
print('The submitted race code distribution is;')
print(df.groupby(['RACE'], dropna=False)['PCN'].count(),'',sep='\n')
print('Updating race code values of null and 6 to a value of 9')
df['RACE'] = df['RACE'].fillna('9').replace('6','9')
print('The updated race code distribution is;')
print(df.groupby(['RACE'], dropna=False)['PCN'].count(),'',sep='\n')

print('-'*80)
# 4. Add additional 4800 columns that are missing in the 5200 to df
print('4. Add additional required 4800 columns that are not in the 5200.')
print()

# add the SPTTYPE field
print('Add the SPTTYPE field with value of 1.','',sep='\n')
df['SPTTYPE'] = str(1)

# add the 10 extra dx code and POA positions as null using iteration
print('''Since the 5200 format contains only 30 dx code positions, add 
      dx code and POA fields for positions 31 thru 40 as null.''')
print()
# iterate to create these dx fields
for i in range(31,41):
    df[f'SECDX{i}'] = np.nan
    df[f'SECDX{i}POA'] = np.nan
del i # removing the variable after loop finishes

# add the 50 extra revcode and charge positions as null using concatenation
print('Add REVCOD# and CHARGE# fields for charge positions 1 thru 50 as null.')
print()

# Create a list of column names and default values
columns = []
for i in range(1, 51):
    columns.append(f'REVCOD{i}')
    columns.append(f'CHARGE{i}')

# Create dfChrgCols to store the new columns in wide format
dfChrgCols = pd.DataFrame(columns=columns)

# concatenate dfChrgCols to df 
df = pd.concat([df, dfChrgCols], axis=1)
del dfChrgCols
del i # removing the variable after loop finishes

# Reorder df columns to meet 4800 requirements.
print('Reorder df columns to meet 4800 requirements','',sep='\n')
df = df.reindex(columns=['PROVNUM', 'PCN', 'MRN', 'SPTTYPE', 'ADMDATE', 'DISDATE',
            'TOTALCLM', 'ZIP', 'DOB', 'SEX', 'RACE', 'ADMTYPE', 'ADMSRC',
            'STATUS', 'ATTMD', 'OPERMD', 'CONMD1', 'CONMD2', 'CONMD3',
            'PAYCODE1', 'PRDIAG', 'PRDIAGPOA', 'SECDX1', 'SECDX1POA',
            'SECDX2', 'SECDX2POA', 'SECDX3', 'SECDX3POA',
            'SECDX4', 'SECDX4POA', 'SECDX5', 'SECDX5POA',
            'SECDX6', 'SECDX6POA', 'SECDX7', 'SECDX7POA',
            'SECDX8', 'SECDX8POA', 'SECDX9', 'SECDX9POA',
            'SECDX10', 'SECDX10POA', 'SECDX11', 'SECDX11POA',
            'SECDX12', 'SECDX12POA', 'SECDX13', 'SECDX13POA',
            'SECDX14', 'SECDX14POA', 'SECDX15', 'SECDX15POA',
            'SECDX16', 'SECDX16POA', 'SECDX17', 'SECDX17POA',
            'SECDX18', 'SECDX18POA', 'SECDX19', 'SECDX19POA',
            'SECDX20', 'SECDX20POA', 'SECDX21', 'SECDX21POA',
            'SECDX22', 'SECDX22POA', 'SECDX23', 'SECDX23POA',
            'SECDX24', 'SECDX24POA', 'SECDX25', 'SECDX25POA',
            'SECDX26', 'SECDX26POA', 'SECDX27', 'SECDX27POA',
            'SECDX28', 'SECDX28POA', 'SECDX29', 'SECDX29POA',
            'SECDX30', 'SECDX30POA', 'SECDX31', 'SECDX31POA',
            'SECDX32', 'SECDX32POA', 'SECDX33', 'SECDX33POA',
            'SECDX34', 'SECDX34POA', 'SECDX35', 'SECDX35POA',
            'SECDX36', 'SECDX36POA', 'SECDX37', 'SECDX37POA',
            'SECDX38', 'SECDX38POA', 'SECDX39', 'SECDX39POA',
            'SECDX40', 'SECDX40POA',
            'PRPROC', 'PRPRDATE', 'SECPRC1', 'SECDAT1',
            'SECPRC2', 'SECDAT2', 'SECPRC3', 'SECDAT3',
            'SECPRC4', 'SECDAT4', 'SECPRC5', 'SECDAT5',
            'SECPRC6', 'SECDAT6', 'SECPRC7', 'SECDAT7',
            'SECPRC8', 'SECDAT8', 'SECPRC9', 'SECDAT9',
            'SECPRC10', 'SECDAT10', 'SECPRC11', 'SECDAT11',
            'SECPRC12', 'SECDAT12', 'SECPRC13', 'SECDAT13',
            'SECPRC14', 'SECDAT14', 'SECPRC15', 'SECDAT15',
            'SECPRC16', 'SECDAT16', 'SECPRC17', 'SECDAT17',
            'SECPRC18', 'SECDAT18', 'SECPRC19', 'SECDAT19',
            'SECPRC20', 'SECDAT20', 'SECPRC21', 'SECDAT21',
            'SECPRC22', 'SECDAT22', 'SECPRC23', 'SECDAT23',
            'SECPRC24', 'SECDAT24', 'SECPRC25', 'SECDAT25',
            'SECPRC26', 'SECDAT26', 'SECPRC27', 'SECDAT27',
            'SECPRC28', 'SECDAT28', 'SECPRC29', 'SECDAT29',
            'SECPRC30', 'SECDAT30',
            'REVCOD1', 'CHARGE1', 'REVCOD2', 'CHARGE2',
            'REVCOD3', 'CHARGE3', 'REVCOD4', 'CHARGE4',
            'REVCOD5', 'CHARGE5', 'REVCOD6', 'CHARGE6',
            'REVCOD7', 'CHARGE7', 'REVCOD8', 'CHARGE8',
            'REVCOD9', 'CHARGE9', 'REVCOD10', 'CHARGE10',
            'REVCOD11', 'CHARGE11', 'REVCOD12', 'CHARGE12',
            'REVCOD13', 'CHARGE13', 'REVCOD14', 'CHARGE14',
            'REVCOD15', 'CHARGE15', 'REVCOD16', 'CHARGE16',
            'REVCOD17', 'CHARGE17', 'REVCOD18', 'CHARGE18',
            'REVCOD19', 'CHARGE19', 'REVCOD20', 'CHARGE20',
            'REVCOD21', 'CHARGE21', 'REVCOD22', 'CHARGE22',
            'REVCOD23', 'CHARGE23', 'REVCOD24', 'CHARGE24',
            'REVCOD25', 'CHARGE25', 'REVCOD26', 'CHARGE26',
            'REVCOD27', 'CHARGE27', 'REVCOD28', 'CHARGE28',
            'REVCOD29', 'CHARGE29', 'REVCOD30', 'CHARGE30',
            'REVCOD31', 'CHARGE31', 'REVCOD32', 'CHARGE32',
            'REVCOD33', 'CHARGE33', 'REVCOD34', 'CHARGE34',
            'REVCOD35', 'CHARGE35', 'REVCOD36', 'CHARGE36',
            'REVCOD37', 'CHARGE37', 'REVCOD38', 'CHARGE38',
            'REVCOD39', 'CHARGE39', 'REVCOD40', 'CHARGE40',
            'REVCOD41', 'CHARGE41', 'REVCOD42', 'CHARGE42',
            'REVCOD43', 'CHARGE43', 'REVCOD44', 'CHARGE44',
            'REVCOD45', 'CHARGE45', 'REVCOD46', 'CHARGE46',
            'REVCOD47', 'CHARGE47', 'REVCOD48', 'CHARGE48',
            'REVCOD49', 'CHARGE49', 'REVCOD50', 'CHARGE50'])

# List the column names for log and checking for edited df
print('After adding additional 4800 columns & reordering, df info includes:')
print(df.info(verbose=True, show_counts=True),'',sep='\n')


# 5. Create final 4800 output
print('-'*80)
print('5. Run some checks and create the final 4800 flat file.','',sep='\n')
# Check for and drop duplicates
#  The 5200 submitted file contains continuation records for detail charges
#  Because we do not include the detail charges in the 4800 dataframe,
#   and because total charges are the same, we can dedup on full records 
#   using the below dedupped code which was copied from clin assess code
print('Check for duplicate records:',
      f'   {df.duplicated(subset="PCN").sum():,} duplicate PCNs',
      sep='\n')
print(f'Dropping {df.duplicated().sum():,} FULL duplicates','',sep='\n')
df.drop_duplicates(inplace=True)

# Report date distributions for new data
print('', '', 'Date distribution of new data:',
      pd.to_datetime(df['DISDATE'], format='%m%d%Y').describe(datetime_is_numeric=True),
      sep='\n')

# Check record counts by individual facilities
# FirstHealth is composed of three facilities under the same MPN (340115)
# These facilities are identified via the first 3 digits of the PCN
print()
print("""Checking subfacility record counts based on the first 2 digits of 
 the submitted PCN. The number of records by subfacility and total:""")
print(df.groupby(df.PCN.str[:2])['PROVNUM'].count())
print('--------------')
print(df.groupby(['PROVNUM'])['PCN'].count(),'',sep='\n')


# check the number of records by month
print()
print("""Checking record counts by month based on the 
 first 2 digits of the submitted DISDATE.""")
print(df.groupby(df.DISDATE.str[:2])['PCN'].count(),'',sep='\n')

# sort the df by DISDATE
print()
print('Sort df by DISDATE.','',sep='\n')
df = df.sort_values('DISDATE')

# export the final file
print()
print('Exporting df to a 4800 pipe-delimited text file.','',sep='\n')
df.to_csv(f'{path_out}/{file_4800}', index=False, sep='|', na_rep='')

# now count the number of rows in the exported 4800 file.
with open(f'{path_out}\\{file_4800}', 'r') as fp:
    num_lines = sum(1 for line in fp)
print()
print(f'''Using the final df, the pipe-delimited text file, {file_4800},
located in {path_out}
has been created and contains {num_lines:,g} lines including a header row.
Check the file visually before using.''')
del num_lines
print()
print()
print("The 5200 to 4800 file conversion program is complete.")