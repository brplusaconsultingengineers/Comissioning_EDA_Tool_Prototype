#%%
from tracemalloc import start
import pandas as pd
import os
from path import Path
import numpy as np
from transformation.raw_data_processing import BASdata
import seaborn as sns

'''
Add monthly bucket visualization of operational parameters
X-axis changes
Standardized MBCx report graphics and analytics
'''
#%%
DIR_CWD = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILEPATH =  DIR_CWD / "Data" / "processed" / "RFGRNT_HRCH_Data_Aligned_Raw.csv"

# %%
df = pd.read_csv(FILEPATH, index_col=0, parse_dates=True).dropna()
df.info()
# %%
df.columns
# %%
BAS_object = BASdata()

# ingest data into the object.
BAS_object.data_ingest(df)
#%%
BAS_object.all_data.info()
#%%
start_date = pd.to_datetime("2022-04-10")
end_date = pd.to_datetime("2022-05-01")

# %%
# prepare AMI dataframe
BAS_object.subset_data = BAS_object.all_data.truncate(before=start_date, after=end_date)

# %%
BAS_object.subset_data['prepost'] = np.where(BAS_object.subset_data.index > start_date, 1, 0)
# %%
BAS_object.subset_data.info()
# %% PLot load profile mean by day of week
categorical_dataframe = BAS_object.subset_data.copy()
categorical_dataframe['DayHour'] = categorical_dataframe.index.hour
categorical_dataframe['DayofWeek'] = categorical_dataframe.index.dayofweek
categorical_dataframe['WeekHour'] = categorical_dataframe.DayHour + categorical_dataframe.DayofWeek*24
categorical_dataframe.head()
#%%
daily_load_profile = categorical_dataframe.groupby(['DayofWeek','DayHour']).mean().reset_index()
daily_load_profile.head()
#%%
sns.lineplot(x=daily_load_profile['DayHour'], y=daily_load_profile['HRCH_1_CondPressure(psi)'],
                hue=daily_load_profile.DayofWeek)


# %%
sns.lineplot(x=categorical_dataframe.groupby(['DayofWeek','DayHour']).mean().index,
            y=categorical_dataframe['HRCH_1_CondPressure(psi)'])
# %%
