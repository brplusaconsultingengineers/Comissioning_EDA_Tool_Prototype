import streamlit as st
import datetime as dt
import glob
import numpy as np
import pandas as pd
import os

def max_width():
    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

def prepare_BAS_for_altair_chart(df, baseload_max=None):
    """[summary]

    Parameters
    ----------
    AMI_prepared_df : [type]
        [description]
    peaks_df : [type]
        [description]
    baseload_max : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    source_df = df.copy()
    source_df = source_df.reset_index()
    source_df.rename(columns={ source_df.columns[1]: "index" }, inplace = True)
    return source_df

def read_BAS(DIR_DATA, dropna=True):
    """
    Returns dataframe from AMI data file in a useful format

    Parameters
    ----------
     DIR_DATA: string
        DIR_DATA (OR .csv output of st.file_uploader!) to AMI data file

    Returns
    ------
    pd.DataFrame
        dtindexed AMI dataframe with duplicates removed and only the 'power_kW' column.
    """
    BAS_data_list = []
    BAS_filepaths = glob.glob(os.path.join(DIR_DATA, "*.csv"))
    for filename in BAS_filepaths:
        df = pd.read_csv(filename, index_col=0, header=0, parse_dates=True)
        df = df.loc[~df.index.duplicated(keep='first')] #remove rows with duplicated indices
        BAS_data_list.append(df)    

    frame_out = pd.concat(BAS_data_list, axis=1, join='outer', ignore_index=False)
    frame_out_cleaned = frame_out.resample('15T').max() #might be changed depending on datastructure

    return frame_out_cleaned

def create_categorical_variables(df):
    '''
    """_summary_: Input Dataframe with Datetime64 indextype. Create datetime categorical variables for plotting

    Returns:
        _type_: DataFrame with Categorical variables
    """    '''
    #TODO create inputs for Holiday / regular day separation

    df['DayHour'] = df.index.hour
    df['DayofWeek'] = df.index.dayofweek
    df['WeekHour'] = df.DayHour + 24*df['DayofWeek']


    return df
