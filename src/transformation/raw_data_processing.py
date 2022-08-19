'''
Project Lead Engineer: Michael Swenson
Assistant Engineer: Taylor Roth
Date: 5/4/2022
Deliverable:
    Analyze RFGRNT of HRCH system trend points to correlate HRCH alarm status.
'''
#Import modules
from msilib.schema import Class
import os
from pathlib import Path
import pandas as pd
import numpy as np
import seaborn as sns
import datetime
from datetime import datetime
# from pandas_profiling import ProfileReport
import glob

class BASdata:
    """Ingests BAS data set. Also contains some general utilities and features for
    the class.

    Class Attributes
    ----------------
    all_data -- pandas dataframe with all rows of data
    subset_data -- pandas dataframe truncated to includes selected date range
    ratchet_power -- the highest power reading used to estimate the power ratchet
    pctiles -- for the subset, a pctile (percentile) is a daily loadshape that corresponds to some \
    percentile usage for each time interval.
    """

    def __init__(self):
        self.all_data = None
        self.subset_data = None


    def open_BAS_file(self, filepath):
        """Open CSV file with BAS data.."""
        if filepath:
            self.all_data = pd.read_csv(
                filepath,
                parse_dates=True,
                index_col=0,
                header=0,
            )

            self.all_data.sort_index(inplace=True)

            # BAS_data_list = []
            # BAS_filepaths = glob.glob(os.path.join(BASdata, "*.csv"))
            # for filename in BAS_filepaths:
            #     self.all_data = pd.read_csv(filename, index_col=0, header=0, parse_dates=True)
            #     self.all_data = self.all_data.loc[~df.index.duplicated(keep='first')] #remove rows with duplicated indices
            #     BAS_data_list.append(self.all_data)    

            # frame_out = pd.concat(BAS_data_list, axis=1, join='outer', ignore_index=False)
            # frame_out_cleaned = frame_out.resample('15T').max() #might be changed depending on datastructure

    def data_ingest(self, dataframe):
        """Ingests BAS data from existing dataframe with datetimeindex"""
        if dataframe.any().any():
            self.all_data = dataframe
            self.all_data.sort_index(inplace=True)
            self.all_data = self.all_data.loc[self.all_data.index.dropna()].copy()
            self.all_data.dropna(inplace=True)

    def BAS_truncate(self, dates):
        """Truncate BAS file to start and end dates"""
        self.truncate_data = self.all_data.truncate(before=dates[0], after=dates[1])
        self.subset_data = self.truncate_data.copy()

    def set_subset(self):
        """In case you don't truncate, set subset with this method.

        :return:
        """
        self.subset_data = self.all_data.copy()

    def reset_subset(self, truncated=True):
        if truncated:
            self.subset_data = self.truncate_data.copy()
        else:
            self.subset_data = self.all_data.copy()
    
    def localize(self):
        """
        simply helps the ami object play better with streamlit graphing

        :return: localized dataframe
        """
        self.subset_data.index = self.subset_data.index.tz_localize(
            tz="US/Eastern", ambiguous="NaT", nonexistent="NaT"
        ).floor("15min")




