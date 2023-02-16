'''
Lead Engineer Analyst & Developer: Taylor Roth
Co-Developer: Michael Swenson
Date: 6/1/2022
Deliverable: 
    Develop Streamlit Application to ingest a standardized dataframe for RetroCommissioning Diagnostic Purposes.
    Modular functionality:
        Column names should reflect the naming convention used in standardized reporting formats
        User input to define
            pre/post measure dates
            indicator column

        Generate useful & standardized diagnostic plots for report integration (export function necesary)
        Generate useful & standardized metrics for reporting values

Source Code: pardir/src
    plt_functions: modularized plotting functions
        next development steps: 
            (1) build out to accept current processed script

    raw_data_processing: custom script for each project to process raw data into acceptable format for RCx Commissioning Script
        next development steps: 


    RCx_diagnostic_analysis_modularized: Streamlit web app interface
        next development steps: 
            (1) Develop to accept excel file in datetime index format and n_columns points of interest
            (2) Produce charts using plt_functions
            (3) accept user inputs for categorical variable. If selected, produce diagnostic charts with categorical hue/classification
                    weekhour
                    weekday
                    dayhour
                    season
                    alarm_status
            (4) Roll out to Michael for review

Overall next steps: 
    - Create Environment.yml file for reproducibility
    - Establish a central repository location for tool development (Atlassian?)
    - 
'''
#%%
#Import Modules Required for Applicaiton
from typing import Any
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import os
import altair as alt
from PIL import Image
import datetime as dt
from copy import deepcopy
from path import Path

from utils import prepare_BAS_for_altair_chart, create_categorical_variables
from transformation.raw_data_processing import BASdata
from Chart_functions import get_chart
#%% Establish root filepath for reference
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#Set tool header with image
image = Image.open(os.path.join(ROOT_PATH, "media/BR+A_graphic_1.jpg"))
st.image(image, width=200)
# colors for graphics
color_domain = ["peak", "intermediate", "base"]
color_range = ["crimson", "orange", "green", 'black']
ESTIMATOR_TYPES = ["smart defaults", "custom"]
# title
st.title("Retro-Comissioning Analytics Tool Prototype")



# User input for BAS file directory
input_file = st.file_uploader(
            "Upload BAS data .csv file.", type=["csv"]
            )
if (input_file is not None) and input_file.name.endswith(".csv"):
    df = pd.read_csv(input_file, index_col=0, parse_dates=True).dropna()
    
    Begin_Date = df.index[0]
    End_Date = df.index[-1]
    print(f'Start Date: {Begin_Date}')
    print(f'End Date: {End_Date}')
else:
    st.stop()

# make an instance of the class.
BAS_object = BASdata()

# ingest data into the object.
BAS_object.data_ingest(df)

# set variables with a mix of automated and user inputs.
date_max = BAS_object.all_data.index.max()
date_min = BAS_object.all_data.index.min()
start_date = date_min
#TODO create slider for daterange selection
# start_date, end_date = st.slider(label='Date Range for Analysis',
#                                     min_value=date_min,
#                                     max_value=date_max,
#                                     value=,
#                                     format= "MM/DD/YY - hh:mm")

start_date = st.sidebar.date_input("start date", start_date, date_min, date_max)
end_date = st.sidebar.date_input("end date", date_max, start_date, date_max)

BAS_object.subset_data = BAS_object.all_data.truncate(before=start_date, after=end_date)
st.dataframe(BAS_object.subset_data.describe())


#TIMESERIES LINEPLOTS
st.header('Timeseries Line Plots')
# Create column selection for graphics and summary statistics
show_time_series = st.checkbox("Show time series? Select parameters on Sidebar")
if show_time_series:
    #Prepare Dataframe for plotting
    altair_linechart_data = prepare_BAS_for_altair_chart(BAS_object.subset_data)
    #Create Selection for parameters
    st.sidebar.markdown("# Select BAS Parameters for Time-Series Plotting")
    for col in BAS_object.all_data:
        plot_selection = st.sidebar.checkbox(f'{col}')
# time-series BAS line plot
        if plot_selection:
            st.markdown(f"{col}")
            chart = (
                alt.Chart(altair_linechart_data)
                .mark_line()
                .encode(
                    x=alt.X("Timestamp:T", title="Date & Time"),
                    y=alt.Y(f"{col}:Q", title=f"{col[-4:-1]}"),
                )
                .properties(width=700, height=400)
                .interactive()
            )

            st.altair_chart(chart)



# COMPARISON CHART
st.header('Parameter Comparison Plots')
show_comparison_series = st.checkbox("Show Comparison Plots?")
if show_comparison_series:
    #Prepare Dataframe for plotting
    altair_scatterplot_data = prepare_BAS_for_altair_chart(BAS_object.subset_data)
    #Create Selection for parameters
    st.sidebar.markdown("Select BAS Parameters for Cross Comparison Plotting")
    X_plot_selection = st.selectbox(options=BAS_object.subset_data.columns,
                                    label='Independent Variable')
    Y_plot_selection = st.selectbox(options=BAS_object.subset_data.columns,
                                    label='Dependent Variable')
    #Create Cross-Comarison Chart
    c = alt.Chart(altair_scatterplot_data).mark_circle().encode(
            x=f"{X_plot_selection}", y=f"{Y_plot_selection}")

    st.altair_chart(c, use_container_width=True)



#TODO CREATE CATEGORICAL VARIABLES FOR EXPLORATION
st.header('Categorical Plots')

DLP_var = st.checkbox('Daily Load Profiles?')
if DLP_var:
    #Prepare Dataframe for plotting
    categorical_dataframe = create_categorical_variables(BAS_object.subset_data)
    
    #Create Selection for parameters
    cat_col_select = st.multiselect("Select BAS Parameters for Analysis", 
                                        categorical_dataframe.columns[:-3])
    
    if cat_col_select:
        daily_load_profile = categorical_dataframe.groupby(['DayofWeek','DayHour']).mean().reset_index()
        st.dataframe(daily_load_profile.head())
        sns.lineplot(x=daily_load_profile.DayHour, 
                    y=daily_load_profile[f'{cat_col_select}'],
                    hue=daily_load_profile.DayofWeek)

#TODO CREATE STRIP PLOT WITH HUES of pre/post
day_hour_stripplot = st.checkbox('DayHour Strip Plot?')

#TODO CREATE STRIP PLOT WITH HUES of pre/post
week_hour_scatterplot = st.checkbox('WeekHour Strip Plot?')
if week_hour_scatterplot:
    #Prepare Dataframe for plotting
    categorical_dataframe = create_categorical_variables(BAS_object.subset_data)
    
    #Create Selection for parameters
    cat_col_select = st.multiselect("Select BAS Parameters for Analysis", 
                                        categorical_dataframe.columns[:-3])
    
    for selection in cat_col_select:
        categorical_dataframe.info()
        sns.scatterplot(x=categorical_dataframe.WeekHour, 
                        y=categorical_dataframe[f'{cat_col_select}'])



#Create Cross-Comarison Chart





#TODO CREATE PRE/POST ANALYSIS
# HISTOGRAM W PREPOST
st.header('Histogram Plots | Pre-Post Analysis')
show_histogram_series = st.checkbox("Show Histogram?")
# if show_histogram_series:
    # # #Prepare Dataframe for plotting
    # # pre_post_date = pd.to_datetime(BAS_object.subset_data.index.min())
    # # pre_post_date = st.sidebar.date_input('Enter Date for Pre-Post Analysis:', pd.to_datetime(pre_post_date))
    # # #Create Categorical variable if input is recieved
    # # if pre_post_date:
    # #     altair_histogram_data = BAS_object.subset_data.copy()
    # #     altair_histogram_data['PrePost'] = np.where(pd.to_datetime(altair_histogram_data.index)<pre_post_date, 0, 1)
    # #     altair_histogram_data_prepost = prepare_BAS_for_altair_chart(altair_histogram_data)

    # #     #Create Selection for parameters
    # #     st.sidebar.markdown("Select BAS Parameters for Time-Series Plotting")
    # #     for col in altair_histogram_data_prepost.iloc[:, :-1].iteritems():
    # #         plot_selection = st.sidebar.checkbox(f'{col}')
    # #         # Histogram BAS line plot
    # #         if plot_selection:
    # #             st.markdown(f"Histogram of {col}")
    # #             chart = (
    # #                 alt.Chart(altair_histogram_data_prepost)
    # #                 .mark_line()
    # #                 .encode(
    # #                     x=alt.X("Timestamp:T", title="Date & Time"),
    # #                     y=alt.Y(f"{col}:Q", title=f"{col}"), 
    # #                     color="PrePost"
    # #                 )
    # #                 .properties(width=700, height=400)
    # #                 .interactive()
    # #             )

    # #             st.altair_chart(chart)
    # # else:
    # #Create Selection for parameters
    # st.sidebar.markdown("Select BAS Parameters for Time-Series Plotting")
    # for col in BAS_object.subset_data.iteritems():
    #     plot_selection = st.sidebar.checkbox(f'{col}')
    #     altair_histogram_data = prepare_BAS_for_altair_chart(BAS_object.subset_data)

    #     # Histogram BAS line plot
    #     if plot_selection:
    #         st.markdown(f"Histogram of {col}")
    #         ax = plt.figure(figsize=(6,6))
    #         ax.plt.style.use('fivethirtyeight')
    #         ax.sns.histplot(data=combined_df, x=combined_df['HRCH power kW'], 
    #             hue='HRCH_Mode', bins=20)
    #         ax.plt.xlabel('HRCH Power [kW]')
    #         ax.plt.title('HRCH Energy by Mode')

    #         st.plotly_chart(ax)


