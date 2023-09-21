##############################################################################
# 4800 DQR flat file processing code
# @author: Jim Cheairs

# This python script creates four dataframes used to populate the 4800 Access process.
#  connects to the Access database and truncates tables.
#  imports client 4800 file into df4800.
#  creates and formats an encounter df and inserts into Access table
#  creates and formats a DX long and narrow df for Access.
#  creates and formats a PX long and narrow df for Access.
##############################################################################

##############################################################################
# Set up Instructions
# This program can be run from a local PC machine or unix.
# Several variables need to be entered for path and file locations.
##############################################################################


import pandas as pd
import time as time
import os
import datetime
import pyodbc
import tempfile
import shutil
import win32com.client

# Start off with some good log information...
# start_time=datetime.datetime.now()
start_time = time.time()

print('*'*80)
print(f"""SYSTEM INFORMATION
Username:  {os.getlogin()}
Run start time: {datetime.datetime.now()}
""")

print("""---------------------------------------------------------------------
This procedure produces dataframes that are used to populate MS Access 
tables that are then used to populate the Excel DQR report for CQD clients.

The processing steps include:
 1. Set variables
 2. Client file import, quality checks & dedup if necessary.
 3. dfDisch creation and DISCH_TEMP table insertion.
 4. dfDxFinal creation (long and narrow format) into DX_TEMP table
 4. dfPxFinal creation (long and narrow format) into PX_TEMP table
 5. dfPhy creation into R_PHY table
 --------------------------------------------------------------------------""")
print()
print('*'*80)
print('STEP 1: SET VARIABLES, CONNECT TO ACCESS AND TRUNCATE TABLES.')
print('*'*80,'',sep='\n')

# 1. set the working directories, import files and export file variables
#   be sure path directories use forward slashes.
# Client specific source data
path_src = 'C:/PHI/Projects/FirstHealth/16th Refresh 202310/Client Data'
file_orig = 'FirstHealth_4800_20230701_20230831.txt'
file_phy = 'ref_phy.txt'

# standard patent attribute reference files
path_ref = 'C:/PHI/Projects/CQD/StdRefFiles'
file_ras = "ref_adm_src_4800.txt"
file_rat = "ref_adm_type_4800.txt"
file_rstatus = "ref_disch_status_4800.txt"
file_rpay = "ref_payer_4800.txt"
file_rrace = "ref_race.txt"

# Access database path
path_db = 'C:/PHI/Projects/CQD/Data Intake/4800_DQR'
file_accdb = '4800.accdb'

# variable for adding HCO name to 4800
hosp_name = 'FirstHealth'

# print the variables for logging
print('Variable Assignments:', '', sep='\n')
print(f'Source file directory: {path_src}')
print(f'disch import file: {file_orig}','',sep='\n')
print(f'Access file directory: {path_db}','',sep='\n')

print(f'Ref file directory: {path_ref}')
print(f'Admit Source Ref file: {file_ras}')
print(f'Admit Type Ref file: {file_rat}')
print(f'Disch Status Ref file: {file_rstatus}')
print(f'Payer Ref file: {file_rpay}')
print(f'Race Ref file: {file_rrace}','',sep='\n')

# print(f'disch export file: {file_disch}')
# print(f'disch nh export file: {file_disch_nh}','',sep='\n')

# Create Access connection string
print(f'Connecting to the {file_accdb} Access database.','',sep='\n')
access_db_file = path_db +'/' + file_accdb
connection_str = 'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={}'.format(access_db_file)
conn = pyodbc.connect(connection_str)
cursor = conn.cursor()
print('Connection successful!')

# Table Truncation
# List of table names you want to truncate
print('Created a list of Access table names for truncation.')
db_tables = ['DISCH_TEMP',
               'DX_TEMP',
               'PX_TEMP',
               'DX_TEMP_AGG',
               'PX_TEMP_AGG',
               'DX_TEMP_POA_YR_QTR',
               'DX_PX_TEMP_SUMMARY',
               'R_PHY',
               'R_PHY_SUMMARY',
               'DATE_RANGES',
               'StdAttributes']
for item in db_tables:
    print(item)
print()

# Iteration to Truncate each table by deleting all records.
print('Iterating through db_tables and truncating each table.','',sep='\n')
for table in db_tables:
    cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    time.sleep(1)
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    num_rows = cursor.fetchone()[0]
    print(f'{table} has been truncated and contains {num_rows:,g} records.')
print()

# close the connection
conn.close()
print(f'The {file_accdb} database has been closed.','',sep='\n')

# Compact and repair the database after table truncation
# Compact & repair function 
def compact_and_repair(database_path):
    # Create a temporary file to store the compacted database
    tmp_dir = tempfile.gettempdir()
    compacted_db_path = os.path.join(tmp_dir, 'compacted_database.accdb')

    # Access application instance
    access_app = win32com.client.Dispatch("Access.Application")

    # Compact and repair the database
    access_app.CompactRepair(database_path, compacted_db_path)

    # Close the Access application
    access_app.Quit()

    # Replace the original database with the compacted one
    shutil.move(compacted_db_path, database_path)

# Run the function
print('Compacting the database after all tables truncated.','',sep='\n')
compact_and_repair(path_db + '/' + file_accdb)
print(f'The {file_accdb} database has been compacted successfully.','',sep='\n')

##############################################################################
# 2. 4800 File Import & Preprocessing
##############################################################################

print('*'*80)
print('STEP 2: IMPORT CLIENT 4800 AND REF_PHY FILES AND FORMAT')
print('*'*80,'',sep='\n')

# 2a. Read in the client submitted 4800 file into df4800 & check quality.
#  Read in only col 1 thru 164 - excludes detail charges
print(f'Importing {path_src}/{file_orig} to df4800.','',sep='\n')
df4800 = pd.read_csv(f"{path_src}/{file_orig}", sep='|', dtype=str)

print(f'{df4800.shape[0]:,g} records were imported into df4800.', '', sep='\n')
# Report date distributions for new data
print('-'*27, 'Date distribution of df4800:',
    pd.to_datetime(df4800['DISDATE'], 
    format='%m%d%Y').describe(datetime_is_numeric=True), '', sep='\n')
# List the column names for log and checking
print('''Use this df4800 info report to check distributins by field.
Total records should be the same for PROVNUM, PCN, MRN, ADMDATE, DISDATE, TOTALCLM, DOB
For DX and PX sequenced fields, should see a large number of fields to have 
data with counts getting progressively lower in higher number seq numbers.
    ''')
print(df4800.info(verbose=True, show_counts=True), sep='\n')

# 2b. Check for duplicate PCNs in df4800 as there should be none.
#  If dups are found, then df4800 is dedupped
dup_count = df4800.duplicated(subset=["PROVNUM", "PCN"]).sum()
print()
print('Checking for duplicate PCNs per PROVNUM in df4800')
if dup_count > 0:
    print(f'df4800 has {dup_count} duplicates')
    print(
        '', f'Dropping {df4800.duplicated().sum():,} FULL duplicates', sep='\n')
    df4800.drop_duplicates(inplace=True)
    print(
        f'df4800 contains {df4800.shape[0]:,g} records after dedupping.', sep='\n')
else:
    print(f'There were {dup_count} duplicates in df4800 which is expected.')
del dup_count  # removing the variable after if function finishes
print()


#  2d.print final counts/distributions of patient attribute fields for logging.
#  create a field list for iterating through the fields of interest.
FieldToPrint = ['ADMSRC', 'ADMTYPE', 'STATUS', 'RACE', 'PAYCODE1', 'SEX']
#  now print record counts and distributions by value for each field
for i in FieldToPrint:
    print('The '+i+' record distribution count is:')
    print(df4800[i].value_counts(dropna=False), '', sep='\n')
    print('The '+i+' record distribution % is:')
    print(df4800[i].value_counts(normalize=True, dropna=False), '', sep='\n')
del i  # removing the variable after loop finishes

#  2e. Replace POA values of 'E' with '1' in all dx poa fields.
df4800['PRDIAGPOA'] = df4800['PRDIAGPOA'].replace('E', '1', regex=False)
for i in range(1, 41):
    df4800['SECDX'+str(i)+'POA'] = df4800['SECDX'+str(i) +
                                          'POA'].replace('E', '1', regex=False)
del i  # removing the variable after loop finishes
print('The PDX and SecDX POA E values have been replaced with 1.', '', sep='\n')

# 2f. Other 4800 formattimg
# Add HCO name to df4800
df4800['Facility Name'] = hosp_name


#  final df4800 info check
print('df4800 is now 4800 compliant. Should see 266 columns.', '', sep='\n')
print(df4800.info(), '', sep='\n')
print('df4800 sample output:')
print(df4800.head(), '', sep='\n')

# provide basic counts for df4800
print('Number of unique PROVNUMs in df4800. Expecting 42 rows')
HCO_COUNT = df4800[['PROVNUM']].nunique()

print(HCO_COUNT,'',sep='\n')
print('Record counts by PROVNUM - FYI only')
print(df4800.groupby(['PROVNUM'])['PCN'].count(), '', sep='\n')


# Read in all standard reference files
print("Reading in all standard reference files into dataframes.")
print("  ")
dfRadmsrc = pd.read_csv(f"{path_ref}/{file_ras}", sep='|', dtype=str)
dfRadmtype = pd.read_csv(f"{path_ref}/{file_rat}", sep='|', dtype=str)
dfRstatus = pd.read_csv(f"{path_ref}/{file_rstatus}", sep='|', dtype=str)
dfRpay = pd.read_csv(f"{path_ref}/{file_rpay}", sep='|', dtype=str)
dfRrace = pd.read_csv(f"{path_ref}/{file_rrace}", sep='|', dtype=str)

# Merge ref data to df4800
# Create a list of tuples, where each tuple contains a reference DataFrame
# and the column name to merge on
ref_data = [(dfRadmsrc, 'ADMSRC', 'admit source description', 'dfRadmsrc'),
            (dfRadmtype, 'ADMTYPE', 'admit type description', 'dfRadmtype'),
            (dfRpay, 'PAYCODE1', 'Payer Description', 'dfPay'),
            (dfRstatus, 'STATUS', 'disch status description', 'dfRstatus'),
            (dfRrace, 'RACE', 'Race Description', 'dfRrace')]


# Now add patient attribute titles to df4800
for ref_df, column, field, df in ref_data:
    df4800 = pd.merge(df4800, ref_df, on=column, how='left', indicator=True)
    print(f'Added the {field} to df4800 by merging to {df}')
    print(f'via a left join on {column}') 
    # print merge results
    print(df4800['_merge'].value_counts(),'',sep='\n')
    df4800.drop('_merge', axis=1, inplace=True)
    
# Add the sex description column to df4800
# create mapping dictionary
sex_mapping = {'M': 'Male',
               'F': 'Female',
               'U': 'Unknown',
               '': 'Blank'}    
# create Sex Descriptopn column
df4800['Sex Description'] = df4800['SEX'].map(sex_mapping)

# create attribute summary for admsrc, admtype, status amnd payer and sex
attrb_pairs = [
    ['Facility Name', 'ADMSRC', 'Admit Src Description', 'Admit Source'],
    ['Facility Name', 'ADMTYPE', 'Admit Type Description', 'Admit Type'],
    ['Facility Name', 'PAYCODE1', 'Payer Description', 'Payer'],
    ['Facility Name', 'STATUS', 'Disch Status Description', 'Discharge Status'],
    ['Facility Name', 'SEX', 'Sex Description', 'Sex'],
    ['Facility Name', 'RACE', 'Race Description', 'Race']
    ]

dfAttributes = []

for fac, code, title, attribute in attrb_pairs:
    dfAttribute = df4800.groupby([fac, 
             code, title]).size().reset_index(name='Cases')
    total_count = dfAttribute['Cases'].sum()
    dfAttribute['Percent of Cases'] = (dfAttribute['Cases'] / total_count) * 100
    dfAttribute['Attribute'] = attribute
    dfAttribute.columns = ['Facility', 'Code', 'Code Descriptiopn',
                       'Cases', 'Percent of Cases', 'Attribute']
    # create a total row
    total_row = pd.DataFrame
    dfAttributes.append(dfAttribute)

# Concatenate all aggregated dataframes
dfAttributeFinal = pd.concat(dfAttributes, ignore_index=True)
# replace NaN values with blanks
dfAttributeFinal = dfAttributeFinal.fillna('')

# 2g. Read in the client submitted ref_phy file into dfPhy & check contents.
print(f'Importing {path_src}/{file_phy} to dfPhy.','',sep='\n')
dfPhy = pd.read_csv(f"{path_src}/{file_phy}", sep='|', dtype=str)
# fill NaN values with blanks
dfPhy = dfPhy.fillna('')

print(f'{dfPhy.shape[0]:,g} records were imported into dfPhy.', '', sep='\n')


##############################################################################
# 3. Create dfDisch encounter file for populating DX_TEMP in Access.
##############################################################################
print('*'*80)
print('STEP 3: Create dfDisch encounter file. ')
print('*'*80,'',sep='\n')

# Create Disch_IMP by selecting a few cols from df4800
print('Creating dfDisch...','',sep='\n')

dfDisch = df4800.loc[:,['PROVNUM',
                  'PCN',
                  'MRN',
                  'ADMDATE',
                  'DISDATE',
                  'TOTALCLM',
                  'PRDIAG',
                  'PRPROC',
                  'SEX',
                  'RACE',
                  'ADMTYPE',
                  'ADMSRC',
                  'STATUS',
                  'PAYCODE1',
                  'DOB',
                  'ATTMD',
                  'OPERMD']].copy()

print(f'dfDisch contains {dfDisch.shape[0]:,g} records.') 
print(f' which should equal {df4800.shape[0]:,g} records in df4800',sep='\n')
print(dfDisch.info(), '', sep='\n')
print('dfDisch sample output:')
print(dfDisch.head(), '', sep='\n')

# Rename a few columns
dfDisch = dfDisch.rename(columns={
    'PAYCODE1': 'PAYER',
    'PRDIAG': 'PDX',
    'PRPROC': 'PPX'})

#  Apply field formats and create additional fields needed for Access tables.
print('Updating date fields and creating Year, Quarter and Month fields.','',sep='\n')
dfDisch['ADMDATE'] = pd.to_datetime(dfDisch['ADMDATE'], format='%m%d%Y')
dfDisch['DISDATE'] = pd.to_datetime(dfDisch['DISDATE'], format='%m%d%Y')
dfDisch['DOB'] = pd.to_datetime(dfDisch['DOB'], format='%m%d%Y')
dfDisch['Disch_Year'] = dfDisch['DISDATE'].dt.year
dfDisch['Disch_Qtr'] = dfDisch['DISDATE'].dt.quarter
dfDisch['Disch_Month'] = dfDisch['DISDATE'].dt.month

# Create additional Fields
dfDisch['TOTALCLM'] = dfDisch['TOTALCLM'].astype(float)
dfDisch['Discharges'] = 1

dfDisch['Cases_w_PDX'] = dfDisch['PDX'].notnull().astype(int)
dfDisch['Cases_w_PPX'] = dfDisch['PPX'].notnull().astype(int)

#create LOS column
dfDisch['LOS'] = (dfDisch['DISDATE'] - dfDisch['ADMDATE']).dt.days
# Count the number of occurrences that are 0
LOS_zero = dfDisch['LOS'].eq(0).sum()
# Print the count
print(LOS_zero)
# change zeroes to 1 to match what databrdige does when processing
dfDisch['LOS'] = dfDisch['LOS'].apply(lambda x: 1 if x == 0 else x)
#check replacements
LOS_zero1 = dfDisch['LOS'].eq(0).sum()
# Print the count
print(LOS_zero1)

#create age columns
dfDisch['AGE_IN_DAYS'] = (dfDisch['ADMDATE'] - dfDisch['DOB']).dt.days
dfDisch['AGE_IN_YEARS'] = round(dfDisch['AGE_IN_DAYS']/365.25)

# create date check flags
dfDisch['DOB_GT_ADMDT'] = (dfDisch['DOB'] > dfDisch['ADMDATE']).astype(int)
dfDisch['ADMDT_GT_DISCHDT'] = (dfDisch['ADMDATE'] > dfDisch['DISDATE']).astype(int)
dfDisch['DOB_Null'] = dfDisch['DOB'].isnull().astype(int)
dfDisch['Admit_Date_Null'] = dfDisch['ADMDATE'].isnull().astype(int)
dfDisch['Disch_Date_Null'] = dfDisch['DISDATE'].isnull().astype(int)

# create Died columns for when STATUS = 20
dfDisch['Died'] = (dfDisch['STATUS'] == '20').astype(int)

# replace NaN values with blank values
dfDisch = dfDisch.fillna('')

print('dfDisch contains these columns.')
print(dfDisch.columns.tolist(),'',sep='\n')


##############################################################################
# 4. Create long & narrow dfDxFinal file.
##############################################################################
print('*'*80)
print('STEP 4: Create long & narrow ICD10 DX file. ')
print('*'*80,'',sep='\n')
# 4. melt DX arrays to long and narrow
#  4a. DX codes
print('-'*80)
print('Melting df4800 to create dfDx for dx code fields.','',sep='\n')

# list comprehension - read about it

# df4800Dx = df4800.copy()
# df4800Dx.rename(columns={'PRDIAG':'SECDX0',
#                  'PRDIAGPOA':'SECDX0POA'}, inplace=True)
# dx_cols = [c for c in df4800Dx.columns if c.find('SECDX')>=0]

# dfDx = df4800.set_index(['PROVNUM', 'PCN', 'DISDATE'])



dfDx = df4800.melt(id_vars=['PROVNUM', 'PCN', 'DISDATE'],
                   value_vars=['PRDIAG',
                               'SECDX1',
                               'SECDX2',
                               'SECDX3',
                               'SECDX4',
                               'SECDX5',
                               'SECDX6',
                               'SECDX7',
                               'SECDX8',
                               'SECDX9',
                               'SECDX10',
                               'SECDX11',
                               'SECDX12',
                               'SECDX13',
                               'SECDX14',
                               'SECDX15',
                               'SECDX16',
                               'SECDX17',
                               'SECDX18',
                               'SECDX19',
                               'SECDX20',
                               'SECDX21',
                               'SECDX22',
                               'SECDX23',
                               'SECDX24',
                               'SECDX25',
                               'SECDX26',
                               'SECDX27',
                               'SECDX28',
                               'SECDX29',
                               'SECDX30',
                               'SECDX31',
                               'SECDX32',
                               'SECDX33',
                               'SECDX34',
                               'SECDX35',
                               'SECDX36',
                               'SECDX37',
                               'SECDX38',
                               'SECDX39',
                               'SECDX40'],
                   var_name='DX Seq', value_name='DX Code')

# rename some columns
dfDx['DX Seq'] = dfDx['DX Seq'].str.replace('SECDX', '')
dfDx['DX Seq'] = dfDx['DX Seq'].str.replace('PRDIAG', '0')
dfDx['DX Seq'] = dfDx['DX Seq'].astype(int)

#  Note: there are 41 DX fields in dfDisch
#  This melt creates 41 dx records per encounter
#    regardless of whether a dx was coded for a given position
#  Thus, after the melt, there are 41 dx records per encounter
print('df4800 has been pivoted to create dfDx.',
      'which provides a long and narrow dx codee format','',sep='\n')
print(f'The total records in dfDx = {dfDx.shape[0]:,}','',sep='\n')
print(f'The total records expected in dfDx = {dfDisch.shape[0]*41:,}')
print('because there are 41 dx fields and the pivot creates 41',
      ' dx records per encounter in dfDisch.','',sep='\n')

# List the pivoted column names for log and checking
print('','The dfDX contains these column names:','',sep='\n')
print(f'{list(dfDx)}','',sep='\n')

# Now remove the records with null dxes & print total record results
# this is done to reduce the number of meaningless rows produced by the melt
dfDx = dfDx[dfDx['DX Code'].notnull()]
print('After removing records with null Dx codes, the ')
print(f"total records remaining in dfDX = {dfDx.shape[0]:,}")
print()

# 4b. Create the same file for the DX POA values
print('-'*80)
print('Melting df4800 to create dfDxPoa for dx POA fields.','',sep='\n')
dfDxPoa = df4800.melt(id_vars=['PROVNUM', 'PCN', 'DISDATE'],
                      value_vars=['PRDIAGPOA',
                                  'SECDX1POA',
                                  'SECDX2POA',
                                  'SECDX3POA',
                                  'SECDX4POA',
                                  'SECDX5POA',
                                  'SECDX6POA',
                                  'SECDX7POA',
                                  'SECDX8POA',
                                  'SECDX9POA',
                                  'SECDX10POA',
                                  'SECDX11POA',
                                  'SECDX12POA',
                                  'SECDX13POA',
                                  'SECDX14POA',
                                  'SECDX15POA',
                                  'SECDX16POA',
                                  'SECDX17POA',
                                  'SECDX18POA',
                                  'SECDX19POA',
                                  'SECDX20POA',
                                  'SECDX21POA',
                                  'SECDX22POA',
                                  'SECDX23POA',
                                  'SECDX24POA',
                                  'SECDX25POA',
                                  'SECDX26POA',
                                  'SECDX27POA',
                                  'SECDX28POA',
                                  'SECDX29POA',
                                  'SECDX30POA',
                                  'SECDX31POA',
                                  'SECDX32POA',
                                  'SECDX33POA',
                                  'SECDX34POA',
                                  'SECDX35POA',
                                  'SECDX36POA',
                                  'SECDX37POA',
                                  'SECDX38POA',
                                  'SECDX39POA',
                                  'SECDX40POA'
                                  ],
                      var_name='DX Seq', value_name='DX POA')

# rename some columns
dfDxPoa['DX Seq'] = dfDxPoa['DX Seq'].str.replace('SECDX', '')
dfDxPoa['DX Seq'] = dfDxPoa['DX Seq'].str.replace('POA', '')
dfDxPoa['DX Seq'] = dfDxPoa['DX Seq'].str.replace('PRDIAG', '0')
dfDxPoa['DX Seq'] = dfDxPoa['DX Seq'].astype(int)

#  Note: there are 41 DX POA fields in dfDisch
#  This melt function creates 41 dxpoa records per encounter
#    regardless of whether a dxpoa was coded for a given position
#  Thus, after the melt, there are 41 dxpoa records per encounter
print('df4800 has been pivoted to create dfDxPoa.',
      'which provides a long and narrow dxpoa codee format','',sep='\n')
print(f'The total records in dfDxPoa = {dfDxPoa.shape[0]:,}','',sep='\n')
print(f'The total records expected in dfDxPoa = {dfDisch.shape[0]*41:,}')
print('because there are 41 dxpoa fields and the pivot creates 41',
      ' dxpos records per encounter in dfDisch.','',sep='\n')

# List the pivoted column names for log and checking
print('','The dfDXPoa contains these column names:','',sep='\n')
print(f'{list(dfDxPoa)}','',sep='\n')

# Now remove the records with null dxes & print total record results
# this is done to reduce the number of meaningless rows produced by the melt
dfDxPoa = dfDxPoa[dfDxPoa['DX POA'].notnull()]
print('After removing records with null Dx codes, the ')
print(f"total records remaining in dfDXPoa = {dfDxPoa.shape[0]:,}")
print()

# print some sample resuts
print('Sample for new dfs:')
print('dfDx:')
print(dfDx.head(), '', sep='\n')
print('dfDxPoa:')
print(dfDxPoa.head(), '', sep='\n')

# 4c. merge into one dx narrow df.
print('Merge of dfDx and dfDxPoa to create dfDxFinal for import.','', sep='\n')
dfDxFinal = pd.merge(dfDx, dfDxPoa, how='left', indicator=True)
print(dfDxFinal['_merge'].value_counts(),'',sep='\n')
print('DX Seq Num case distribution of dfDxFinal.')
print('Expect smaller numbers as the seq number increases.')
print(dfDxFinal.groupby(['DX Seq'])['PROVNUM'].count(), '', sep='\n')

# format DISDATE to date
dfDxFinal['DISDATE'] = pd.to_datetime(dfDxFinal['DISDATE'], format='%m%d%Y')

# Rename some columns to match the target Access table TEMP_DX
dfDxFinal = dfDxFinal.rename(columns={
    'DX Seq': 'SEQ',
    'DX Code': 'DX',
    'DX POA': 'POA'})

# replace NaN values with blank values
dfDxFinal['POA'] = dfDxFinal['POA'].fillna('')

print('dfDxFinal info after a few col name changes:')
print(dfDxFinal.info(verbose=True, show_counts=True), '', sep='\n')

##############################################################################
# 5. Create long & narrow dfPxFinal file.
##############################################################################
print('*'*80)
print('STEP 5: Create long & narrow ICD10 PX file. ')
print('*'*80,'',sep='\n')
# 5. melt PX arrays to long and narrow
#  5a. PX codes
print('-'*80)
print('Melting df4800 to create dfPx for px code fields.','',sep='\n')
dfPx = df4800.melt(id_vars=['PROVNUM', 'PCN', 'DISDATE', 'ADMDATE'],
                   value_vars=['PRPROC',
                               'SECPRC1',
                               'SECPRC2',
                               'SECPRC3',
                               'SECPRC4',
                               'SECPRC5',
                               'SECPRC6',
                               'SECPRC7',
                               'SECPRC8',
                               'SECPRC9',
                               'SECPRC10',
                               'SECPRC11',
                               'SECPRC12',
                               'SECPRC13',
                               'SECPRC14',
                               'SECPRC15',
                               'SECPRC16',
                               'SECPRC17',
                               'SECPRC18',
                               'SECPRC19',
                               'SECPRC20',
                               'SECPRC21',
                               'SECPRC22',
                               'SECPRC23',
                               'SECPRC24',
                               'SECPRC25',
                               'SECPRC26',
                               'SECPRC27',
                               'SECPRC28',
                               'SECPRC29',
                               'SECPRC30'],
                   var_name='PX Seq', value_name='PX Code')

# rename some columns
dfPx['PX Seq'] = dfPx['PX Seq'].str.replace('SECPRC', '')
dfPx['PX Seq'] = dfPx['PX Seq'].str.replace('PRPROC', '0')
dfPx['PX Seq'] = dfPx['PX Seq'].astype(int)

#  Note: there are 31 PX fields in dfDisch
#  This melt function creates 31 px records per encounter
#    regardless of whether a px was coded for a given position
#  Thus, after the melt, there are 31 px records per encounter
print('dfDisch has been pivoted to create dfPx.',
      'which provides a long and narrow px codee format','',sep='\n')
print(f'The total records in dfPx = {dfPx.shape[0]:,}','',sep='\n')
print(f'The total records expected in dfPx = {dfDisch.shape[0]*31:,}')
print('because there are 31 px fields and the pivot creates 31',
      ' px records per encounter in dfDisch.','',sep='\n')

# List the pivoted column names for log and checking
print('','The dfPx contains these column names:','',sep='\n')
print(f'{list(dfPx)}','',sep='\n')

# Now remove the records with null pxes & print total record results
# this is done to reduce the number of meaningless rows produced by the melt
dfPx = dfPx[dfPx['PX Code'].notnull()]
print('After removing records with null px codes, the ')
print(f"total records remaining in dfPx = {dfPx.shape[0]:,}")
print()

# print some sample resuts
print('Sample for new dfs:')
print(dfPx.head(), '', sep='\n')

print(dfPx.groupby(['PX Seq'])['PROVNUM'].count(), '', sep='\n')

#  5b. PX code dates
print('-'*80)
print('Melting df4800 to create dfPxDate for px date fields.','',sep='\n')
dfPxDate = df4800.melt(id_vars=['PROVNUM', 'PCN', 'DISDATE', 'ADMDATE'],
                   value_vars=['PRPRDATE',
                               'SECDAT1',
                               'SECDAT2',
                               'SECDAT3',
                               'SECDAT4',
                               'SECDAT5',
                               'SECDAT6',
                               'SECDAT7',
                               'SECDAT8',
                               'SECDAT9',
                               'SECDAT10',
                               'SECDAT11',
                               'SECDAT12',
                               'SECDAT13',
                               'SECDAT14',
                               'SECDAT15',
                               'SECDAT16',
                               'SECDAT17',
                               'SECDAT18',
                               'SECDAT19',
                               'SECDAT20',
                               'SECDAT21',
                               'SECDAT22',
                               'SECDAT23',
                               'SECDAT24',
                               'SECDAT25',
                               'SECDAT26',
                               'SECDAT27',
                               'SECDAT28',
                               'SECDAT29',
                               'SECDAT30'],
                   var_name='PX Seq', value_name='PX Date')

# rename some columns
dfPxDate['PX Seq'] = dfPxDate['PX Seq'].str.replace('SECDAT', '')
dfPxDate['PX Seq'] = dfPxDate['PX Seq'].str.replace('PRPRDATE', '0')
dfPxDate['PX Seq'] = dfPxDate['PX Seq'].astype(int)

#  Note: there are 31 px date fields in dfDisch
#  This melt function creates 31 px date records per encounter
#    regardless of whether a px date was coded for a given position
#  Thus, after the melt, there are 31 px date records per encounter
print('df4800 has been pivoted to create dfPxDate.',
      'which provides a long and narrow px date format','',sep='\n')
print(f'The total records in dfPxDate = {dfPxDate.shape[0]:,}','',sep='\n')
print(f'The total records expected in dfPxDate = {dfDisch.shape[0]*31:,}')
print('because there are 31 px date fields and the pivot creates 31',
      ' px date records per encounter in dfDisch.','',sep='\n')

# List the pivoted column names for log and checking
print('','The dfPxDate contains these column names:','',sep='\n')
print(f'{list(dfPxDate)}','',sep='\n')

# Now remove the records with null pxes & print total record results
# this is done to reduce the number of meaningless rows produced by the melt
dfPxDate = dfPxDate[dfPxDate['PX Date'].notnull()]
print('After removing records with null px dates, the ')
print(f"total records remaining in dfPxDate = {dfPxDate.shape[0]:,}")
print()

# print some sample resuts
print('Sample for new dfs:')
print('dfPx:')
print(dfPx.head(), '', sep='\n')
print(dfPxDate.head(), '', sep='\n')

# 5c. merge into one dx narrow df.
print('Merge of dfPx & dfPxDate to create dfPxFinal for export.','', sep='\n')
dfPxFinal = pd.merge(dfPx, dfPxDate, how='left', indicator=True)
print(dfPxFinal['_merge'].value_counts())

print(dfPxFinal['PX Date'].isnull().sum())

# check for null dates due to left only merge issues that creates null PX dates
# create a left_only count variable
null_px_date_count = (dfPxFinal['_merge'] == 'left_only').sum()
# fill null px dates if any with the associated ADMDATE
if null_px_date_count > 0:
    print(f'''After the merge there are {null_px_date_count} records without a 
    px date. These null dates must be replaced with the associated ADMDATE 
    because the target table PX_TEMP in {file_accdb} is expecting dates.''')
    print()    
    # Find the records with missing px dates
    missing_px_dt_records = dfPxFinal[dfPxFinal['_merge'] == 'left_only']
    print(f'These {null_px_date_count} records have missing dates:')
    print(missing_px_dt_records,'',sep='\n')
    # Replace the null dates with the ADMDATE
    mask = dfPxFinal['_merge'] == 'left_only'
    dfPxFinal.loc[mask, 'PX Date'] = dfPxFinal.loc[mask, 'ADMDATE'] 
    # Now print afte the replacement
    print(f'These {null_px_date_count} records have been updated:')
    print(dfPxFinal.loc[mask],'',sep='\n')
    

print(dfPxFinal['PX Date'].isnull().sum())

# format date fields from text tp dates
dfPxFinal['DISDATE'] = pd.to_datetime(dfPxFinal['DISDATE'], format='%m%d%Y')
dfPxFinal['ADMDATE'] = pd.to_datetime(dfPxFinal['ADMDATE'], format='%m%d%Y')
dfPxFinal['PX Date'] = pd.to_datetime(dfPxFinal['PX Date'], format='%m%d%Y')
# dfPxFinal['PX Date'] = dfPxFinal['PX Date'].replace(pd.NaT, None)
# dfPxFinal['PX Date'] = dfPxFinal['PX Date'].fillna(value=None)

# Rename some columns to match the target Access table PX_TEMP
dfPxFinal = dfPxFinal.rename(columns={
    'DISDATE': 'DISCH_DATE',
    'ADMDATE': 'ADMIT_DATE',
    'PX Seq': 'SEQ',
    'PX Code': 'PX',
    'PX Date': 'PX_DATE'})

# replace NaN values with blank values
dfPxFinal['PX_DATE'] = dfPxFinal['PX_DATE'].fillna('')


print('PX Seq Num case distribution of dfPxFinal.')
print('Expect smaller numbers as the seq number increases.')
print(dfPxFinal.groupby(['SEQ'])['PROVNUM'].count(), '', sep='\n')

print('dfPxFinal info after a few col name changes:')
print(dfPxFinal.info(verbose=True, show_counts=True), '', sep='\n')

##############################################################################
# 6. Populate the Access tables
##############################################################################
print('*'*80)
print('STEP 6: POPULATE THE ACCESS TABLES.')
print('*'*80,'',sep='\n')

# Populate the DISCH_TEMP, DX_TEMP, PX_TEMP and R_PHY Access tables

# create dictionary of dataframes and corresponding target Access tables
print('Creating a dictionary for Access table insertion iteration')
tables_and_dfs = [
    ('DISCH_TEMP', dfDisch, 'dfDisch'),
    ('DX_TEMP', dfDxFinal, 'dfDxFinal'),
    ('PX_TEMP', dfPxFinal, 'dfPxFinal'),
    ('R_PHY', dfPhy, 'dfPhy')]
# print the list for logging
print('The iteration list includes:')
for table, df, dfname in tables_and_dfs:
    print(dfname + ' to be inserted into the ' + table +' Access table')
print()

# print(list(tables_and_dfs.items()),'',sep='\n')

# Connect to Access
print('Connecting to the 4800.accdb Access database.','',sep='\n')
conn = pyodbc.connect(connection_str)
cursor = conn.cursor()
print('Connection successful!')

# Iterate through the dictionary and insert each dataframe into the corresponding table
print('''Now populating Access tables through iteration.Note that this process
      uses a row by row insertion and thus will take a few minutes per table.
      Now is a good time to refresh that beverage!!
      ''')
for table, df, dfname in tables_and_dfs:
    print(f'Inserting rows into {table} table from {dfname}')
    for index, row in df.iterrows():
        cursor.execute(f"""
            INSERT INTO {table} ({', '.join(df.columns)}) 
            VALUES ({', '.join('?' * len(df.columns))})
        """, tuple(row[col] for col in df.columns))
    # Commit the transaction
    conn.commit()

    # Count and print the number of rows in the table
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    num_rows = cursor.fetchone()[0]
    num_df = len(df)
    print(f'The number of rows in {dfname} is {num_df:,g}')
    print(f'The number of rows inserted into {table} is {num_rows:,g}')
    print()

# Close the cursor and connection
print('Closing the cursor connection and the 4800_Python.accdb db.')
cursor.close()
conn.close()
print(f'''Congratulations!!! The process is complete. 
      Open {file_accdb} to complete the DQR report process.''')


