import pandas as pd
import numpy as np


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
        self.ratchet_power = None
        self.pctiles = None

    def open_BAS_file(self, filepath):
        """Open CSV file with BAS data. Dependent upon AMIDEX format."""
        if filepath:
            self.all_data = pd.read_csv(
                filepath,
                parse_dates=True,
                index_col=0,
                header=0,
            )

            self.all_data.sort_index(inplace=True)

    def data_ingest(self, dataframe):
        """Ingests BAS data from existing dataframe with datetimeindex"""
        if dataframe.any().any():
            self.all_data = dataframe
            self.all_data.sort_index(inplace=True)
            self.all_data = self.all_data.loc[self.all_data.index.dropna()].copy()

    def BAS_truncate(self, dates):
        """Truncate BAS file to start and end dates"""
        self.truncate_data = self.all_data.truncate(before=dates[0], after=dates[1])
        self.subset_data = self.truncate_data.copy()
        self.ratchet_power = np.max(self.truncate_data.power)

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