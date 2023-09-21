##############################################################################
# Prime Facility Dashboard Processing Code
# @author: Jim Cheairs

# This python script intakes clinical dashboard fac & facqtr metric files 
# and the HAI supplemental file and creates output to populate 
#  required excel tables for creating the Prime Facility Dashboards.
#   The final deliverable includes 41 individual facility Excel dashboards
#   produced quarterly.
# Major process steps include:
# 1. Set all variables
# 2. read in and format necessary client files in dataframes
#    (metrics.xlsx, ref_hosp, ref metric, HAI.xlsx, benchmarks).
# 3. Perform additional formatting to fac, facqtr and HAI files.
# 4. Create final dataframes that are used to populate the excel template.
# 5. Iterate by facility (x41) to create each facility's dashbaord.
##############################################################################
#%%
import time as time
import datetime
import os
import pandas as pd
import xlwings as xw
import numpy as np

# Start off with some good log information...
start_time=datetime.datetime.now()
#start_time = time.time()

print('*'*80)
print(f"""SYSTEM INFORMATION
Username:  {os.getlogin()}
Run start time: {datetime.datetime.now()}
""")

print("""This code set creates the Prime Facility Dashboard Excel reports.

An Excel dashboard is produced for each Prime facility in the dataset. There
 are 41 facilities that will receive a report.

The processing sections include:
 1. Set Variables
 2. Import the aggregated fac/facqtr and other client files and check for quality
 3. Apply formatting to dataframes to meet prime requirements.
 4. Create intermediate dataframe results that include all facilities
 5. Using these dataframes, iterate through the ref_hosp list to produce 
    and save each facility excel file. 
""")

# 1. set the working directories and file constants
print('*'*80)
print('STEP 1: SET DIRECTORY, FILES AND MISC VARIABLES.')
print('*'*80,'',sep='\n')

# Variables that change
#  These variables need to be cheched and updated with each quarterly project
P_SRC = 'C:/PHI/Projects/Prime/Refresh 2023q2/DB Output'
F_METRICS = 'prime_metrics_07-01-2019_06-30-2023_Final.xlsx'
F_FAC = 'fac'
F_FACQTR = 'facqtr'
F_HOSP = 'ref_hosp_all.xlsx'
F_HOSP_LOOP = 'HCO Ref Facility Rpts 23q2'
F_HOSP_TAB =  'HCO Ref Facility Rpts 23q2'
F_METRIC_REF = 'ref_metrics.xlsx'
F_HAI = 'Prime HAI Final_2019q3_2023q2_updt.xlsx'
F_100TOP_BENCH = 'Prime_100Top_Benchmarks_2022_w_R30.xlsx'
F_HAI_BENCH = 'Prime_HAI_Benchmarks_2022.xlsx'
P_REPORTS = 'C:/PHI/Projects/Prime/Refresh 2023q2/Deliverable/Reports 2023q2'
F_TEMPLATE = 'Prime Fac Dashboard RS 30 - HAI Tbls Only - trends removed.xlsx'
RPT_CURR_QTR = '2023 Q2'
RPT_CURR_QTR_SAF = '2022 Q2'
RPT_CURR_QTR_MSPB = '2020'
RPT_SUFFIX = '_2023q2'
# Rolling year mapping for HAI measure aggregation
# create mapping that assigns each 4 quarter group to a year, 1 thru 4
year_mapping = {
    '2019 Q3': 'Year 1',
    '2019 Q4': 'Year 1',
    '2020 Q1': 'Year 1',
    '2020 Q2': 'Year 1',
    '2020 Q3': 'Year 2',
    '2020 Q4': 'Year 2',
    '2021 Q1': 'Year 2',
    '2021 Q2': 'Year 2',
    '2021 Q3': 'Year 3',
    '2021 Q4': 'Year 3',
    '2022 Q1': 'Year 3',
    '2022 Q2': 'Year 3',
    '2022 Q3': 'Year 4',
    '2022 Q4': 'Year 4',
    '2023 Q1': 'Year 4',
    '2023 Q2': 'Year 4'

}

# Variables that do not change
COMPARISON = 'Top Decile'
# Metrics shown in the 2x2 plot
MSR_2X2 = ('M','C','A','$','R','30D M','30D R','H','OM','O', 'MSPB')
MSR_RefTrend = ('M','C','A','$','R','30D M','30D R',
                '30D RS', 'H','OM','O', 'MSPB')
HAI_codes = ['I','I-CAUTI', 'I-CDIFF', 'I-CLABSI', 'I-MRSA',
                    'I-SSI-CS', 'I-SSI-HY']
# Metrics shown in current quarter graphs
MSR_CURR_QTR = ('M','C','A','$','R','30D R','H','OM')
MSR_CURR_QTR_SAF = ('30D M','30D RS') 
MSR_CURR_QTR_MSPB = 'MSPB'


# print the constants for logging
print('Path and File Constants:','',sep='\n')
print(f'Source file directory: {P_SRC}')
print(f'Aggregate metric import excel file: {F_METRICS}')
print(f'Aggregate fac excel tab: {F_FAC}')
print(f'Aggregate facqtr excel tab: {F_FACQTR}')
print(f'Hospital ref excel file: {F_HOSP}')
print(f'HAI Supplemental data: {F_HAI}')
print(f'100Top benchmark excel file: {F_100TOP_BENCH}')
print(f'Report production file directory for table reports: {P_REPORTS}')
print(f'Facility Report template w trend tables is: {F_TEMPLATE}')
print(f'The current quarter constant: {RPT_CURR_QTR}')
print(f'The trend table report file name suffix: {RPT_SUFFIX}')
print()
print('Other Constants:','',sep='\n')
print(f'The benchmark used for comparison: {COMPARISON}')
print(f'The 2x2 measures list: {MSR_2X2}')
print(f'The current quarter measures list: {MSR_CURR_QTR}')
print()


##############################################################################
# 2. File Import and Preprocessing
##############################################################################
print('*'*80)
print('STEP 2: IMPORT CLIENT FILES AND FORMAT')
print('*'*80,'',sep='\n')

# 2a. Read in and format the Metric_by_fac tab from Metrics_combined.xlsx.
#   Read in file and remove HAI records

print('-'*80)
print(f'2a. Importing the {F_FAC} tab from {F_METRICS} to dfFacSrc',sep='\n')
dfFacSrc = pd.read_excel(f'{P_SRC}/{F_METRICS}',
                         sheet_name = F_FAC, dtype=str)

print(f'{dfFacSrc.shape[0]:,g} records were imported into dfFacSrc.')
# remove HAI records
# first count the records we are removing
HAI_count = dfFacSrc['Metric Code'].isin(HAI_codes).sum()
print(f'{HAI_count:,g} HAI records removed from dfFacSrc')
dfFacSrc = dfFacSrc[~dfFacSrc['Metric Code'].isin(HAI_codes)]
print(f'{dfFacSrc.shape[0]:,g} records remain in dfFacSrc.',
      '',sep='\n')

#   Format numeric fields to float
#   List used to change formats for number fields after import
print('Reformatting all number fields to float in dfFacSrc','',sep='\n')
types_dict_fac = {'Qualified': float,
                  'Observed_src': float,
                  'Expected_src': float,
                  'Improvement_src': float,
                  'Recent_src': float,
                  'Observed': float,
                  'Expected': float,
                  'Improvement': float,
                  'Recent': float}
#   Iterate using types_dict_fac to change numeric fields from str to float
for col, col_type in types_dict_fac.items():
    dfFacSrc[col] = dfFacSrc[col].astype(col_type)

#   check that all benchmarks are populated 
print('Checking row count benchmark. Each should have the same count except' 
      'Top Decile which has 41 additional MSPB records.')
print(dfFacSrc['Benchmark'].value_counts(),'',sep='\n')

#   Create dfFac which includes the Decile benchmark records only.
print(f'Creating dfFac from dfFacSrc with {COMPARISON} benchmark rows only.') 
dfFac = dfFacSrc.loc[(dfFacSrc['Benchmark'] == COMPARISON)].copy()
# List the column names for log and checking
print(f'{dfFac.shape[0]:,g} records were imported into dfFac.')
print(f'which should equal the {COMPARISON} row count above.','',sep='\n')
print('dfFac info includes:')
print(dfFac.info(verbose=True, show_counts=True),'',sep='\n')

del HAI_count # remove this variable

# 2b. Read in and format the Metric_by_facqtr tab from Metrics_combined.xlsx.
#   Read in file
print('-'*80)
print(f'2b. Importing the {F_FACQTR} tab from {F_METRICS} to dfFacSrc',
      sep='\n')
dfFacqtrSrc = pd.read_excel(f'{P_SRC}/{F_METRICS}',
                         sheet_name = F_FACQTR, dtype=str)
print(f'{dfFacqtrSrc.shape[0]:,g} records were imported into dfFacqtrSrc.')
# remove HAI records
# first count the records we are removing
HAI_count = dfFacqtrSrc['Metric Code'].isin(HAI_codes).sum()
print(f'{HAI_count:,g} HAI records removed from dfFacqtrSrc')
dfFacqtrSrc = dfFacqtrSrc[~dfFacqtrSrc['Metric Code'].isin(HAI_codes)]
print(f'{dfFacqtrSrc.shape[0]:,g} records remain in dfFacqtrSrc.',
      '',sep='\n')

del HAI_count # remove this variable

#   List used to change formats for number fields after import
print('Reformatting Qualified, Obs, Exp and OE Ratio fields to float in dfFacqtrSrc','',sep='\n')
# Used to change formats for number fields after import
types_dict_facqtr = {'Qualified': float,
                     'Observed_src': float,
                     'Expected_src': float,
                     'OE_ratio_src': float,
                     'Observed': float,
                     'Expected': float,
                     'OE_ratio': float}

#   iterate using types_dict to change numeric fields from str to float
for col, col_type in types_dict_facqtr.items():
    dfFacqtrSrc[col] = dfFacqtrSrc[col].astype(col_type)

#   check that all benchmarks are populated 
print('Checking row count benchmark. Each should have the same count except' 
      'Top Decile which has 123 additional MSPB records.')
print(dfFacqtrSrc['Benchmark'].value_counts(),'',sep='\n')

# create dfFacqtr which only includes the Decile benchmark records
print(f'Creating dfFacqtr from dfFacqtrSrc with {COMPARISON} benchmark rows only.') 
dfFacqtr = dfFacqtrSrc.loc[(dfFacqtrSrc['Benchmark'] == COMPARISON)].copy()
print(f'{dfFacqtr.shape[0]:,g} records were imported into dfFacqtr.')
print(f'which should equal the {COMPARISON} row count above.','',sep='\n')
print('dfFacqtr info includes:')
print(dfFacqtr.info(verbose=True, show_counts=True),'',sep='\n')


# 2c. Read in the HAI supplemental file 
#  This file is used to provide HAI outcomes data which is treated differently
print('-'*80)
print(f'2c. Importing the HAIs tab from {F_HAI} to dfHAI',
      sep='\n')
# dfHAI = pd.read_csv(f"{P_SRC}/{F_HAI}", sep='|', dtype=str)
dfHAI = pd.read_excel(f'{P_SRC}/{F_HAI}',
                        sheet_name = 'HAIs', dtype=str)
print(f'{dfHAI.shape[0]:,g} records were imported into dfHAI.','',
      sep='\n')
print('dfHAI info includes:')
print(dfHAI.info(verbose=True, show_counts=True),'',sep='\n') 

#   Format numeric fields to float
dfHAI['Observed_c'] = dfHAI['Observed_c'].astype(float)
dfHAI['Expected_c'] = dfHAI['Expected_c'].astype(float)

# Add a Year Quarter column
print('Adding a Year Quarter column as YYYY Q#')
dfHAI['Year Quarter'] = dfHAI['Year'] + ' Q' +dfHAI['Quarter Number']
# add rolling 4 quarter year column

# add Rolling Year column using the established year_mapping dictionary
# print out year mapping dictionary.
print('Adding a Rolling Year (Year1, Year2, etc.) to dfHAI')
for year, label in year_mapping.items():
    print(f"{year}: {label}")
# assign the mapping
dfHAI['Rolling Year'] = dfHAI['Year Quarter'].map(year_mapping)
print()
print('The 4 rolling years in dfHAI are:')
print(dfHAI.groupby('Rolling Year').size())
print()

# 2d1. Read in the tab from ref_hosp file for excel file iteration. 
print('-'*80)
print(f'2d1. Importing the {F_HOSP_LOOP} tab from {F_HOSP}, to dfHospLoop',sep='\n')
dfHospLoop = pd.read_excel(f'{P_SRC}/{F_HOSP}',
                       sheet_name = F_HOSP_LOOP, dtype=str)

# 2d2. Read in the ref_hosp file
print('-'*80)
print(f'2d2. Importing the {F_HOSP_TAB} tab from {F_HOSP}, to dfHosp',sep='\n')
dfHosp = pd.read_excel(f'{P_SRC}/{F_HOSP}',
                       sheet_name = F_HOSP_TAB, dtype=str)

# Rename the column FAC_ID to Facility ID
dfHosp = dfHosp.rename(columns={'FAC_ID': 'Facility ID'})

print(f'{dfHosp.shape[0]:,g} records were imported into dfHosp.','',sep='\n')
# List the column names for log and checking
print('dfHosp info includes:')
print(dfHosp.info(verbose=True, show_counts=True),'',sep='\n')

# 2e. Read in the 100Top benchmark file
# this file is only used for populating the current quarter charts
# Prime reports current quarter performance to the static 100Top comparisons
print('-'*80)
print(f'2e. Importing the 100Top benchmark file, {F_100TOP_BENCH}, to dfBench',
      sep='\n')
dfBench = pd.read_excel(f'{P_SRC}/{F_100TOP_BENCH}')
print(f'{dfBench.shape[0]:,g} records were imported into dfBench.','',sep='\n')
# List the column names for log and checking
print('dfBench info includes:')
print(dfBench.info(verbose=True, show_counts=True),'',sep='\n')

# 2f. Read in the HAI benchmark file
# this file is only used for populating the HAI Year tables
print('-'*80)
print(f'2f. Importing the HAI benchmark file, {F_HAI_BENCH}, to dfBenchHAI',
      sep='\n')
dfBenchHAI = pd.read_excel(f'{P_SRC}/{F_HAI_BENCH}')
print(f'{dfBenchHAI.shape[0]:,g} records were imported into dfBenchHAI.','',sep='\n')
# List the column names for log and checking
print('dfBenchHAI info includes:')
print(dfBenchHAI.info(verbose=True, show_counts=True),'',sep='\n')

# 2g. Read in the Metric ref table
# this file is used for adding Metric Description to final RefTrend df
print('-'*80)
print(f'2g. Importing the ref_metrics tab from {F_METRIC_REF} to dfMetricRef',
      sep='\n')
dfMetricRef = pd.read_excel(f'{P_SRC}/{F_METRIC_REF}',
                         sheet_name = 'ref_metrics', dtype=str)
print(f'{dfMetricRef.shape[0]:,g} records were imported into dfMetricRef.','',
      sep='\n')
print('dfMetricRef info includes:')
print(dfMetricRef.info(verbose=True, show_counts=True),'',sep='\n')


##############################################################################
# 3. Format dfFac and dfFacqtr to meet Prime requirements
##############################################################################
print('*'*80)
print('STEP 3: Format dfFac & dfFacqtr to meet Prime requirements')
print('*'*80,'',sep='\n')

# Make necessary formatting changes to dfFac and dfFacqtr.

# The remaining formatting procedures for both dfs are done through iteration.
# establish a working list for iteration
format_dfs = [(dfFac,'dfFac'), (dfFacqtr, 'dfFacqtr')]
# Define metric codes to be relabeled
rename_codes = ['M30', 'R30', 'RS30', 'S', 'L']
renamed_codes = ['30D M', '30D R', '30D RS', 'H', 'A']
#Define metrics codes whose descriptons will be changed
replace_codes = ['M30-HA', 'M30-HF', 'M30-PN', 'R30-HA', 'R30-HF', 
                 'R30-PN', 'R30-TJ', 'RS30-HF', 'RS30-PN', 'RS30-TJ']
print('Completing formatting of dfFac and dfFacqtr.','',sep='\n')
for df, df_name in format_dfs:
    print('-'*80)
    print(f'Formatting {df_name}.','',sep='\n')
    # Update Metric code values for some codes to meet Prime Requirements
    print(f'Update Metric Code values to Prime values in {df_name}'
          ' for these metric codes:',' M30, R30, RS30, S and L.','',sep='\n')
    print(f'{df_name} Metric Code counts before mapping:')
    print(df[df['Metric Code'].isin(rename_codes)].
          groupby(['Metric Code'])['Medicare ID'].count(),'',sep='\n') 
    # Apply the code update
    df.update(df.replace({'Metric Code':{'M30':'30D M',
                                      'R30':'30D R',
                                      'RS30': '30D RS',
                                      'L':'A',
                                      'S':'H'}}, regex=False))
    print(f'{df_name} Metric Code counts after mapping:')
    print(df[df['Metric Code'].isin(renamed_codes)].
          groupby(['Metric Code'])['Medicare ID'].count(),'',sep='\n') 
    # Now update Metric Descriptions for relevant 30Day mort and Readmit titles.
    # in both data frames.
    print(f'Update Metric Descriptions to Prime values in {df_name}.')
    print('for these metric codes:')
    for code in replace_codes:
        print(f'  {code}')
    print()
    # Print original Metric Description counts
    print(f'{df_name} Metric Description counts before update:')
    print(df[df['Metric Code'].isin(replace_codes)].
          groupby(['Metric Code','Metric Description'])['Medicare ID'].count(),
          '',sep='\n') 
    df.update(df.replace({'Metric Description':
                    {'30 Day Mortality - Heart Attack':'30 Day Mortality - AMI',
                     '30 Day Mortality - Heart Failure':'30 Day Mortality - HF',
                     '30 Day Mortality - Pneumonia': '30 Day Mortality - PN',
                     '30 Day Readmit - Heart Attack':'30 Day Readmit - AMI',
                     '30 Day Readmit - Heart Failure':'30 Day Readmit - HF',
                     '30 Day Readmit - Pneumonia':'30 Day Readmit - PN',
                     '30 Day Readmit - Total Joint':'30 Day Readmit - Joint',
                     'SAF 30 Day Readmit - Heart Failure': 'SAF 30 Day Readmit - HF',
                     'SAF 30 Day Readmit - Pneumonia': 'SAF 30 Day Readmit - PN',
                     'SAF 30 Day Readmit - Total Joint': 'SAF 30 Day Readmit - Joint'}},
                          regex=False))
    # print counts after update
    print(f'{df_name} Metric Description counts after update:')
    print(df[df['Metric Code'].isin(replace_codes)].
          groupby(['Metric Code','Metric Description'])['Medicare ID'].count(),
          '',sep='\n') 

    # Add average observed & expected columns to fdFac and dfFacqtr
    #   (relevant for some current quarter metrics).
    print(f'Create Avg Observed & Expected columns in {df_name}.',
          ' These measures are used for some current qtr metrics.','' , sep='\n')
    #   Average Observed
    df['Average Observed'] = (df['Observed_src'] / df['Qualified'])
    #   Average Expected
    df['Average Expected'] = (df['Expected_src'] / df['Qualified'])
       
    # Print final infor for QA.
    print(f'{df_name} contains these final columns:')
    print(df.info(verbose=True, show_counts=True),'',sep='\n')
    print(f'Sample for {df_name}:')
    print(df.head(),'', sep='\n')
    
# Create look up values that are used in excel for vlookups.
print('Create look up column (LU Key) in dfFac (as Metric Code)','' , sep='\n')
dfFac.loc[:, 'LU Key'] = dfFac['Metric Code']

# In dfFacqtr, add the column, Bench, and fill with '1'.
#    this is done to provide OE Ratio compare line of 1.0 in trend graphs.
print('Adding the column, Bench, filled with 1 to dfFacqtr.',
      ' This is done to provide OE Ratio compare line of 1.0 in trend graphs.',
      '' , sep='\n')
dfFacqtr['Bench'] = 1

print('Additional Formatting of dfFac and dfFacqtr is complete.','',sep='\n')

  
##############################################################################
# 4. Create final dataframes needed for iteration to create excel files.
##############################################################################
print('-'*80)
print('STEP 4: Create final dataframes needed for Excel file iteration.')
print('-'*80,'',sep='\n')

# 4a. Create 2x2 dataframe using specific columns/metrics from dfFac.
#   meets excel rqmnts for populating the tbl_2x2_py table in the 2X2 tab
print('-'*80)
print('4a. Create df2x2 using specific columns/metrics from dfFac,',
 ' which meets rqmnts to populate the tbl_2x2_py table in the 2X2 tab',
 ' in the Prime Excel template.','' , sep='\n')
df2x2 = dfFac.loc[dfFac['Metric Code'].isin(MSR_2X2),
                     ['LU Key',
                      'Medicare ID',
                      'Facility Name',
                      'Facility Abbreviation',
                      'Benchmark',
                      'Metric Code',
                      'Recent',
                      'Improvement']]

#    Add a Metric Abbrv field
df2x2['Metric Abbrv']=df2x2['Metric Code'].map({'M': 'RAMI',
                                             'C': 'ECRI',
                                             'A':'LOS',
                                             '$': 'Costs',
                                             'R': 'HW Read',
                                             '30D M': '30D Mort',
                                             '30D R': '30D Read',
                                             'H':'HCAHPS',
                                             'OM':'Op Marg',
                                             'MSPB': 'MSPB',
                                             'O': 'Overall',})
#   print result checks
print(f'    df2x2 has been created with {df2x2.shape[0]:,g} records')
print(' and contains these columns:','')
print(df2x2.info(verbose=True, show_counts=True),'',sep='\n')

# 4b. Create dfRefTrend as the ref table that holds all possible quarters
#   for each facility and metric
#   the ref data frame we are creating includes these fields:
#    ['Medicare ID', 'FAC_ID', 'Facility Name', 'Facility Abbreviation',
#    'YearQuarter', 'Metric Code', 'Benchmark']
#    4b1. Using dfFacqtr, determine the full quarters for each facility &
#      measure defined by the variable MSR_2X2. 
#     ('M','C','A','$','R','30D M','30D R','H','OM','O', 'MSPB')
#      Call this dfRefMajor
#    4b2. For 30D R and 30D M cohort measures, append similar data for each
#      cohort using that cohort's parent measure quarters from 4b1.
#      this is done in sections per major metric resulting in three final dfs
#      based on concatenating the cohorts together for each major metric.
#    4b3. create the final dfRefTrend by concatenating the 4 dfs from  4b1 & 2.

# meets excel rqmnts for populating the tbl_trend_py table in the Trend Data tab

print('-'*80)
print('4b. Create dfRefTrend which contains all possible'
 ' facility/metric/quarter combinations.',
 ' This ensures all quarters are repesented in cohort popualtions that'
 ' may have quarter gaps.','' , sep='\n')
#  4b1. Major Metric full quarter ref data frame creation
#    create master list using the variable - 
print('-'*80)
print('Create Non cohort reference df using MSR_2X2 metric list.','',sep='\n')
dfRefMajor = dfFacqtr.loc[dfFacqtr['Metric Code'].isin(MSR_RefTrend),
                              ['Medicare ID', 
                               'Facility Name',
                               'Facility Abbreviation',
                               'YearQuarter',
                               'Metric Code',
                               'Benchmark']]
print(f'{dfRefMajor.shape[0]:,g}: dfRefMajor record count','',sep='\n')
print('dfRefMajor contains these measures and counts:')
print(dfRefMajor['Metric Code'].value_counts(dropna=False), '', sep='\n')

#  4b2. Create dfs for 30D M, 30D R and HAI
#   30 Day Readmit cohort full quarter ref data frame creation
#    Create the master dfRefR30 using the 30D R composite metric

print('-'*80)
print('Create 30D readmit reference dfs using the 30D R metric.','',sep='\n')
dfRefR30 = dfFacqtr.loc[dfFacqtr['Metric Code'] == '30D R',
                              ['Medicare ID', 
                               'Facility Name',
                               'Facility Abbreviation',
                               'YearQuarter',
                               'Metric Code', 
                               'Benchmark']]
print(f'{dfRefR30.shape[0]:,g}: dfRefR30 record count','',sep='\n')
print('All R30 df cohort counts should be the same.')
# create a row count variable for logging later
R30_COHORT_CHECK = 7*dfRefR30.shape[0]

#   Loop to create the 30D R cohort ref information using dfRefR30 as a 
#    baseline for each of the 7 cohorts
dfRefR30_cohort = pd.DataFrame()
for cohort in ['CA', 'CO', 'HA', 'HF', 'PN', 'ST', 'TJ']:
    dfRefR30_Temp = dfRefR30.copy()
    dfRefR30_Temp['Metric Code'] = f'R30-{cohort}'
    print(f'Added {dfRefR30_Temp.shape[0]:,g} R30_{cohort} ref records.')
    dfRefR30_cohort = pd.concat([dfRefR30_cohort,dfRefR30_Temp],
                                ignore_index=True)
print()
print('Created final dfRefR30_cohort by concatenating R30 cohorts together.')
print(f'Created {dfRefR30_cohort.shape[0]:,g}: records dfRefR30_cohort record count')
print('Checking the value (7 x dfRefR30)')
print(f'{R30_COHORT_CHECK}: dfRefR30_cohort count check','',sep='\n')

#   30 Day Mortality cohort full quarter ref data frame creation
#    Create the master dfRefM30 using the 30D M composite metric
print('-'*80)
print('Create 30D mortality reference dfs using the 30D M metric.','',sep='\n')
dfRefM30 = dfFacqtr.loc[dfFacqtr['Metric Code'] == '30D M',
                              ['Medicare ID', 
                               'Facility Name',
                               'Facility Abbreviation',
                               'YearQuarter',
                               'Metric Code', 
                               'Benchmark']]
print('M30 df counts should be the same.')
print(f'{dfRefM30.shape[0]:,g}: dfRefM30 record count')
# create a row count variable for logging later
M30_COHORT_CHECK = 6*dfRefM30.shape[0]

#   Loop to create the 30D M cohort ref information using dfRefM30 as a 
#    baseline for each of the 6 cohorts
dfRefM30_cohort = pd.DataFrame()
for cohort in ['CA', 'CO', 'HA', 'HF', 'PN', 'ST']:
    dfRefM30_Temp = dfRefM30.copy()
    dfRefM30_Temp['Metric Code'] = f'M30-{cohort}'
    print(f'{dfRefM30_Temp.shape[0]:,g}: RefM30_{cohort} record count')
    dfRefM30_cohort = pd.concat([dfRefM30_cohort,dfRefM30_Temp],
                                ignore_index=True)

#    Concatenate the dfRefM30 cohort dfs into dfRefM30_cohort
print()
print('Created final dfRefM30_cohort by concatenating M30 cohorts together.')
print(f'{dfRefM30_cohort.shape[0]:,g}: dfRefM30_cohort record count')
print('Checking the value (6 x dfRefM30)')
print(f'{M30_COHORT_CHECK}: dfRefM30_cohort count check','',sep='\n')


#   SAF 30 Day Readmission cohort full quarter ref data frame creation
#    Create the master dfRefRS30 using the 30D RS composite metric
print('-'*80)
print('Create SAF 30D readmission reference dfs using the 30D RS metric.','',sep='\n')
dfRefRS30 = dfFacqtr.loc[dfFacqtr['Metric Code'] == '30D RS',
                              ['Medicare ID', 
                               'Facility Name',
                               'Facility Abbreviation',
                               'YearQuarter',
                               'Metric Code', 
                               'Benchmark']]
print('RS30 df counts should be the same.')
print(f'{dfRefRS30.shape[0]:,g}: dfRefRS30 record count')
# create a row count variable for logging later
RS30_COHORT_CHECK = 6*dfRefRS30.shape[0]

#   Loop to create the 30D RS cohort ref information using dfRefRS30 as a 
#    baseline for each of the 6 cohorts
#    Concatenate the dfRefRS30 cohort dfs into dfRefRS30_cohort
dfRefRS30_cohort = pd.DataFrame()
for cohort in ['CA', 'CO', 'HA', 'HF', 'PN', 'TJ']:
    dfRefRS30_Temp = dfRefRS30.copy()
    dfRefRS30_Temp['Metric Code'] = f'RS30-{cohort}'
    print(f'{dfRefRS30_Temp.shape[0]:,g}: RefRS30_{cohort} record count')
    dfRefRS30_cohort = pd.concat([dfRefRS30_cohort,dfRefRS30_Temp],
                                ignore_index=True)

print()
print('Created final dfRefRS30_cohort by concatenating RS30 cohorts together.')
print(f'{dfRefRS30_cohort.shape[0]:,g}: dfRefRS30_cohort record count')
print('Checking the value (6 x dfRefRS30)')
print(f'{RS30_COHORT_CHECK}: dfRefRS30_cohort count check','',sep='\n')


#  4b3. concatenate dfRefMajor and the 3 cohort ref dfs into dfRefTrend
print('-'*80)
print('Create dfRefTrend by concatenating all 4 cohort dfs together:',
      'dfRefMajor and the 3 cohort ref dfs','',sep='\n')
dfRefTrend = pd.concat([dfRefMajor,
                        dfRefM30_cohort,
                        dfRefR30_cohort,
                     #   dfRefHAI_cohort,
                        dfRefRS30_cohort], ignore_index=True)
print(f'{dfRefTrend.shape[0]:,g}: dfRefTrend record count','',sep='\n')

#    Add the Metric Description from dfMetricRef to dfRefTrend as final step.
print('Add the Metric description to dfRefTrend via merge with dfMetricRef.')
print('Merge results should have 0 in left_only and right_only results.','',
      sep='\n')
dfRefTrend = pd.merge(dfRefTrend, dfMetricRef, how='left', indicator=True)
print(dfRefTrend['_merge'].value_counts())
print()

# check sum of 3 cohort ref counts
# cohort count variables
COHORT_COUNT = dfRefM30_cohort.shape[0]+\
      dfRefR30_cohort.shape[0]+dfRefMajor.shape[0]+dfRefRS30_cohort.shape[0]
# now print sum of record count of all 4 ref dfs
print(f'{COHORT_COUNT:,g} is the sum of the 4 cohort record counts',
      'which should equal the dfRefTrend count above.','',sep='\n')

# print sample of dfRefTrend
dfRefTrend.drop('_merge', axis=1,inplace=True)
print('Sample rows from dfRefTrend:')
print(dfRefTrend.head(),'', sep='\n')

#  4c. Create dfTrend which is a subset of columns from dfFacqtr
#      pd.merge dfRefTrend, dfTrend as left to create a new dfTrendAll which
#      is used to create the excel trend output. 
#      for gap quarters, OE ratios, Observed and Expected are filled with 0 
print('-'*80)
print('''4c. Create dfTrend which is a subset of columns from dfFacqtr
 and a merge on dfRefTrend to create a new dfTrendAll which is used to
 create the excel trend output. 
 Note: For gap quarters, OE ratios, Observed and Expected values will be
 filled with 0.
 ''')

#  4c1. create final Trend DF
#   first pull all rows from dfFacqtr for specific columns
print('Create dfTrend by selecting a subset of cols from dfFacqtr','',sep='\n')
dfTrend = dfFacqtr[['Medicare ID',
                     'Facility Name',
                     'Facility Abbreviation',
                     'Benchmark',
                     'Metric Code',
                     'Metric Description',
                     'YearQuarter',
                     'Qualified',
                     'Observed_src',
                     'Expected_src',
                     'OE_ratio_src',
                     'Observed',
                     'Expected',
                     'OE_ratio',
                     'Bench',
                     'Average Observed',
                     'Average Expected']].copy()
print(f'dfTrend contains {dfTrend.shape[0]:,g} records.','',sep='\n')
print(f'dfRefTrend contains {dfRefTrend.shape[0]:,g} records.','',sep='\n')
#  4c2. merge with dfRefTrend left to add missing quarters
print('''4c2. Create dfTrendAll via merging dfTrend with dfRefTrend 
      to add missing quarters.''')
dfTrendAll = pd.merge(dfRefTrend, dfTrend, how='left', indicator=True)
print(dfTrendAll['_merge'].value_counts(),'',sep='\n')
print(f'dfTrendAll contains {dfTrendAll.shape[0]:,g} records post merge.',
      'which should equal dfRefTrend record count above.','',sep='\n')
# why do I have these array variables?
print('dfTrend has these measures:')
v_src_array = dfTrend['Metric Description'].unique()
print(v_src_array,'',sep='\n')
print('dfRefTrend has these measures:')
v_ref_array = dfRefTrend['Metric Description'].unique()
print(v_ref_array,'',sep='\n')

#4c. Replace missing quarter Indexes, Observed and expected with 0
#   by using the _merge field to identify left_only rows which need filling.
print('For gap quarters that have no data, fill Indexes, Observed & Expected '
      'valueswith 0 and Bench with 1 where _merge = left_only.')
gap_fields = ['OE_ratio_src', 'Observed_src', 'Expected_src',
              'OE_ratio', 'Observed', 'Expected']
for gap_field in gap_fields:
    dfTrendAll.loc[dfTrendAll['_merge'] == 'left_only', gap_field] = 0

# Add 1 to the bench field where missing. 
dfTrendAll.loc[dfTrendAll['_merge'] == 'left_only',
                                      'Bench'] = 1

#drop the _merge field and print sample.
print()
dfTrendAll.drop('_merge', axis=1,inplace=True)
print('Sample rows from dfTrendAll:')
print(dfTrendAll.head(),'', sep='\n')

# Add a Key field to provide a look up code in Excel
dfTrendAll['LU Key'] = dfTrendAll['Metric Code'] + dfTrendAll['YearQuarter']
print('dfTrendAll contains these record counts per measure.')
print(dfTrendAll['Metric Code'].value_counts(sort=True,dropna=False), '', sep='\n')

# export some check files to csv
print(f'Exporting dfTrendAll to {P_SRC}/TrendAll.csv')
dfTrendAll.to_csv(f"{P_SRC}/TrendAll.csv", index=False, sep=',', na_rep='')
print(f'Exporting dfTrend to {P_SRC}/Trend.csv')
dfTrend.to_csv(f"{P_SRC}/Trend.csv", index=False, sep=',', na_rep='')
print(f'Exporting dfRefTrend to {P_SRC}/RefTrend.csv')
dfRefTrend.to_csv(f"{P_SRC}/TrendRef.csv", index=False, sep=',', na_rep='')


# 4d. current 4 quarters data
# Meets excel rqmnts for populating the tbl_curr4qtrs_py table
#   in the Current 4 Qtrs tab
# The tbl_curr4qtrs excel table provides data used to populate the current
#  period tables to the right of each trend graph on the Dashboard tab.
# remove Overall Metric as it is not relevant in this data set.
print('-'*80)
print('''4d. Create dfCurr4qtrs which is a subset of columns from dfFac
 with the overall metric removed. This dataframe is used to populate
 the tbl_curr4qtrs_py excel table This table is used to populate
  current period tables to the right of each trend graph. 
 ''')

dfCurr4qtrs = dfFac.loc[dfFac['Metric Code'] != 'O',
                        ['LU Key',
                         'Medicare ID',
                         'Facility Name',
                         'Facility Abbreviation',
                         'Benchmark',
                         'Metric Code',
                         'Metric Description',
                         'Qualified',
                         'Observed_src',
                         'Expected_src',
                         'Recent_src',
                         'Average Observed',
                         'Average Expected']]
print(f'dfCurr4qtrs contains {dfCurr4qtrs.shape[0]:,g} records.','',sep='\n')
print('Sample rows from dfCurr4qtrs:')
print(dfCurr4qtrs.head(),'', sep='\n')

# 4e. current quarter data 
#  meets excel rqmmnts for populating the tbl_currqtr_py table in the
#  Current Qtr tab. This tab supplies data for the graphs displayed in the
#  BG tab which compares to 100Top winners rather than databridge Top Decile.
#  Pulls same measures shown in 2x2 plot except for Overall and adds 30D RS.
#  filter for the required metrics and current quarter

print('-'*80)
print('''4e. Create dfCurrqtr which is a subset of columns from dfFac
 for 2x2 metrics (excluding the overall) and the SAF 30 Day Readmits.
 This dataframe is used to populate the currqtr_py table excel table which
 is used to populate data in the BG tab which compares to 100Top winners
 rather than databridge Top Decile benchmarks. 
 ''')

# Using iteration to create three dataframes which are then concatenated into one.

dataframes = []

# Ensure all metric variables are in a list format to use for iteration
metrics_quarters = [(list(MSR_CURR_QTR), RPT_CURR_QTR),
                    (list(MSR_CURR_QTR_SAF), RPT_CURR_QTR_SAF),
                    ([MSR_CURR_QTR_MSPB], RPT_CURR_QTR_MSPB)] 

# Now iterate for each metric list and quarter
for metric, quarter in metrics_quarters:
    condition = dfFacqtr['Metric Code'].isin(metric) & (dfFacqtr['YearQuarter'] == quarter)

    df = dfFacqtr.loc[condition, ['Medicare ID',
                                      'Facility Name',
                                      'Facility Abbreviation',
                                      'Benchmark Class',
                                      'YearQuarter',
                                      'Benchmark',
                                      'Metric Code',
                                      'Metric Description',
                                      'Qualified',
                                      'Observed_src',
                                      'Expected_src',
                                      'OE_ratio_src',
                                      'Average Observed']]
    dataframes.append(df)

# concatenate into one dataframe
dfCurrqtr = pd.concat(dataframes, ignore_index=True)

# add a lookup key whcih ci used in excel
dfCurrqtr['LU Key'] = dfCurrqtr['Metric Code']

# reorder columns for formatting
dfCurrqtr = dfCurrqtr.reindex(columns=['LU Key',
                                       'Medicare ID',
                                       'Facility Name',
                                       'Facility Abbreviation',
                                       'Benchmark Class',
                                       'YearQuarter',
                                       'Benchmark',
                                       'Metric Code',
                                       'Metric Description',
                                       'Qualified',
                                       'Observed_src',
                                       'Expected_src',
                                       'OE_ratio_src',
                                       'Average Observed'])
                                       
print(f'dfCurrqtr has been created for {RPT_CURR_QTR} for these metrics:')
print(f'{MSR_CURR_QTR}, {MSR_CURR_QTR_SAF} and {MSR_CURR_QTR_MSPB}.')
print(f' and contains {dfCurrqtr.shape[0]:,g} records.','',sep='\n')

# create final output by adding 100Top winner and non winnder values
dfCurrqtr = pd.merge(dfCurrqtr, dfBench
  [['Metric Code', 'Benchmark Class', 'Winners', 'Non Winners']],
  left_on=['Metric Code', 'Benchmark Class'],
  right_on=['Metric Code','Benchmark Class'],
  how='left', indicator=True)
print('''100Top static winner and non winner values have been added by a merge
with dfBench via an left join on Metric Code and Benchmark Class.
Note: there are no 100Top values for the 30 Day readmit metrics.''')
# print merge results
print(dfCurrqtr['_merge'].value_counts())
print()
dfCurrqtr.drop('_merge', axis=1,inplace=True)
# print final for log
print(f'dfCurrqtr contains {dfCurrqtr.shape[0]:,g} records.','',sep='\n')
print('Sample rows from dfCurrqtr:')
print(dfCurrqtr.head(),'', sep='\n')


# create databridge quarters for each facility
dfRefDbQtrs = dfRefMajor.loc[dfRefMajor['Metric Code'] == 'A',
                               ['Facility Name',
                                'Facility Abbreviation',
                                'YearQuarter']]

print('-'*80)
print('''4f. Create dfHaiYearFinal which is used to populate the HAI tables in 
      excel reports. The final df contains HAI measure outcomes by 
      facility, HAI measure and rolling year. Each rolling year contains 
      4 quarters.''') 

# Create HAI final dataframe - aggregation by year
print('Create dfHaiYear by aggregating by facility, Metric Code and rolling year.')
dfHaiYear = dfHAI.groupby(['Facility ID', 'Measure', 'Rolling Year'], 
                          as_index=False)[['Observed_c', 'Expected_c']].sum()
# Rename the columns Measure to Metric Code and Facility ID to Medicare ID
print('Rename a few columns to match prime requirements.','',sep='\n')
dfHaiYear = dfHaiYear.rename(columns={'Measure': 'Metric Code',
                                      'Facility ID': 'Medicare ID'})
# Relabel Metric Code values 
# First change these values

code_replace = {'CDIF': 'CDIFF',
                'SSI Colon': 'SSI-CS',
                'SSI Hyst': 'SSI-HY'}
print('Renaming a few metric codes.')
print(f'Codes to be renamed are {code_replace}','',sep='\n') 
dfHaiYear['Metric Code'] = dfHaiYear['Metric Code'].replace(code_replace)
                                             
# add I- in front of each metric code to match Prime reporting requirements
print('Adding "I-" in front of each metric code.', '',sep='\n')
dfHaiYear['Metric Code'] = 'I-' + dfHaiYear['Metric Code']
# Create a new field based on Observed_c/Expected_c
print('Calculate an SIR score for each record where expected is >= 1.')
print('Records with expected values < 1 will be nan','',sep='\n')
dfHaiYear['SIR'] = np.where(dfHaiYear['Expected_c'] >= 1, 
                            dfHaiYear['Observed_c'] / dfHaiYear['Expected_c'], np.nan)
# change nan to Expected < 1
print('Change the nan SIR values to "Expected < 1".','',sep='\n') 
dfHaiYear['SIR'] = dfHaiYear['SIR'].fillna('Expected < 1')
# count the number of rows where expected < 1 for checking

# Create HAI Composite dataframe which includes mean SIRs of HAI measures
#  calculate these means based on rows where expected values >= 1
#  create df with expected < 1 rows removed
print('''Create a HAI composite DF which will contain composite scores
      for each facility and rolling year by taking the mean of the HAI 
      submeasure SIR scores where SIR <> "Expected < 1".''')
# create a filter to keep only records with a valid SIR score      
dfHaiYearFilter = dfHaiYear[dfHaiYear['SIR'] != 'Expected < 1'] 
#  now compute HAI composite dataframe
dfHaiComp = dfHaiYearFilter.groupby(['Medicare ID', 'Rolling Year']).agg({'SIR': 'mean'}).reset_index()
# add columns to meet the full HAI reporting requirements (match dfHaiYear)
dfHaiComp['Metric Code'] = 'I'
dfHaiComp['Observed_c'] = 'N/A'
dfHaiComp['Expected_c'] = 'N/A'
# reorder columns to match dfHaiYear
dfHaiComp = dfHaiComp.reindex(columns=['Medicare ID',
                                        'Metric Code',
                                        'Rolling Year',
                                        'Observed_c',
                                        'Expected_c',
                                        'SIR'])
print(f'dfHaiComp contains {dfHaiComp.shape[0]:,g} records.','',sep='\n')

# concat dfHaiComp & dfHaiYear to create final dataframe
print('Create dfHaiYearFinal by concatenating dfHaiComp and dfHaiYear.')
print()
dfHaiYearFinal = pd.concat([dfHaiYear, dfHaiComp], ignore_index=True)

# Add in facility name, metric description and benchmarks with merges

# Metric Description
print('Add the Metric description to dfHaiYearFinal via merge with dfMetricRef.',
      sep='\n')
dfHaiYearFinal = pd.merge(dfHaiYearFinal, dfMetricRef, how='left', indicator=True)
print(dfHaiYearFinal['_merge'].value_counts())
print()
dfHaiYearFinal.drop('_merge', axis=1,inplace=True)

# Facility Name
print('Add the Facility Name and abbreviationto dfHaiYearFinal via merge with dfHosp.',
      sep='\n')
dfHaiYearFinal = pd.merge(dfHaiYearFinal, dfHosp[['Medicare ID',
                                                  'Facility Name', 
                                                  'Facility Abbreviation']],
                          how='left', indicator=True)
print(dfHaiYearFinal['_merge'].value_counts())
print()
dfHaiYearFinal.drop('_merge', axis=1,inplace=True)

# Benchmark score
print('Add the 100Top HAI benchmark to dfHaiYearFinal via merge with dfBenchHAI.',
      sep='\n')
dfHaiYearFinal = pd.merge(dfHaiYearFinal, dfBenchHAI[['Metric Code', 
                'Expected SIR']] , how='left', indicator=True)
print(dfHaiYearFinal['_merge'].value_counts())
print()
dfHaiYearFinal.drop('_merge', axis=1,inplace=True)

# Reorder columns
dfHaiYearFinal = dfHaiYearFinal.reindex(columns=['Medicare ID',
                                                 'Facility Name',
                                                 'Facility Abbreviation',
                                                 'Metric Code',
                                                 'Metric Description',
                                                 'Rolling Year',
                                                 'SIR',
                                                 'Expected SIR',
                                                 'Observed_c',
                                                 'Expected_c'])

# sort dfHaiYearFinal
dfHaiYearFinal = dfHaiYearFinal.sort_values(by=['Facility Name', 'Metric Code', 'Rolling Year'])
print('dfHaiYearFinal contains these final columns:')
print(dfHaiYearFinal.info(verbose=True, show_counts=True),'',sep='\n')
print('Sample for dfHaiYearFinal:')
print(dfHaiYearFinal.head(),'', sep='\n')

# check measure/Rolling Year fill rate
dfHaiCheck = dfHaiYearFinal.groupby(['Facility Name', 'Medicare ID',
                    'Rolling Year']).agg({'Metric Code': 'count'}).reset_index()
# Check for any Facility/year that has a Metric Code count < 7
# Most facilities should have 7 per year except those where a HAI composite 
# cannot be computed because all submeasures had expected values < 1
print('Checking facility/year records with count less than 7.')
dfHaiLT7 = dfHaiCheck[dfHaiCheck['Metric Code'] < 7]
print('Most facilities should have 7 records per year.')
print('However, a facility/year may have 6 because a composite could not be computed')
for facility, group in dfHaiLT7.groupby('Facility Name'):
    print(f'Facility Name: {facility}\n')
    print(group)
    print('\n' + '-' * 80 + '\n')
print('HAI df creation complete.','',sep='\n')
# Export to CSV for QA checks - 
dfHaiYearFinal.to_csv(f"{P_SRC}/HAI_Final_Ckeck.csv", index=False, sep=',', na_rep='')

#%%
#####################################################################
# ITERATION FOR FINAL EXCEL OUTPUT to template that uses trend tables
# Uses dataframes created in section above to populate excel tables.
# Iterates by Facility name and saves the excel template as final facilty file.



# make a facility variable for iteration using the data in dfHosp reference
v_fac_array = dfHospLoop['Facility Name'].unique()
# count the number of facilities in the variable
facility_count = len(v_fac_array)
print()
print('-'*80)
print('Now running the facility Excel report iteration.','',sep='\n')
print(f'{facility_count} individual Excel reports will be '
      f'produced for these facilities:','',sep='\n')
for i, fac in enumerate(v_fac_array, start=1):
    print(f'  {i}. {fac}')
print()

for i, fac_name in enumerate(v_fac_array, start=1):
    print(f' #{i}. Creating {fac_name}{RPT_SUFFIX}.xlsx')
    # ref_hosp data ##########################################################
    # meets excel rqmnts for populating the tbl_hosp_py table in the Facility tab.
    
    dfexp_hosp = dfHosp.loc[dfHosp['Facility Name'] == fac_name,
                         ['Medicare ID',
                         'Facility Name',
                         'Facility Abbreviation',
                         'Benchmark Class',
                         'Quarters Available']]
    
    # Databridge quarters
    dfexp_qtr = dfRefDbQtrs.loc[dfRefDbQtrs['Facility Name'] == fac_name,
                                 ['Facility Abbreviation',
                                  'YearQuarter']]

    # 2x2 data ###############################################################
    # select for a sinle facility
    dfexp_2x2 = df2x2.loc[df2x2['Facility Name'] == fac_name]


    # trend data #############################################################
    # select for a single facility
    dfexp_trend = dfTrendAll.loc[dfTrendAll['Facility Name'] == fac_name,
                                [ 'LU Key', 'Medicare ID',
                                 'Facility Name',
                                 'Facility Abbreviation',
                                 'Benchmark',
                                 'Metric Code',
                                 'Metric Description',
                                 'YearQuarter',
                                 'Qualified',
                                 'Observed_src',
                                 'Expected_src',
                                 'OE_ratio_src',
                                 'Observed',
                                 'Expected',
                                 'OE_ratio',
                                 'Bench',
                                 'Average Observed',
                                 'Average Expected']]


    # current 4 quarters data ################################################
    # Meets excel rqmnts for populating the tbl_curr4qtrs_py table
    #   in the Current 4 Qtrs tab
    # The tbl_curr4qtrs excel table provides data used to populate the current
    #  period tables to the right of each trend graph on the Dashboard tab.

    # select for single facility 
    dfexp_curr4qtrs = dfCurr4qtrs.loc[dfCurr4qtrs['Facility Name'] == fac_name]

    # current quarter data #######################################################
    # meets excel rqmmnts for populating the tbl_currqtr_py table in the
    #  Current Qtr tab. This tab supplies data for the graphs displayed in the
    #   BG tab 
    #   current quarter performance for the same measures shown in 2x2 plot.
    # filter for the facility and current quarter

    dfexp_currqtr = dfCurrqtr.loc[dfCurrqtr['Facility Name'] == fac_name]
    

    #HAI table on the HAI Table Results tab

    dfexp_hai_all = dfHaiYearFinal.loc[dfHaiYearFinal['Facility Name'] == fac_name]
    
    
    # Making dfs to populate the HAI tables on the Dashboard tab
    # HAO codes to use
    HAI_codes = ['I', 'I-CAUTI', 'I-CDIFF', 'I-CLABSI', 'I-MRSA', 'I-SSI-CS', 'I-SSI-HY']
    # Columns to pull per table
    table_columns = ['Metric Code', 'Rolling Year', 'SIR', 'Expected SIR',
                      'Observed_c', 'Expected_c']

    # Create an empty dictionary to store the DataFrames
    df_dict = {}
    
    # Iterate through the metric codes and create the DataFrames
    for HAI_code in HAI_codes:
        df_key = f'dfHAI_{HAI_code}'
        df_dict[df_key] = dfHaiYearFinal.loc[(dfHaiYearFinal['Facility Name'] == fac_name)
                                            & (dfHaiYearFinal['Metric Code'] == HAI_code),
                                            table_columns].copy()
 
    # Access the DataFrames using their corresponding keys
    dfexp_hai_comp = df_dict['dfHAI_I']
    dfexp_hai_cauti = df_dict['dfHAI_I-CAUTI']
    dfexp_hai_cdiff = df_dict['dfHAI_I-CDIFF']
    dfexp_hai_clabsi = df_dict['dfHAI_I-CLABSI']
    dfexp_hai_mrsa = df_dict['dfHAI_I-MRSA']
    dfexp_hai_ssi_cs = df_dict['dfHAI_I-SSI-CS']
    dfexp_hai_ssi_hy = df_dict['dfHAI_I-SSI-HY']
    
    
    # Excel population using xlwings
    table_info = [
        ('Trend Metric Keys', 'tbl_dbqtr_py', dfexp_qtr),
        ('2x2', 'tbl_2x2_py', dfexp_2x2),
        ('Current 4 Qtrs', 'tbl_curr4qtrs_py', dfexp_curr4qtrs),
        ('Trend Data', 'tbl_trend_py', dfexp_trend),
        ('Current Qtr', 'tbl_currqtr_py', dfexp_currqtr),
        ('Facility', 'tbl_hosp_py', dfexp_hosp),
        ('HAI Table Results', 'tbl_hai_all', dfexp_hai_all),
        ('Dashboard', 'tbl_hai_comp_d', dfexp_hai_comp),
        ('Dashboard', 'tbl_hai_cauti_d', dfexp_hai_cauti),
        ('Dashboard', 'tbl_hai_cdiff_d', dfexp_hai_cdiff),
        ('Dashboard', 'tbl_hai_clabsi_d', dfexp_hai_clabsi),
        ('Dashboard', 'tbl_hai_mrsa_d', dfexp_hai_mrsa),
        ('Dashboard', 'tbl_hai_ssi_cs_d', dfexp_hai_ssi_cs),
        ('Dashboard', 'tbl_hai_ssi_hy_d', dfexp_hai_ssi_hy)
    ]


    # Excel population using xlwings
    # load workbook
    app = xw.App(visible=False)
    wb = xw.Book(f'{P_SRC}/{F_TEMPLATE}')
    time.sleep(5)

    for sheet, table, df in table_info:
        ws = wb.sheets[sheet]
        ws.range(table).options(index=False, header=False).value = df
        time.sleep(2)
        del ws

    print()
    print(f'The facility report for {fac_name} has been created in:')
    print(f'Directory: {P_REPORTS}')
    print(f'File Name: {fac_name}{RPT_SUFFIX}.xlsx','',sep='\n')
    wb.save(f'{P_REPORTS}/{fac_name}{RPT_SUFFIX}.xlsx')
    wb.close()
    app.quit()



# specify the directory where reports are stored
reports_dir = P_REPORTS

# get a list of all files in the directory
all_files = os.listdir(reports_dir)

# filter the list for .xlsx files
xlsx_files = [file for file in all_files if file.endswith('.xlsx')]
print()
print(f'The Prime facility report run for {RPT_CURR_QTR} is complete!','',sep='\n')
# print the count of .xlsx files
print("Total number of Excel reports produced:", len(xlsx_files))
print() 
print(f'These reports in {P_REPORTS} are available for further QA:','',sep='\n')
# print the list of .xlsx files
for file in xlsx_files:
    print(' - ',file)

  

