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
            parameters of analysis
            bin size for histograms

        Generate useful & standardized diagnostic plots for report integration
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

Tool Development Next steps: 
    - Create environment.yml file for reproducibility
    - Establish a central repository location for tool development (Atlassian?)
    - Consider evaluating utility of Fisher-Jenks algorithm for peak and base load determination
    - Localhost broadcast over vpn to allow for team usage.
    - Consider packaging into methods for cleaner main script. 

Notes:
    - 

'''
#%%
#Import Modules Required for Applicaiton
from enum import unique
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
import matplotlib as mpl
import matplotlib.pyplot as plt


from src.utils import prepare_BAS_for_altair_chart, create_categorical_variables
from src.transformation.raw_data_processing import BASdata
from src.Chart_functions import get_chart

import plotly.figure_factory as ff

#%% Establish root filepath for reference
ROOT_PATH = os.getcwd()
#Set tool header with image
image = Image.open(os.path.join(ROOT_PATH, "media/BR+A_graphic_3.jpg"))
st.image(image, width=200)
# colors for graphics
color_range_ind = list(sns.color_palette("tab10", n_colors=12).as_hex())
color_range_pairlist = (sns.color_palette("Paired", n_colors=12).as_hex())
hue_range = list(sns.color_palette("flare", n_colors=20).as_hex())
# title
st.title("MB-Comissioning EDA Tool Prototype")

# User input for BAS file directory
input_file = st.file_uploader(
            "Upload BAS data .csv file.", type=["csv"]
            )
if (input_file is not None) and input_file.name.endswith(".csv"):
    df = pd.read_csv(input_file, index_col=0, parse_dates=True).dropna()
    print(df.info())
else:
    st.warning("Dataframe Must be date-time Indexed.")
    st.stop()

# make an instance of the class.
BAS_object = BASdata()

# ingest data into the object.
BAS_object.data_ingest(df)

# set variables with a mix of automated and user inputs.
date_max = BAS_object.all_data.index.max()
date_min = BAS_object.all_data.index.min()
print(f'Minimum Date: {date_min}')
print(f'Maximum Date: {date_max}')

start_date = date_min
#TODO create slider for daterange selection
start_date = st.sidebar.date_input("start date", start_date, date_min, date_max)
end_date = st.sidebar.date_input("end date", date_max, start_date, date_max)

BAS_object.subset_data = BAS_object.all_data.truncate(before=start_date, after=end_date)
st.dataframe(BAS_object.subset_data.describe())

# Create User Input for indicator Column
indicator_param = st.sidebar.radio(
                                    options=BAS_object.subset_data.columns,
                                    label="Select Indicator Parameter"
                                    )

#TIMESERIES LINEPLOTS
st.header('Timeseries Line Plots')
# Create column selection for graphics and summary statistics
show_time_series = st.checkbox("Show time series plots?")
if show_time_series:
    #Prepare Dataframe for plotting
    altair_linechart_data = prepare_BAS_for_altair_chart(BAS_object.subset_data)
    print(altair_linechart_data.info())
    print(altair_linechart_data.head())
    #Create Selection for parameters
    plot_selection = st.multiselect(label='Select Parameter', options=BAS_object.all_data.columns)
    print(plot_selection)
    lineplot_overlay = st.radio("Overlay plots?", options=['No', 'Yes'])
# time-series BAS line plot
    if lineplot_overlay =='No':
    #Column Headers cannot have any special characters: [], %, etc..
        color_index=-1
        for i in plot_selection:
            color_index+=1
            st.markdown(f"{i}")
            #TODO Add hover for mouse with tool tip for interactive chart
            #create individual chart for all parameter selection
            chart = (
                alt.Chart(altair_linechart_data)
                .mark_line(color=color_range_ind[color_index])
                .encode(
                    x=alt.X(f"index:T", title="Date & Time"),
                    y=alt.Y(f"{i}:Q", title=f"{i}"),
                    tooltip=['index', f"{i}"]
                )
                .properties(width=700, height=400)
                .interactive()
                .configure_view(fill='#EEEEEE')
            )

            st.altair_chart(chart)
            st.write(f'Minimum Value of {i}: ', altair_linechart_data[f'{i}'].min())
            st.write(f'Maximum Value of {i}: ', altair_linechart_data[f'{i}'].max())
            st.write(f'Date of Peak Load: ', BAS_object.subset_data[f'{i}'].idxmax())
    else:
        #add index col to plot_selection
        plot_selection = ["index"] + plot_selection
        print('Selected params: ',plot_selection)
        #create chart for all parameter selection
        altair_linechart_data = altair_linechart_data[plot_selection]
        print(altair_linechart_data.head())
        print(altair_linechart_data.info())
        altair_linechart_data_melt = altair_linechart_data.melt("index")
        print("MELT: ", altair_linechart_data_melt.head())
        print("MELT: ", altair_linechart_data_melt.info())
        # TODO handle string "On / Off" parameter. Need to convert to 0 - 100
        # Create a selection that chooses the nearest point & selects based on x-value
        nearest = alt.selection(type='single', nearest=True, on='mouseover',
                                fields=['index'], empty='none')
        
        line = alt.Chart(altair_linechart_data_melt).mark_line().encode(
            x="index:Q",
            y="value:Q",
            color="variable"
        )
        # Transparent selectors across the chart. This is what tells us
        # the x-value of the cursor
        selectors = alt.Chart(altair_linechart_data_melt).mark_point().encode(
                                                                        x='index:Q',
                                                                        opacity=alt.value(0),
                                                                        ).add_selection(nearest)
        # Draw points on the line, and highlight based on selection
        points = line.mark_point().encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))
        # Draw text labels near the points, and highlight based on selection
        text = line.mark_text(align='left', dx=5, dy=-5).encode(text=alt.condition(nearest, 'value:Q', alt.value(' ')))
        # Draw a rule at the location of the selection
        rules = alt.Chart(altair_linechart_data_melt).mark_rule(color='gray').encode(x='index:Q').transform_filter(nearest)
        # Put the five layers into a chart and bind the data
        chart = alt.layer(line, selectors, points, rules, text).interactive().properties(width=800, height=600).configure_view(fill='#EEEEEE')
    

        st.altair_chart(chart)

# COMPARISON CHART
#currently, indicator column is specified as last column of dataframe
st.header('Parameter Comparison Plots')
show_comparison_series = st.checkbox("Show Comparison Plots?")
if show_comparison_series:
    #Prepare Dataframe for plotting
    altair_scatterplot_data = prepare_BAS_for_altair_chart(BAS_object.subset_data)
    #select hue index based on indicator value count for display
    if len(altair_scatterplot_data[f"{indicator_param}"].value_counts() < 5):
        hue_range = [hue_range[0], hue_range[10], hue_range[-1]]
    else:
        pass    
    
    #Create Selection for parameters
    st.sidebar.markdown("Select BAS Parameters for Cross Comparison Plotting")
    col1, col2 = st.columns(2)
    with col1:
        X_plot_selection = st.radio(options=BAS_object.subset_data.columns,
                                    label="Independent Variable")
    with col2:
        Y_plot_selection = st.radio(options=BAS_object.subset_data.columns,
                                    label='Dependent Variable')
    #Create Cross-Comarison Chart
    c = (
        alt.Chart(altair_scatterplot_data)
        .mark_circle()
        .encode(
                x=f"{X_plot_selection}",
                y=f"{Y_plot_selection}",
                color=alt.Color(f'{indicator_param}', scale=alt.Scale(range=hue_range[:])),
                tooltip=['index', f"{X_plot_selection}", f"{Y_plot_selection}", f"{indicator_param}"]
                )
        .properties(width=700, height=400)
        .interactive()
        .configure_view(fill='#EEEEEE')
        )
    st.altair_chart(c, use_container_width=True)

    unique_val_cnt = len(set(altair_scatterplot_data[f'{indicator_param}'])) #too many unique values reduces utility of grouping, unless specifying bin groups
    if unique_val_cnt < 5:
        print('Unique Val Count: ', unique_val_cnt)
        st.write('Statistics of Dataset by Indicator: ', indicator_param)
        st.write(altair_scatterplot_data.groupby(f'{indicator_param}')[[f"{X_plot_selection}", f"{Y_plot_selection}"]].describe())

#TODO CREATE CATEGORICAL VARIABLES FOR EXPLORATION
st.header('Categorical Plots')

WLP_var = st.checkbox('Weekly & Daily Load Profiles?')
if WLP_var:
    #Prepare Dataframe for plotting
    categorical_dataframe = deepcopy(create_categorical_variables(BAS_object.subset_data[0:-6]))
    print(BAS_object.subset_data.info())
    #Create Selection for parameters
    #TODO split into two columns based on length of df to streamline page
    WLP_cat_col_select = st.selectbox(
                            options=BAS_object.subset_data.columns,
                            label="Select BAS Parameters for Analysis"
                            )
                            
#Weekly Load Profile Plot
    if WLP_cat_col_select:
        categorical_dataframe.info()
        fig = plt.figure(figsize=(14,6))
        plt.style.use('bmh') #seaborn-darkgrid, fivethirtyeight
        # plt.title(f'eQuest Modeled and Actual Air-Side System CFM by Week-Hour')
        # plt.suptitle('Tufts Cumming Center')
        # plt.xlabel('Week Hour')
        # plt.ylabel('CFM')
        sns.scatterplot(
                    data=categorical_dataframe,
                    x=categorical_dataframe.WeekHour, 
                    y=categorical_dataframe[f'{WLP_cat_col_select}'],
                    label=f'{WLP_cat_col_select}',
                    alpha=0.6,
                    hue=f'{indicator_param}'
                    )
        plt.legend()
        st.pyplot(fig)

#Daily Load Profile Plot
        fig = plt.figure(figsize=(14,6))
        plt.style.use('bmh') #seaborn-darkgrid, fivethirtyeight
        # plt.title(f'eQuest Modeled and Actual Air-Side System CFM by Week-Hour')
        # plt.suptitle('Tufts Cumming Center')
        # plt.xlabel('Week Hour')
        # plt.ylabel('CFM')
        sns.scatterplot(
                    data=categorical_dataframe,
                    x=categorical_dataframe.DayHour, 
                    y=categorical_dataframe[f'{WLP_cat_col_select}'],
                    label=f'{WLP_cat_col_select}',
                    alpha=0.6,
                    hue=f'{indicator_param}'
                    )
        plt.legend()
        st.pyplot(fig)




# #TODO CREATE HEATMAP
st.header('Heatmap')
htmp_var = st.checkbox('Data Heatmap?')
if htmp_var:
    #Prepare Dataframe for plotting
    heatmap_df = deepcopy(create_categorical_variables(BAS_object.subset_data[0:-6]))
                            
    fig, ax = plt.subplots()
    sns.heatmap(heatmap_df.corr(), ax=ax)
    st.write(fig)


# PRE/POST ANALYSIS
# HISTOGRAM W PREPOST
st.header('Histogram Plots | Pre-Post Analysis')
show_histogram_series = st.checkbox("Show Histogram?")
if show_histogram_series:
#Prepare Dataframe for plotting
    pre_post_date = pd.to_datetime(
                                st.slider(
                                        label='Select Date for Pre-Post Analysis:', 
                                        min_value=start_date,
                                        max_value=end_date
                                        )
                                    )
    #Create Categorical variable if input is recieved
    if pre_post_date:
        altair_histogram_data = deepcopy(BAS_object.subset_data)
        altair_histogram_data['PrePost'] = np.where(altair_histogram_data.index<pre_post_date, 0, 1)

        #Create Selection for parameters
        HIST_cat_col_select = st.selectbox(
                                options=BAS_object.subset_data.columns,
                                label="Select BAS Parameters for Analysis",
                                key = "histogram"
                                )
        altair_histogram_data_melt = pd.melt(altair_histogram_data, id_vars='PrePost', value_vars=f"{HIST_cat_col_select}")
        
        df_mean = altair_histogram_data_melt.value.mean()
        df_std = altair_histogram_data_melt.value.std()
        bin_width = df_mean - df_std
        print('Bin Width: ', bin_width)

        user_bin_width = st.slider(label='Select Histogram Bin-Width:', 
                                    min_value=2,
                                    max_value=round(bin_width)
                                                )
                                            

        # Histogram BAS line plot
        if HIST_cat_col_select:
            hist_chart =( alt.Chart(altair_histogram_data_melt)
                            .mark_bar(opacity=0.6,)
                            .encode(
                                alt.X('value:Q', bin=alt.Bin(step=user_bin_width)),
                                alt.Y('count()', stack=None),
                                alt.Color('PrePost:N')
                                    )
                            .properties(width=700, height=400)
                            .configure_view(fill='#EEEEEE')
                        )
    st.altair_chart(hist_chart, use_container_width=True)
    # print(altair_histogram_data_melt.head())
    # st.caption("Mean Condenser Pressure by Pre/Post Periods: ", altair_histogram_data_melt.groupby("PrePost")['value'].mean())
    

# %%
st.header('Here is my new header')
