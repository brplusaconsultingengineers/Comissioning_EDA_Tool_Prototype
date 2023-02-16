import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

DIR_MAIN = Path(r'C:\Users\TRoth\OneDrive - Bard, Rao + Athanas Consulting Engineers, LLC \Documents\Project Management\Bates')
DIR_GRAPHIC = DIR_MAIN / "Graphics"

def pair_plot(frame, save_filename, save_fig=False):
    g = sns.pairplot(frame, hue="Alarm_Status", palette="tab10")
    for ax in g.axes.flatten():
        # rotate x axis labels
        ax.set_xlabel(ax.get_xlabel(), rotation = 45)
        # rotate y axis labels
        ax.set_ylabel(ax.get_ylabel(), rotation = 45)
        # set y labels alignment
        ax.yaxis.get_label().set_horizontalalignment('right')
    if save_fig ==True:
        plt.savefig(DIR_GRAPHIC / f'{save_filename}_Pair_Plot.pdf')

def line_plot(frame):
    num_cols = len(frame.columns)
    plot_color_list = sns.color_palette(palette='Set2', n_colors=num_cols,\
                         desat=None, as_cmap=False)

    list = np.arange(0, num_cols-1, 1)

    for num in list:
        BAS_point = str(frame.columns[num][0:27])
        
        plt.style.use('bmh') #seaborn-darkgrid, fivethirtyeight
        plt.figure(figsize=(10,6))
        plt.title(f"Scatter Plot of {BAS_point} by Alarm Type")
        plt.ylabel(f'{BAS_point[-3:0]}')
        plt.xlabel('DateTime Index')
        # markers_on = frame.loc[frame.iloc[:,-1] != "No Alarm"]
        # sns.lineplot(x=frame.index, y=frame.iloc[:,num],
        #             markers='o', markevery=markers_on)
        
        # plt.xticks(rotation=45)

        plt.show()  

def hued_scatterplot(frame, save_filename='', save_fig=False):
    """Produces Datetime Lineplot of Outdoor Air Flows and Discharge Air Flows.


    Args:
        frame (pandas dataframe): frame must have datatime index, and features
        of outdoor air flow, discharge air flow (or supply air flow) in columns
        0 and 1.
    """
    num_cols = len(frame.columns)
    plot_color_list = sns.color_palette(palette='Set2', n_colors=num_cols,\
                         desat=None, as_cmap=False)

    list = np.arange(0, num_cols-1, 1)

    for num in list:
        BAS_point = str(frame.columns[num][0:27])
        
        plt.style.use('bmh') #seaborn-darkgrid, fivethirtyeight
        plt.figure(figsize=(10,6))
        plt.title(f"Scatter Plot of {BAS_point} by Alarm Type")
        plt.ylabel(f'{BAS_point[-3:0]}')
        plt.xlabel('DateTime Index')

        sns.scatterplot(x=frame.index, y=frame.iloc[:,num],
                    color=plot_color_list[num], hue=frame.iloc[:,-1])
        plt.xticks(rotation=45)
        if save_fig ==True:
            plt.savefig(DIR_GRAPHIC / f'{BAS_point}_{save_filename}_scatterplot.pdf')

        plt.show()


def DayHour_WeekHour_strip_plot(frame):
    """Produces Datetime stripplot of Outdoor Air Flows and Discharge Air Flows
    relative to Dayhour or Weekhour.


    Args:
        frame (pandas dataframe): frame must have datatime index, and features
        of outdoor air flow, discharge air flow (or supply air flow) in columns
        0 and 1.

        hourtype (str): string must be either "DayHour" or "WeekHour". Used to index
        into columns for X-axis assignment.
    """
    equipment_name = str(frame.columns[0][0:11])
    frame = frame.resample('h').mean()
    frame['DayHour'] = frame.index.hour
    frame_melt = frame.iloc[:,[0,1,3]].melt(id_vars=["DayHour"])

    plt.figure(figsize=(12,6))
    plt.style.use('bmh') #seaborn-darkgrid, fivethirtyeight
    plt.title(f"{equipment_name}")
    plt.suptitle('Outdoor Air Flow and Discharge Air Flow')
    plt.xlabel('Day Hour')
    plt.ylabel('Flow [CFM]')

    sns.stripplot(x=frame_melt['DayHour'], y=frame_melt.value,
                    data=frame_melt, hue=frame_melt.variable)
    plt.legend()
    plt.show()

def ECDF_plot(frame):
    """Creates ECDF plot for all columns in one plot. Columns must have 
        the same datatype.

    Args:
        frame (pandas dataframe): frame must have float or int values.
    """
    plt.style.use("fivethirtyeight")
    num_cols = len(frame.columns)
    list = np.arange(0, num_cols, 1)
    plt.figure(figsize=(14,8))
    plt.title("ECDF Plot of Outdoor Air Percentages")
    plt.xlabel("Outdoor Air Percentage [OA-F / DA-F] %")
    for num in list:
            sns.ecdfplot(frame.iloc[:,num], label=frame.columns[num][0:11])
    plt.legend()
    plt.show()

def KDE_plot(frame, save_filename='', save_fig=False):
    
    num_cols = len(frame.columns)
    plot_color_list = sns.color_palette(palette='Set2', n_colors=num_cols,\
                         desat=None, as_cmap=False)

    list = np.arange(0, num_cols-1, 1)

    for num in list:
        BAS_point = str(frame.columns[num][0:27])
        
        plt.style.use('bmh') #seaborn-darkgrid, fivethirtyeight
        plt.figure(figsize=(10,6))
        plt.title(f"KDE Plot of {BAS_point} by Alarm Type")
        plt.xlabel(f'{BAS_point[-3:0]}')
        plt.ylabel('Proportional Count')

        sns.kdeplot(x=frame.iloc[:,num],
                    # label=frame.iloc[-1], 
                    color=plot_color_list[num], hue=frame.iloc[:,-1],
                    fill=False)
        # plt.legend()
        if save_fig ==True:
            plt.savefig(DIR_GRAPHIC / f'{BAS_point}_{save_filename}_KDEplot.pdf')

        plt.show()



