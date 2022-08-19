# Comissioning_EDA_Tool_Prototype
BAS data modularized graphical analysis tool.
Lead Engineer Analyst & Developer: Taylor Roth
Co-Developer: Michael Swenson
Date: 6/1/2022
Deliverable: 
    Develop Streamlit Application to ingest a standardized dataframe with Datetime index (and no header for index column) for MB-Commissioning Diagnostic Purposes.
    Modular functionality:
        Column names should reflect the naming convention used in standardized reporting formats
        User input to define:
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

Tool Development Next steps: 
    - Create environment.yml file for reproducibility
    - Establish a central repository location for tool development (Atlassian?)
    - Consider evaluating utility of Fisher-Jenks algorithm for peak and base load determination
    - Localhost broadcast over vpn to allow for team usage.
    - Consider packaging into methods for cleaner main script. 
