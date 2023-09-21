##############################################################################
# Split Files 4800 formatting code
# @author: Jim Cheairs

# This python script intakes 4800 split files to create std 4800 output
# 1. imports 3 client files - disch, dx and px into dataframes with headers.
# 2. pivots dx and px dataframes into wide dataframes, one record per encounter.
# 3. merges disch, dx_wide and px_wide into a final 4800m wide format.
# 4. adds additional required 4800 fields with nulls.
# 5. Outputs final 4800 pipe-delimited file.
##############################################################################

##############################################################################
# Set up Instructions
# This program can be run from a local PC machine or unix.
# Several variables need to be entered for path and file locations.
# 1. Set the source directory variable (path_src) to source file location.
# 2. Set the file_disch variable as the name of the client discharge file.
# 3. Set the file_dx variable as the name of the client DX file.
# 4. Set the file_px variable as the name of the client PX file.
# 5. Set the file_4800 variable as the name of the final 4800 file.
##############################################################################
#%%
import pandas as pd
import time as time
import os
import datetime

# Start off with some good log information...
# start_time=datetime.datetime.now()
start_time = time.time()

print(f"""-------------------------------------
SYSTEM INFORMATION
Username:  {os.getlogin()}
Run start time: {datetime.datetime.now()}
-------------------------------------""")

print("""---------------------------------------------------------------------
This procedure creates a 4800 formatted file from client supplied split files.

The split files include a disch file containing one record per encounter and
narrow/long diagnosis and procedures files that contain dx and px codes
for each encounter by seq number.

The processing sections include:
 1. Disch File Import and Preprocessing (dfDisch)
 2. DX file import, format and pivot processing (dfDX and dfDXFlat)
 3. PX file import, format and pivot processing (dfPX and dfPXFlat)
 4. Merging dfDisch, dfDXFlat and dfPXFlat to create a final 4800 flat file
--------------------------------------------------------------------------""")
print()

# set the working directories, import files and export file variables
# be sure path directories use forward slashes.
path_src = 'C:/PHI/Projects/Oaklawn/2023q2/Client Data'
file_disch = 'Oaklawn_20230401_20230630_Disch.txt'
file_dx = 'Oaklawn_20230401_20230630_Dx.txt'
file_px = 'Oaklawn_20230401_20230630_Px_6_null_dates.txt'
file_4800 = 'Oaklawn_4800_20230401_20230630.txt'

# print the variables for logging
print('Variable Assignments:','',sep='\n')
print(f'Source file directory: {path_src}')
print(f'disch import file: {file_disch}')
print(f'dx import file: {file_dx}')
print(f'px import file: {file_px}')
print(f'4800 export file: {file_4800}.','',sep='\n')

##############################################################################
# 1. Disch File Import and Preprocessing
# 1a. Import file_disch to dfDisch
# 1b. Check for duplicates and drop if necessary.
# 1c. Check for nulls in all fields and replace if necessary
# 1d. Create column key to use for merging with dx and px files later.
##############################################################################
# 1a. Read in the client submitted disch file into dfDisch & print record count.
print('-'*80)
print('STEP 1: BEGIN DISCHARGE FILE PROCESSING SEGMENT')
print('-'*80,'',sep='\n')
print(f'Importing the disch file - {path_src}/{file_disch} - to dfDisch',sep='\n')
dfDisch = pd.read_csv(f'{path_src}/{file_disch}', sep='|', dtype=str)
print(f'{dfDisch.shape[0]:,g} records were imported into dfDisch.','',sep='\n')
# List the column names for log and checking
print('dfDisch info includes:')
print(dfDisch.info(verbose=True, show_counts=True),sep='\n')

# 1b. Check for duplicate PCNs in dfDisch as there should be none.
#  This check should be done on this file before any file processing
#  If dups are found, then dfDisch is dedupped 
#  Check with Riley on this
dup_count = dfDisch.duplicated(subset=["PROVNUM","PCN"]).sum()
print()
print('Checking for duplicate PCNs per PROVNUM in dfDisch')
if dup_count > 0:
    print(f'dfDisch has {dup_count} duplicates')
    print('', f'Dropping {dfDisch.duplicated().sum():,} FULL duplicates',sep='\n')
    dfDisch.drop_duplicates(inplace=True)
    print(f'dfDisch contains {dfDisch.shape[0]:,g} records after dedupping.',sep='\n')
else: 
    print(f'There were {dup_count} duplicates in dfDisch which is expected.')
del dup_count # removing the variable after if function finishes
print()

# 1c. Check for null values and pt attribute field distributions.
#  First print patient attribute reports to check for null rows
print('''Checking for significant numbers of null values per column.
 Columns where nulls are ok are the 5 phy fields.
 Should not see large numbers of nulls in other fields.
 If needed, update nulls with default values of Information not available 
  for ADMSRC, ADMTYPE & PAYCODE1.
..
Null counts by field are:''')
print(dfDisch.isna().sum(),sep='\n')
print()

#  Null update procedures if needed for ADMSRC, ADMTYPE & PAYCODE1 
#  set null count variables
ADMSRC_nan = dfDisch['ADMSRC'].isna().sum()
ADMTYPE_nan = dfDisch['ADMTYPE'].isna().sum()
PAYCODE1_nan = dfDisch['PAYCODE1'].isna().sum()
#  run through each of these fields to replace nulls with not available values
#  then delete the null variable
if ADMSRC_nan > 0:
    dfDisch['ADMSRC'] = dfDisch['ADMSRC']. fillna('9')
    print(f'{ADMSRC_nan} ADMSRC null records were replaced with the value 9.',sep='\n')
    del ADMSRC_nan
if ADMTYPE_nan > 0:
    dfDisch['ADMTYPE'] = dfDisch['ADMTYPE']. fillna('9')
    print(f'{ADMTYPE_nan} ADMTYPE null records were replaced with the value 9.',sep='\n')
    del ADMTYPE_nan
if PAYCODE1_nan > 0:
    dfDisch['PAYCODE1'] = dfDisch['PAYCODE1']. fillna('90')
    print(f'{PAYCODE1_nan} PAYCODE1 null records were replaced with the value 90.',sep='\n')
    del PAYCODE1_nan
print()

#  print final counts & distributions of patient attribute fields for logging.
#  create a field list for iterating through the fields of interest.
FieldToPrint = ['ADMSRC', 'ADMTYPE', 'STATUS', 'RACE', 'PAYCODE1']
#  now print record counts and distributions by value for each field
for i in FieldToPrint:
    print('The '+i+' record distribution count is:')
    print(dfDisch[i].value_counts(dropna=False),'',sep='\n')
    print('The '+i+' record distribution % is:')
    print(dfDisch[i].value_counts(normalize=True, dropna=False),'',sep='\n')
del i # removing the variable after loop finishes

# 1d. Create a new record key column called PROVNUM_PCN for merging later
dfDisch['PROVNUM_PCN'] = dfDisch['PROVNUM'] +'_'+dfDisch['PCN']
print('A new column key, PROVNUM_PCN, was created from PROVNUM + PCN.','',sep='\n')

# Show sample output of dfDisch for log
print('','Final dfDisch sample output:')
print(dfDisch.head(),'', sep='\n') 
print('Disch file processing is complete!','',sep='\n')

##############################################################################
# 2. DX file import and pivot processing
# 2a. Read in the client submitted DX file as the dataframe dfDX
# 2b. Check for duplicates and drop if necessary.
# 2c. Check for nulls in all fields and DXSQN & DXPOA frequencies.
# 2d. Create column key to use for merging with dx and px files later.
# 2e. Check for maximun DXSQN and format as 4800 expects 41 DXSQN positions
# 2f. Pivot dfDX in dfDXFlat, rename columns & if needed, add additioanl DX fields
##############################################################################

# 2a. Read in the client submitted dx file into dfDX & print record count.
print('-'*80)
print('STEP 2: BEGIN DIAGNOSIS FILE PROCESSING SEGMENT')
print('-'*80,'',sep='\n')
print(f'Import the dx file - {path_src}/{file_dx} - to dfDX.','',sep='\n')
dfDX = pd.read_csv(f"{path_src}/{file_dx}", sep='|', dtype=str)
print(f'{dfDX.shape[0]:,g} records were imported into dfDX.',sep='\n')
# List the column names for log and checking
print('dfDX info includes:')
print(dfDX.info(verbose=True, show_counts=True),'',sep='\n')

# 2b. Check for duplicate PROVNUM/PCN/DX_SQNs in dfDX as there should be none.
# This check should be done on this file before any file processing
# If dups are found, then dfDisch is dedupped 
dup_count = dfDX.duplicated(subset=["PROVNUM","PCN","DXSQN"]).sum()
print('Checking for duplicate PROVNUM/PCN/DXSQN in dfDX')
if dup_count > 0:
    print(f'dfDX has {dup_count} duplicates')
    print('', f'Dropping {dfDX.duplicated().sum():,} FULL duplicates',
          '',sep='\n')
    dfDX.drop_duplicates(inplace=True)
    print(f'After dedupping, dfDX contains {dfDX.shape[0]:,g} records.' )
else: 
    print(f'There were {dup_count} duplicates in dfDX which is expected.',
          '',sep='\n')
del dup_count # removing the variable after if function finishes

# 2c. Check for null values and DXSQN & DXPOA distributions.
#  null check
print('''Checking for significant numbers of null values per column.
 We do not expect any.
Null counts by field are:''')
print(dfDX.isna().sum(),sep='\n')
print()

#  DX Seqence Number Frequency check
#  is problematic if only the first few dx seq num position are populated
print('''Checking the DXSQN frequency. 
We expect a large number of DXSQN positions to have data 
with counts getting progressively lower in higher number DXSQNs.

The DX Seq Num record distribution count is:''')
print(dfDX['DXSQN'].value_counts(dropna=False),'',sep='\n')
print('The DX Seq Num record distribution % is:')
print(dfDX['DXSQN'].value_counts(normalize=True, dropna=False),'',sep='\n')

#  DX POA fill rate check
#  expect POA = Y and 1 distribution to > 90%
print()
print('''Checking the DXPOA fill rate. 
We expect the POA = Y & 1 to be around >=90%. 

The DX POA record distribution count is:''')
print(dfDX['DXPOA'].value_counts(dropna=False),'',sep='\n')
print('The DX POA record distribution % is:')
print(dfDX['DXPOA'].value_counts(normalize=True, dropna=False),'',sep='\n')

# 2d. create a new record key column called PROVNUM_PCN &
#     format DXSQN to int
dfDX['PROVNUM_PCN'] = dfDX['PROVNUM'] +'_'+dfDX['PCN']
# convert the diagnoasis sequnce number (DXSQN) to interger
dfDX['DXSQN'] = dfDX['DXSQN'].astype(int)
print('A new column key, PROVNUM_PCN, was created from PROVNUM + PCN.')
print('The dx sequence column, DXSQN, was changed to an interger type.',
      '',sep='\n')

# Print sample outpiut
print('Sample output:')
print(dfDX.head(),'',sep='\n') 

# 2e. DXSQN formatting
#  determine max diagnosis sequence submitted stored as a variable
max_dx_seq = dfDX['DXSQN'].max()
print(f'The max dx seq number submitted in the DX file is {max_dx_seq}.',
      '',sep='\n')

#  runs only if DXSQN > 41 (4800 accomodates up to 41 DXSQN positions)
#   if client provides dx sequence numbers greater than 41
#   then this will keep only rows in dfDX where DXSQN < 42
if max_dx_seq > 41:
    dfDX = dfDX.loc[dfDX['DXSQN']<42]
    dfDX_count = dfDX.shape[0]
    print(f'Since the client submitted a max dx seq number of {max_dx_seq}')
    print('which exceeds the 41 dx positions supported in the 4800 format,')
    print('those excess records have been removed from dfDX')
    # count the number of rows in dfDX after truncation
    dfDX_count = dfDX.shape[0]
    # print the record count in dfDX after removing dxseq >41
    print(f'Total dx records remaining in dfDX = {dfDX.shape[0]:,g}',
          '',sep='\n')
    
# 2f. Pivot the records in dfDX into a wide format as dfDXFlat
#    this produces a wide dataframe but with dual column names (DX and seq#) 
dfDXFlat = dfDX.pivot(index='PROVNUM_PCN', 
                      columns='DXSQN', values= ['DX','DXPOA'])

#   Collapse the dual column names into a single row
#   Also reset seq number range to start with 0 instead of 1
#   This is done because sec dx code seq begins with 1
dfDXFlat.columns = [f'{c[0]}{c[1]-1}' for c in dfDXFlat.columns]

#   print the record count in dfDXFlat 
print("""
dfDX has been pivoted into a flattened dataframe, dfDXFlat:
 - The dual columns were collapsed into single column names.
 - The seq numbers in fields reset to start with 0 rather than 1. """)
print(f'The total records in dfDXFlat = {dfDXFlat.shape[0]:,g}','',sep='\n')

#   rename dx columns to match 4800 column name requirements
#   First rename the principal dx and POA field names
dfDXFlat.rename(columns = {'DX0':'PRDIAG'}, inplace = True)
dfDXFlat.rename(columns = {'DXPOA0':'PRDIAGPOA'}, inplace = True)
#   For the rest of the columns, replace DX with SECDX
dfDXFlat.columns = dfDXFlat.columns.str.replace('DX','SECDX')
#   Finally, rename the SECDXPOA# columns using a loop 
for i in range(1,max_dx_seq):
    dfDXFlat.rename(columns = {f'SECDXPOA{i}':f'SECDX{i}POA'}, inplace = True)
del i # removing the variable after loop finishes
# print what was done
print("""
The dfDXFlat dataframe column names have been been formatted:
 - The principal dx and POA columns were renamed.
 - All secondary dx and poa columns were renamed.
""")

#   If needed, add the additional secondary dx columns to meet 4800 requirements.
if max_dx_seq < 41:
    # loop to add the dx code and POA positions
    for i in range(max_dx_seq,41):
        dfDXFlat[f"SECDX{i}"] = ""
        dfDXFlat[f"SECDX{i}POA"] = ""
    del i # removing the variable after loop finishes
    print(f'Added {40-max_dx_seq} dx code and POA fields as null')
    print('to meet 4800 requirements')
    print(f'The starting seq num for missing dx fields = {max_dx_seq}',
          '',sep='\n')

# List the column names for log checking
print("dfDXFlat now contains these columns.")
print(dfDXFlat.info(verbose=True),sep='\n')

#   compute the difference in records between dfDisch and dfDXFlat
#   df_count_rows - dfDXFlat_count_rows
#   set variables
dfDisch_count = dfDisch.shape[0]
dfDXFlat_count = dfDXFlat.shape[0]
disch_to_dx_diff = dfDisch_count - dfDXFlat_count
# dx_fill_rate
dx_fill_rate = format((dfDXFlat_count/dfDisch_count)*100, "2f")

if disch_to_dx_diff == 0:
    print()
    print('Both dfDisch and dfDXFlat dataframes have the same record count')
    print(f' of {dfDisch_count:,g}. This is expected.','',sep='\n')
elif disch_to_dx_diff > 0:
    print()
    print(f'dfDXFlat has {disch_to_dx_diff} less records than dfDisch')
    print(f'which is {dx_fill_rate}% of total discharges.') 
    print('This rate should be at least 99% so check if less than this.',
          '',sep='\n')
elif disch_to_dx_diff < 0:
    print()
    print(f'dfDisch has {-1 * disch_to_dx_diff} less records than dfDXFlat')
    print('This is generally not an issue if small as we only use ') 
    print('encounters included in the disch file.','',sep='\n')

# Show sample output of dfDXFlat for log
print('Final dfDXFlat sample output:')
print(dfDXFlat.head(),'', sep='\n') 
print('DX file processing is complete!','',sep='\n')

#############################################################################

##############################################################################
# 3. PX file import and pivot processing
# 3a. Read in the client submitted PX file as the dataframe dfPX
# 3b. Check for duplicates and drop if necessary.
# 3c. Check for nulls in all fields and PRCSQN frequencies.
# 2d. Create column key to use for merging with dx and px files later.
# 2e. Check for maximun PRCSQN and format as 4800 expects 31 PRCSQN positions
# 2f. Pivot dfPX in dfPXFlat, rename columns & if needed, add additioanl PX fields
##############################################################################
# PX file import and processing
# Read in the client submitted PX file as the dataframe dfPX
print('-'*80)
print('STEP 3: BEGIN PROCEDURE FILE PROCESSING SEGMENT')
print('-'*80,'',sep='\n')
print(f'Import the px file - {path_src}/{file_px} - to dfPX','',sep='\n')
dfPX = pd.read_csv(f"{path_src}/{file_px}", sep='|', dtype=str)
print(f'{dfPX.shape[0]:,g} records were imported into dfPX.','',sep='\n')
# List the column names for log and checking
print('dfPX info includes:')
print(dfPX.info(verbose=True, show_counts=True),sep='\n')

# 3b. Check for duplicate PROVNUM/PCN/PXSQNs in dfPX as there should be none.
# This check should be done on this file before any file processing
# If dups are found, then dfPX is dedupped 
dup_count = dfPX.duplicated(subset=["PROVNUM","PCN","PRCSQN"]).sum()
print()
print('Checking for duplicate PROVNUM/PCNs/PRCSQN in dfPX')
if dup_count > 0:
    print(f'dfPX has {dup_count} duplicates')
    print('', f'Dropping {dfPX.duplicated().sum():,} FULL duplicates','',sep='\n')
    dfPX.drop_duplicates(inplace=True)
else: 
    print(f'There were {dup_count} duplicates in dfPX which is expected.',
          '',sep='\n')
del dup_count

# 3c. Check for null values and DXSQN & DXPOA distributions.
#  null check
print('''Checking for significant numbers of null values per column.
We do not expect any.
 
Null counts by field are:''')
print(dfPX.isna().sum(),sep='\n')
print()

#  PX Seqence Number Frequency check
#  Though PX fill rates are lower than DX fill rates, it is is problematic
#    if only the first few Px seq num position are populated
print('''Checking the PRCSQN frequency. 
We expect PRCSQN positions to have data 
with counts getting progressively lower in higher number PRCSQNs

The PX Seq Num record distribution count is:''')
print(dfPX['PRCSQN'].value_counts(dropna=False),'',sep='\n')
print('The PX Seq Num record distribution % is:')
print(dfPX['PRCSQN'].value_counts(normalize=True, dropna=False),'',sep='\n')

# 3d.create a new record key column as PROVNUM_PCN
dfPX['PROVNUM_PCN'] = dfPX['PROVNUM'] +'_'+dfPX['PCN']
# convert the procedure sequnce number (pxSQN) to interger
dfPX['PRCSQN'] = dfPX['PRCSQN'].astype(int)
print("""A new column key, PROVNUM_PCN, was created from PROVNUM + PCN.
The px sequence column, PRCSQN, was changed to an interger type.
""")

# Print sample outpiut
print('Sample output:')
print(dfPX.head(),'',sep='\n')

# 3e. PRCSQN formatting
# determine max procedure sequence submitted stored as a variable
# If that number is greater than 31, then remove records where px seq > 31
max_px_seq = dfPX['PRCSQN'].max()
print(f'The max px seq number submitted in the PX file is {max_px_seq}.')

#  runs only if PRCSQN > 31 (4800 accomodates up to 31 PRCSQN positions)
#   keep only those detail records where PRCSQN =< 31 (4800 max allowed PXes)
#   if client provides px sequence numbers greater than 31
#   then this will keep only rows in dfPX where PRCSQN < 32
if max_px_seq > 31:
    dfPX = dfPX.loc[dfPX['PRCSQN']<32]
    dfPX_count = dfPX.shape[0]
    print(f'Since the client submitted a max px seq number of {max_px_seq}')
    print('which exceeds the 31 dx positions supported in the 4800 format,')
    print('those excess records have been removed from dfPX')
    # count the number of rows in dfPX after truncation
    dfPX_count = dfPX.shape[0]
    # print the record count in dfPX 
    print(f'Total dx records remaining in dfPX = {dfPX_count}','',sep='\n')

# 3f. Pivot the records in dfPX into a wide format as dfPXFlat
#   this produces a wide dataframe but with dual column names 
dfPXFlat = dfPX.pivot(index='PROVNUM_PCN', 
                      columns='PRCSQN', values= ['PROC','PRCDATE'])

#   Collapse the dual column names into a single row
#   Also reset seq number range to start with 0 instead of 1
#   is necessary because the sec PX code fields begin with 1 thru 30
dfPXFlat.columns = [f'{c[0]}{c[1]-1}' for c in dfPXFlat.columns]

#   print what was done and the record count in dfPXFlat 
print("""
dfPX has been pivoted into a flattened dataframe, dfPXFlat
 - The dual columns were collapsed into single column names.
 - The seq numbers in fields reset to start with 0 rather than 1.""")
print(f'The total records in dfPXFlat after pivoting = {dfPXFlat.shape[0]:,g}',
      '',sep='\n')

#   Rename px columns to match 4800 column names
#   First modify all px and px date field names 
dfPXFlat.columns = dfPXFlat.columns.str.replace('PRCDATE','SECDAT')
dfPXFlat.columns = dfPXFlat.columns.str.replace('PROC','SECPRC')
#   Now rename px columns with 0 seq to 4800 principal px names
dfPXFlat.rename(columns = {'SECPRC0':'PRPROC', 'SECDAT0':'PRPRDATE'}, inplace = True)

#   explain what has been changed to dxPXFlat
print("""The dfPXFlat dataframe column names have been been formatted:
 - The principal px and date columns renamed.
 - All existing secondary px and date columns renamed.
 """)

#   If needed, add the additional secondary px columns to meet 4800 requirements.
#     Note, most clients do not submit more than 31 px codes for an encounter.
if max_px_seq < 31:
    # loop to add the px code and date positions
    for i in range(max_px_seq, 31):
        dfPXFlat[f"SECPRC{i}"] = ""
        dfPXFlat[f"SECDAT{i}"] = ""
    del i # removing the variable after loop finishes
    print(f'Added {30-max_px_seq} px code and date fields as null')
    print('to meet 4800 requirements')
    print(f'The starting seq num for missing px fields = {max_px_seq},',
          '',sep='\n')

# List the column names for log checking
print("dfPXFlat now contains these columns.")
print(dfPXFlat.info(verbose=True),'',sep='\n')

#   compute the difference in records between dfDisch and dfPXFlat
#   in most cases, there will be fewer px records to disch records
#   we expect around a 60% fill rate but it can sometimes be less
#   if less than 60, check with the PM and business analyst.
#   df_count_rows - dfPXFlat_count_rows
dfPXFlat_count = dfPXFlat.shape[0]
disch_to_px_diff = dfDisch_count - dfPXFlat_count
#    px_fill_rate
px_fill_rate = format((dfPXFlat_count/dfDisch_count)*100, ".2f")

if disch_to_px_diff == 0:
    print('Both dfDisch and dfPXFlat dataframes have the same record count')
    print(f' of {dfDisch_count:,g} which is unusual but not an error.',
          '',sep='\n')
elif disch_to_px_diff > 0:
    print(f'dfPXFlat has {disch_to_px_diff:,g} less records than dfDisch.')
    print(f' Thus, {px_fill_rate}% of discharges have one or more procedures.') 
    print('This rate should be close to 60% so check if materially less.',
          '',sep='\n')
elif disch_to_dx_diff < 0:
    print(f'dfDisch has {-1 * disch_to_px_diff:,g} less records than dfPXFlat')
    print('This rarely occurrs - not an issue if small as we only use ') 
    print('encounters included in the disch file.','',sep='\n')

# Show sample output of dfPXFlat for log
print('Final dfPXFlat sample output:')
print(dfPXFlat.head(),'', sep='\n') 
print('PX file processing is complete!','',sep='\n')

##############################################################################
# 4. Merge dfDisch, dfDXFlat and dfPXFlat and create 4800 flat file
##############################################################################

print('-'*80)
print('STEP 4: BEGIN DF MERGES AND 4800 FILE CREATION SEGMENT')
print('-'*80,'',sep='\n')
df4800 = pd.merge(dfDisch, 
    dfDXFlat, left_on=['PROVNUM_PCN'], right_on=['PROVNUM_PCN'], 
    how='left', indicator=True)
print('dfDisch and dfDXFlat merge')
print('df4800 has been created by merging dfDisch and dfDXFlat (left join).')
print('The results of that merge are:')
print(df4800['_merge'].value_counts(),'',sep='\n')
df4800.drop('_merge', axis=1,inplace=True)

df4800 = pd.merge(df4800, 
     dfPXFlat, left_on=['PROVNUM_PCN'], right_on=['PROVNUM_PCN'], 
     how='left', indicator=True)
print('df4800 and dfPXFlat merge')
print('dfPXFlAT (left join) has been merged to df4800')
print('The results of that merge are:')
print(df4800['_merge'].value_counts(),'',sep='\n')
df4800.drop('_merge', axis=1,inplace=True)
df4800.drop('PROVNUM_PCN', axis=1,inplace=True)

# print the record count in df4800 
print(f'The total records in df4800 = {df4800.shape[0]:,g}.','',sep='\n')

# add the 50 revcode and charge positions
for i in range(1,51):
    df4800[f"REVCOD{i}"] = ""
    df4800[f"CHARGE{i}"] = ""
del i # removing the variable after loop finishesprint()

# 3. Reorder fields to meet 4800 output requirements
df4800 = df4800.reindex(columns=
            ['PROVNUM', 'PCN', 'MRN', 'SPTTYPE', 'ADMDATE', 'DISDATE',
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
# Summarize the changes
print('''All charge fields have been added to df4800 for 1 thru 50 as null
and df4800 columns have been reordered to meet requirements.''')

# Check for duplicate PCNs in df4800 as there should be none.
# Probably not needed but have left this check in for safety
# If dups are found, then df4800 is dedupped 
# Check with Riley on this
dup_count = df4800.duplicated(subset=["PROVNUM","PCN"]).sum()
print('','Checking for duplicate PROVNUM/PCNs in df4800', sep='\n')
if dup_count > 0:
    print(f'df4800 has {dup_count} duplicates.')
    print(f'Dropping {df4800.duplicated().sum():,} FULL duplicates','',sep='\n')
    df4800.drop_duplicates(inplace=True)
else: 
    print(f'There were {dup_count} duplicates in df4800 which is expected',
          '',sep='\n')

# Report date distributions for new data
print('-'*27, 'Date distribution of new data:',
      pd.to_datetime(df4800['DISDATE'],format='%m%d%Y').describe(datetime_is_numeric=True)
,'', sep='\n')

print('df4800 is now 4800 compliant. Should see 264 columns.','',sep='\n')
print(df4800.info(),'',sep='\n')
print('df4800 sample output:')
print(df4800.head(),'',sep='\n')

# export the final file
print('Exporting df4800 to a 4800 pipe-delimited text file.')
df4800.to_csv(f"{path_src}\\{file_4800}", index=False, sep='|', na_rep='')
print()
# now count the number of rows in the exported 4800 file.
with open(f'{path_src}\\{file_4800}', 'r') as fp:
    num_lines = sum(1 for line in fp)
print()
print(f'''Using the reformatted df4800, the pipe-delimited text file, {file_4800},
located in {path_src}
has been created and contains {num_lines:,g} lines including a header row.
Check the file visually before using.''')
del num_lines
print()
print()
print('The 4800 split file conversion program is complete.')