'''
Project Lead Engineer: Michael Swenson
Assistant Engineer: Taylor Roth
Date: 5/4/2022
Deliverable:
    Analyze RFGRNT of HRCH system trend points to correlate HRCH alarm status.
'''
#%% Import modules
import os
from pathlib import Path
from tkinter import Variable
from click import progressbar
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from sympy import var
from yaml import parse
import datetime
from datetime import datetime
# from pandas_profiling import ProfileReport
from plt_functions import KDE_plot, hued_scatterplot, pair_plot, line_plot
import glob
import statsmodels.api as sm
import statsmodels.formula.api as smf
from skimpy import clean_columns


%matplotlib inline

# %% Set filepaths for data import and results
DIR_MAIN = Path(r'C:\Users\TRoth\OneDrive - Bard, Rao + Athanas Consulting Engineers, LLC \Documents\Project Management\Bates')
DIR_DATA = DIR_MAIN / "Data"
DIR_DATA_RAW = DIR_DATA / "raw"
DIR_DATA_RAW_HRCH = DIR_DATA_RAW / "HRCH"
# Datafile Directories
DIR_DATA_RAW_HRCH_CWS = DIR_DATA_RAW_HRCH / "CWSide"
DIR_DATA_RAW_HRCH_HWS = DIR_DATA_RAW_HRCH / "HWSide"
DIR_DATA_RAW_RFGRNT = DIR_DATA_RAW_HRCH / "Refrigerant"

DIR_DATA_RAW_ACCH1 = DIR_DATA_RAW / "ACCH1"
DIR_DATA_RAW_ACCH2 = DIR_DATA_RAW / "ACCH2"
DIR_DATA_RAW_CHWS = DIR_DATA_RAW / "CHWSystem"

DIR_DATA_PROCESSED = DIR_DATA / "processed"
DIR_RESULTS = DIR_MAIN / "Results"

#%% Import HRCH Data
RFGRNT_HRCH_data_list = []
RFGRNT_HRCH_files = glob.glob(os.path.join(DIR_DATA_RAW_RFGRNT, "*.csv"))
for filename in RFGRNT_HRCH_files:
    df = pd.read_csv(filename, index_col=0, header=0, parse_dates=True)
    df = df.loc[~df.index.duplicated(keep='first')] #remove rows with duplicated indices
    RFGRNT_HRCH_data_list.append(df)    

RFGRNT_HRCH_df = pd.concat(RFGRNT_HRCH_data_list, axis=1, join='outer', ignore_index=False)

# Note alarm values are not 15 minute interval. Status change at occurance.
# for analysis, resampling of the timestamps to align with other system
# parameters is required. Once resampled to 15T, NaN values are zeroed to 
# reflect 'no alarm'

#%%
RFGRNT_HRCH_df.head()
#%%
RFGRNT_HRCH_df.tail()
#%% 
RFGRNT_HRCH_df.info()
#%%
RFGRNT_HRCH_df.describe()
#%% Save raw aligned file
RFGRNT_HRCH_df.to_csv(DIR_DATA_PROCESSED / "RFGRNT_HRCH_Data_Aligned_Raw.csv")

# #%% Create Profile Report for EDA
# RFGRNT_HRCH_df_profilereport = ProfileReport(RFGRNT_HRCH_df.sample(20),  progress_bar=True)

# #%% Save profile report for viewing
# RFGRNT_HRCH_df_profilereport.to_file(DIR_RESULTS / "RFGRNT_HRCH_ProfileReport.html")
#%% Drop NaN to isolate around fault alarms. Alarms occur at mixed interval, so resampling
# at max value will align. No other values will be resampled.
Alarm_prep_df = RFGRNT_HRCH_df.resample('15T').max()

RFGRNT_HRCH_df_WA = pd.DataFrame(Alarm_prep_df['HRCH_1_WarningAlarm'].dropna())
RFGRNT_HRCH_df_FA = pd.DataFrame(Alarm_prep_df['HRCH_1_FaultAlarm'].dropna())
RFGRNT_HRCH_df_PA = pd.DataFrame(Alarm_prep_df['HRCH_1_ProblemAlarm'].dropna())

Alarm_df = RFGRNT_HRCH_df_WA.join(RFGRNT_HRCH_df_FA, how='outer')
Alarm_df = Alarm_df.join(RFGRNT_HRCH_df_PA, how='outer')

Alarm_iso_df = Alarm_df.join(RFGRNT_HRCH_df.drop(['HRCH_1_WarningAlarm', 'HRCH_1_FaultAlarm', 'HRCH_1_ProblemAlarm'], axis=1),  how='inner')
Alarm_iso_df = Alarm_iso_df.fillna(value=0)#fill nan values with 0 signalling no alarm
Alarm_iso_df.info()
#%% Resample dataframe to 15 minute interval by MAX.
# Only values resampled are alarm indicators
RFGRNT_HRCH_df = RFGRNT_HRCH_df.resample('15T').max()
RFGRNT_HRCH_df.fillna(value=0, inplace=True) # alarm values NaN while not active
RFGRNT_HRCH_df.info()


#%% Create alarm status column ranging 1-3 dependent on which alarm is active For Plotting
def str_categorise(row):  
    if row['HRCH_1_WarningAlarm'] > 0 :
        return 'Warning Alarm'
    elif row['HRCH_1_FaultAlarm'] > 0 :
        return 'Fault Alarm'
    elif row['HRCH_1_ProblemAlarm'] > 0 :
        return 'Problem Alarm'
    return 'No Alarm'
#%% Create Plotting DF of all data with zeroed NaNs
# #Create Alarm Status Indicator Column from function above. Drop Alarm values.
RFGRNT_HRCH_df_plt = RFGRNT_HRCH_df.copy()
RFGRNT_HRCH_df_plt['Alarm_Status'] = RFGRNT_HRCH_df_plt.apply(lambda row: str_categorise(row), axis=1)
RFGRNT_HRCH_df_plt = RFGRNT_HRCH_df_plt.drop(['HRCH_1_WarningAlarm', 'HRCH_1_FaultAlarm', 'HRCH_1_ProblemAlarm'], axis=1)
#%% Create Plotting DF of all data with only active alarm points 
# Create Alarm Status Indicator Column from function above
Alarm_iso_df_plt = Alarm_iso_df.copy()
Alarm_iso_df_plt['Alarm_Status'] = Alarm_iso_df_plt.apply(lambda row: str_categorise(row), axis=1)
Alarm_iso_df_plt = Alarm_iso_df_plt.drop(['HRCH_1_WarningAlarm', 'HRCH_1_FaultAlarm', 'HRCH_1_ProblemAlarm'], axis=1)

'''
Being Exploratory Graphical Data Analysis

'''
#%% Create pairplot isolated Alarm data for data
pair_plot(Alarm_iso_df_plt, save_filename='Alarm_Only')
#%%Create pairplot all data for data
pair_plot(RFGRNT_HRCH_df_plt, save_filename='All_Data')
#%% Create KDE Plots to isolate indpdnt variable of interest
KDE_plot(Alarm_iso_df_plt, save_filename='Alarm_Only')
#%% Create KDE Plots to isolate indpdnt variable of interest
KDE_plot(RFGRNT_HRCH_df_plt)
#%%
hued_scatterplot(Alarm_iso_df_plt, save_filename='Alarm_Only')
#%%
hued_scatterplot(RFGRNT_HRCH_df_plt)

#%%
plt.style.use('bmh') #seaborn-darkgrid, fivethirtyeight
plt.figure(figsize=(10,6))
plt.title(f"Line Plot of Condenser Pressure")
plt.suptitle(f"Red Dot show Fault Alarms")
plt.ylabel(f'Condenser PSI_Gauge')
plt.xlabel('DateTime Index')
markers_on = RFGRNT_HRCH_df_plt.loc[RFGRNT_HRCH_df_plt.iloc[:,-1] == "Fault Alarm"].index
sns.lineplot(x=RFGRNT_HRCH_df_plt.index, y=RFGRNT_HRCH_df_plt['HRCH_1_CondSatTemp(°F)'])
RFGRNT_HRCH_df_plt['HRCH_1_CondSatTemp(°F)'][markers_on].plot(style='ro')
# plt.xticks(rotation=45)

plt.show()  


#%%
iso_data = RFGRNT_HRCH_df_plt['2022-04-29':'2022-05-06']
iso_data['DayHour'] = iso_data.index.hour
iso_data['DayofWeek'] = iso_data.index.dayofweek
iso_data['WeekHour'] = iso_data.DayHour + iso_data.DayofWeek*24
#%%
plt.style.use('bmh') #seaborn-darkgrid, fivethirtyeight
plt.figure(figsize=(10,6))
plt.title(f"Line Plot of GHW Return Temperature")
plt.suptitle(f"Red Dot show Fault Alarms")
plt.ylabel(f'Degrees Fahrenheit')
plt.xlabel('DateTime Index')
markers_on = iso_data.loc[RFGRNT_HRCH_df_plt['Alarm_Status'] == "Fault Alarm"].index
sns.lineplot(x=iso_data.index, y=iso_data['HW_Sys_HrCh_HrChGhwSTmp(°F)'])
iso_data['HW_Sys_HrCh_HrChGhwSTmp(°F)'][markers_on].plot(style='ro')

plt.show() 












#%%
iso_data_melt = iso_data[['HRCH_1_CondPressure(psi)','WeekHour','Alarm_Status']].melt(id_vars=["WeekHour", 'Alarm_Status'])
#%%
plt.figure(figsize=(12,6))
plt.style.use('bmh') #seaborn-darkgrid, fivethirtyeight
plt.title(f"HRCH_1_CondPressure(psi)")
plt.xlabel('Hour of Week')
plt.ylabel('Condenser Pressure (PSIG)')

sns.stripplot(x=iso_data_melt['WeekHour'], y=iso_data_melt.value,
                data=iso_data_melt, hue=iso_data_melt.Alarm_Status)
plt.legend()
plt.show()


#%% Create numeric alarm status column ranging 1-3 dependent on which alarm is active for regression
def num_categorise(row):  
    if row['HRCH_1_WarningAlarm'] > 0 :
        return 1 #'HRCH_1_WarningAlarm'
    elif row['HRCH_1_FaultAlarm'] > 0 :
        return 2 #'HRCH_1_FaultAlarm'
    elif row['HRCH_1_ProblemAlarm'] > 0 :
        return 3 #'HRCH_1_ProblemAlarm'
    return 0
#%% Create Alarm Status Indicator Column from function above. Drop Alarm values.
RFGRNT_HRCH_df_reg = RFGRNT_HRCH_df.copy()
RFGRNT_HRCH_df_reg['Alarm_Status'] = RFGRNT_HRCH_df_reg.apply(lambda row: num_categorise(row), axis=1)
RFGRNT_HRCH_df_reg = RFGRNT_HRCH_df_reg.drop(['HRCH_1_WarningAlarm', 'HRCH_1_FaultAlarm', 'HRCH_1_ProblemAlarm'], axis=1)
#%% Create Alarm Status Indicator Column from function above
Alarm_iso_df_reg = Alarm_iso_df.copy()
Alarm_iso_df_reg['Alarm_Status'] = Alarm_iso_df_reg.apply(lambda row: num_categorise(row), axis=1)
Alarm_iso_df_reg = Alarm_iso_df_reg.drop(['HRCH_1_WarningAlarm', 'HRCH_1_FaultAlarm', 'HRCH_1_ProblemAlarm'], axis=1)












#%% Clean names for linear regression analysis.
RFGRNT_HRCH_df_reg_clean = clean_columns(RFGRNT_HRCH_df_reg, replace={'%':'pct'})
Alarm_iso_df_reg_clean = clean_columns(Alarm_iso_df_reg, replace={'%':'pct'})
# column_str = str(clean_columns(RFGRNT_HRCH_df_status, replace={',':'+', '%':'pct', '       ':''}).columns)
# print(column_str[8:386].replace(',','+'))
#%% Reg Model
Alarm_formula = "alarm_status ~ ch_w_sys_hrch_ch_p_04_spd_cmd_pct +\
       ch_w_sys_hrch_ch_p_05_spd_cmd_pct+ ch_w_sys_hrch_hr_ch_dif_pr_psi+\
       ch_w_sys_hrch_hrch_iso_vlv_pos_fb_pct+ ch_w_sys_hrch_hrch_s_tmp_f+\
       hrch_1_chiller_cap_pct+ hrch_1_ent_cond_wtr_tmp_f+\
       hrch_1_ent_evap_wtr_tmp_f+ hrch_1_lvg_cond_wtr_tmp_f+\
       hrch_1_lvg_evap_wtr_tmp_f+ oa_t_f + 1"

Alarm_formula_trimmed = "alarm_status ~ ch_w_sys_hrch_hrch_s_tmp_f + \
                            hrch_1_ent_cond_wtr_tmp_f+\
                            hrch_1_lvg_evap_wtr_tmp_f+ oa_t_f + 1"

#%% Create OLS to isolate correlated variables for Warning Alarm
#Not enough instances of Alarm to correlate
regression_results = smf.ols(Alarm_formula, data=RFGRNT_HRCH_df_reg_clean).fit()
print(regression_results.summary())

#%% Create OLS to isolate correlated variables for Warning Alarm
#Not enough instances of Alarm to correlate
regression_results = smf.ols(Alarm_formula, data=Alarm_iso_df_reg_clean).fit()
print(regression_results.summary())

#%% Create OLS to isolate correlated variables for Warning Alarm
#Not enough instances of Alarm to correlate
regression_results = smf.ols(Alarm_formula_trimmed, data=Alarm_iso_df_reg_clean).fit()
print(regression_results.summary())


#%%
