########################################################################
#  Program Name: 0_southeast_append_new_data.py  
#  Description:  Append new quarter's data to previous 202105 run.
#
#  Inputs:  raw/SEAL_HLTH_MC_202102-202104_v3.txt
#           202105/raw/SEAL_HLTH_MC_20171001_20210217 V2_final.txt
#
#  Output:  created/SEAL_HLTH_MC_appended_20171001_202104.txt
#
#  Author: Riley Franks, 8/17/2021
#
# Used for 202203 Run of First Healths Data (needed to combine the
# 2022 data file with new file containing Jan. 2022 data)
########################################################################
import pandas as pd
# import numpy as np
import os
import time
import datetime
# import _log_helper_scripts as log
# import shutil
# import RUN_PARAMETERS as params


# import RUN_PARAMETERS as params
# import two_by_two_helper_scripts as helpers

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.options.display.float_format = '{:.4f}'.format
 
### Start off with some good log information...
def printLogHeader():
    """Report session information to be used at top of run log."""
    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print(f"Username: {os.getlogin()}",
          f"PID: {os.getpid()}",
          f"Run start time: {datetime.datetime.now():%a %b %d, %Y %I:%M%p %Z}",
          sep="\n")
    print("---------------------------------------------------------------")
 
start_time = time.time()
printLogHeader()
# program_name = os.path.basename(__file__).upper()
# print(f'\nRunning {program_name}')

### Set parameters
old_file = 'FirstHealth_4800_20221201_20230131.txt'
new_file1 = 'FirstHealth_4800_20230101_20230228.txt'
new_file2 = 'FirstHealth_4800_20230201_20230331.txt'
new_file3 = 'FirstHealth_4800_20230301_20230430.txt'
final_file = 'FirstHealth_4800_20221201_20230430_test.txt'
client_path = 'C:/PHI/Projects/FirstHealth/12th Refresh 202303/Client Data/Preprocessing'
# new_file_name = new_file.split(client_path+'/raw/')[1]

### Read in old data
# first count the number of rows in the old file.
with open(f'{client_path}/{old_file}', 'r') as fp:
    num_lines = sum(1 for line in fp)
print()
print(f'''The old file, {old_file},
located in {client_path}
contains {num_lines:,.0f} lines including a header row.
''')
del num_lines

old_df = pd.read_csv(f'{client_path}/{old_file}', sep='|', dtype=str)
print('')
print(f'Total records in old_df = {old_df.shape[0]:,.0f}',"",sep='\n')

# print the record count in the dataframe extract
print(f"Total records imported into old_df from client file = {old_df.shape[0]:,.0f}")
print()

### Read in new data file1
print('','New data:',sep='\n')
# first count the number of rows in the new file.
with open(f'{client_path}/{new_file1}', 'r') as fp:
    num_lines = sum(1 for line in fp)
print()
print(f'''The new file, {new_file1},
located in {client_path}
contains {num_lines:,.0f} lines including a header row.
''')
del num_lines

new_df = pd.read_csv(f'{client_path}/{new_file1}', sep='|', dtype=str)
print('')
print(f'Total records in new_df = {new_df.shape[0]:,.0f}',"",sep='\n')


### Report date distributions for the old & new data
print('','','-'*27,'Date distribution of previous data:',
      pd.to_datetime(old_df['DISDATE'], format='%m%d%Y').describe(datetime_is_numeric=True),
      '','','-'*27,'Date distribution of new data:',
      pd.to_datetime(new_df['DISDATE'], format='%m%d%Y').describe(datetime_is_numeric=True),
      sep='\n')

### Combine old & new
df = pd.concat([old_df, new_df], ignore_index=True, sort=False)

### Check for and drop duplicates
dupe_count = df.duplicated(subset="PCN").sum()
print('','Checking for duplicate records:',
      f'   {df.duplicated(subset="PCN").sum():,} duplicate PCNs',
      sep='\n')
print('',f'Dropping {df.duplicated(subset="PCN").sum():,} duplicates of PCN, keeping last','',sep='\n')
df.drop_duplicates(subset="PCN", keep='last', inplace=True)
print(f'Total records in df = {df.shape[0]:,.0f}')
#QA check new file 1
print('\nRecord Count QA Check - file1:')
print('Subsetted previous file record count: ', len(old_df))
print('New file record count: ', len(new_df))
print('Total dupes to remove: ',dupe_count)
print('Final file record count: ', len(df))
print('QA Check Passed? ', len(df)==len(old_df)+len(new_df)-dupe_count)
print()

# copy df into old_df
old_df = df.copy()
print(f'After copying df into old_df, total records in old_df = {old_df.shape[0]:,.0f}',"",sep='\n')

#%%
### Read in new data file2
print('','New data:',sep='\n')
# first count the number of rows in the new file.
with open(f'{client_path}/{new_file2}', 'r') as fp:
    num_lines = sum(1 for line in fp)
print()
print(f'''The new file, {new_file2},
located in {client_path}
contains {num_lines:,.0f} lines including a header row.
''')
del num_lines

new_df = pd.read_csv(f'{client_path}/{new_file2}', sep='|', dtype=str)
print(f'Total records in new_df = {new_df.shape[0]:,.0f}',"",sep='\n')
print()

### Report date distributions for the old & new data
print('','','-'*27,'Date distribution of previous data:',
      pd.to_datetime(old_df['DISDATE'], format='%m%d%Y').describe(datetime_is_numeric=True),
      '','','-'*27,'Date distribution of new data:',
      pd.to_datetime(new_df['DISDATE'], format='%m%d%Y').describe(datetime_is_numeric=True),
      sep='\n')

### Combine old & new
df = pd.concat([old_df, new_df], ignore_index=True, sort=False)

### Check for and drop duplicates
dupe_count = df.duplicated(subset="PCN").sum()
print('','Checking for duplicate records:',
      f'   {df.duplicated(subset="PCN").sum():,} duplicate PCNs',
      sep='\n')
print('',f'Dropping {df.duplicated(subset="PCN").sum():,} duplicates of PCN, keeping last','',sep='\n')
df.drop_duplicates(subset="PCN", keep='last', inplace=True)
# QA check new file 2
print(f'Total records in df = {df.shape[0]:,.0f}')
print('\nRecord Count QA Check - file2:')
print('Subsetted previous file record count: ', len(old_df))
print('New file record count: ', len(new_df))
print('Total dupes to remove: ',dupe_count)
print('Final file record count: ', len(df))
print('QA Check Passed? ', len(df)==len(old_df)+len(new_df)-dupe_count)
print()

# copy df into old_df
old_df = df.copy()
print(f'After copying df into old_df, total records in old_df = {old_df.shape[0]:,.0f}',"",sep='\n')
#%%
### Read in new data file3
print('','New data:',sep='\n')
# first count the number of rows in the new file.
with open(f'{client_path}/{new_file3}', 'r') as fp:
    num_lines = sum(1 for line in fp)
print()
print(f'''The new file, {new_file3},
located in {client_path}
contains {num_lines:,.0f} lines including a header row.
''')
del num_lines

new_df = pd.read_csv(f'{client_path}/{new_file3}', sep='|', dtype=str)
print(f'Total records in new_df = {new_df.shape[0]:,.0f}',"",sep='\n')
print()

### Report date distributions for the old & new data
print('','','-'*27,'Date distribution of previous data:',
      pd.to_datetime(old_df['DISDATE'], format='%m%d%Y').describe(datetime_is_numeric=True),
      '','','-'*27,'Date distribution of new data:',
      pd.to_datetime(new_df['DISDATE'], format='%m%d%Y').describe(datetime_is_numeric=True),
      sep='\n')

### Combine old & new
df = pd.concat([old_df, new_df], ignore_index=True, sort=False)

### Check for and drop duplicates
dupe_count = df.duplicated(subset="PCN").sum()
print('','Checking for duplicate records:',
      f'   {df.duplicated(subset="PCN").sum():,} duplicate PCNs',
      sep='\n')
print('',f'Dropping {df.duplicated(subset="PCN").sum():,} duplicates of PCN, keeping last','',sep='\n')
df.drop_duplicates(subset="PCN", keep='last', inplace=True)
# QA check new file 3
print(f'Total records in df = {df.shape[0]:,.0f}')
print('\nRecord Count QA Check - file3:')
print('Subsetted previous file record count: ', len(old_df))
print('New file record count: ', len(new_df))
print('Total dupes to remove: ',dupe_count)
print('Final file record count: ', len(df))
print('QA Check Passed? ', len(df)==len(old_df)+len(new_df)-dupe_count)
print()

### Report date distributions for final df data
print('','','-'*27,'Date distribution of final data:',
      pd.to_datetime(df['DISDATE'], format='%m%d%Y').describe(datetime_is_numeric=True),
      sep='\n')
#%%
### Output
# sort the df by DISDATE
print('Sorting df by DISDATE.','',sep='\n')
df = df.sort_values('DISDATE')

# export the final file
print('Exporting df to a 4800 pipe-delimited text file.')
df.to_csv(f'{client_path}/{final_file}', index=False, sep='|', na_rep='')
print()
# now count the number of rows in the exported 4800 new file.
with open(f'{client_path}/{final_file}', 'r') as fp:
    num_lines = sum(1 for line in fp)
print()
print(f'''Using df, the pipe-delimited text file, {final_file},
located in {client_path}
has been created and contains {num_lines:,g} lines including a header row.
Check the file visually before using.''')
del num_lines
print()
print()
print("The temporary FirstHealth concatenation program is complete.")


print('\n\nRecord Count QA Check:')
print('Subsetted previous file record count: ', len(old_df))
print('New file record count: ', len(new_df))
print('Total dupes to remove: ',dupe_count)
print('Final file record count: ', len(df))
print('QA Check Passed? ', len(df)==len(old_df)+len(new_df)-dupe_count)

### End the log
log.printLogCloser()
log.printTimeSince(start=start_time,text=f'{program_name} run time:')

