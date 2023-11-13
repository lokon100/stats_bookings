# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 14:05:48 2022

@author: Skye
"""

# %% importing
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.dates import MonthLocator, DateFormatter, DayLocator
import numpy as np
import pandas as pd
import warnings
import math
import calplot
import seaborn as sn

import variable_work as vw
from variable_work import bookings, week_names, weekday, weekend, studio_name, studio_type, sources  # analysis:ignore

from filtering import filter_stats_data, source_list, studio_list, day_list

import stats_question_mark as sqm
import config as cg

warnings.simplefilter('ignore', FutureWarning)
mpl.rcParams['figure.dpi'] = 600


# %% functions

def what_used():
    string = ""
    if cg.filter_on == False:
        return string
    string = string + ("Sans:")
    if cg.atlantic == True:
        string = string + (" Atlantic")
    if cg.pit == True:
        string = string + (" Pit")
    if cg.full_day == True:
        string = string + (" Full Day Bookings")
    if vw.use_advance_low == True:
        string = string + (" " + str(cg.days_advance_low) + " in advance")
    if vw.use_advance_high == True:
        string = string + (" " + str(cg.days_advance_high) + " in advance")
    if cg.use_date == True:
        string = string + \
            (" between " + str(cg.date_range[0]) + " and " + str(cg.date_range[1]))
    return string


def calc_bins_ticks(column, step):
    hmin = int(column.min())
    hmax = int(column.max())
    bins1 = [x * step for x in range(hmin, ((hmax*2)+1))][1:]
    ticks1 = [x for x in range(hmin, hmax+1)]
    return bins1, ticks1


def filter_thing(df, filter_list, col):
    keep_list = []
    for i in filter_list:
        keep_list.extend(df.index[df[col] == i].tolist())
    df = df.loc[keep_list]
    return df


def find_count_hours(df, query, col):
    keep_list = []
    for i in query:
        keep_list.extend(df.index[df[col] == i].tolist())
    df = df.loc[keep_list]
    x = df[['Source', 'Hours']]
    x = x.groupby('Source').agg(['sum']).droplevel(0, axis=1)
    return x


def get_perc(x):
    porcent = 100.*x/x.sum()
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(x.index, porcent)][:5]
    return labels

def filter_activities(df):
    df['Activity'] = df['Activity'].str.lower()
    df = df[df['Activity'].notna()]
    for i in activities.columns:
        filter_list = activities[i].dropna()[1:].tolist()
        mask = df['Activity'].apply(lambda x: any(item for item in filter_list if item in x))
        change_list = df[mask].index.tolist()
        df.loc[change_list, 'Activity'] = i
    df = df[df['Activity'].isin(activities.columns)]
    return df


def attendees_activities_var(df):
    df = df[['# of Attendees', 'Activity']]
    df = df[df['# of Attendees'].notna()]
    df = df[df['Activity'].notna()]
    df = filter_activities(df)
    return df


def duration_activities_var(df):
    df = df[['Hours', 'Activity']]
    df = df[df['Hours'].notna()]
    df = df[df['Activity'].notna()]
    df = filter_activities(df)
    duration_df = pd.DataFrame()
    for i in activities.columns:
        temp = df[df['Activity']==i]['Hours']
        duration_df = pd.concat([duration_df.reset_index(drop=True), temp.reset_index(drop=True)], axis=1)
    duration_df.columns = activities.columns
    return df


def bookings_activities_var(df):
    df = df[['Date of Activity', 'Activity']]
    df = df[df['Date of Activity'].notna()]
    df = df[df['Activity'].notna()]
    df = filter_activities(df)
    df.index = pd.to_datetime(df['Date of Activity'])
    df = df['Activity']
    temp = df.resample('W').sum().index
    activities_df = pd.DataFrame(columns=activities.columns, index=temp)
    for i in activities.columns:
        temp = df[df==i]
        activities_df[i] = temp.resample('W').count()
    activities_df = activities_df.fillna(0)
    temp = activities_df.max().sort_values(ascending=False).index.tolist()
    activities_df = activities_df[temp]
    return activities_df

def making_studio_graphs(df):
    df_studio = df[['Studio', 'Hours']]
    df_studio = df_studio[df_studio['Studio'].notna()]
    df_studio = df_studio[df_studio['Hours'].notna()]
    hours = sorted(df_studio.Hours.dropna().unique().tolist())
    studio_df = pd.DataFrame(index=hours, columns=studio_name)
    for i in studio_name:
        studio = df_studio[df_studio['Studio'] == i]
        studio = studio['Hours']
        studio = studio.value_counts().sort_index()
        studio_df[i] = studio
    studio_df = studio_df.fillna(0)
    studio_df = studio_df.T
    return studio_df


def making_time_graphs(df, frame):
    hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    df = df.copy()
    weeks = pd.date_range(df['Date of Activity'].min(), df['Date of Activity'].max(), freq='W-MON').strftime('%m/%d/%Y').tolist()
    df['Date of Activity'] = pd.to_datetime(df['Date of Activity'])
    if frame == 'D':
        labels = week_names
        dates = pd.DataFrame(index=hours, columns=week_names, dtype=float)
        for i in range(len(week_names)):
            x = df[df['Date of Activity'].dt.dayofweek == i]
            if len(x) != 0:
                x = x.apply(lambda x: pd.date_range(x['Start Time'], x['End Time'], freq='H'), axis=1).explode().dt.hour.value_counts().reindex(np.arange(0,24), fill_value=0)
            dates.iloc[:, i] = x
    if frame == 'W':
        labels = weeks
        dates = pd.DataFrame(index=hours, columns=weeks, dtype=float)
        for i in range(len(weeks)):
            if i < len(weeks)-1:
                mask = (df['Date of Activity'] > weeks[i]) & (df['Date of Activity'] <= weeks[i+1])
                x = df.loc[mask]
            else: x = pd.DataFrame()
            if len(x) != 0:
                x = x.apply(lambda x: pd.date_range(x['Start Time'], x['End Time'], freq='H'), axis=1).explode().dt.hour.value_counts().reindex(np.arange(0,24), fill_value=0)
                dates.loc[:, weeks[i]] = x
    if frame == 'M':
        labels = months
        dates = pd.DataFrame(index=hours, columns=months, dtype=float)
        for i in months:
            x = df[df['Date of Activity'].dt.month_name() == i]
            if len(x) != 0:
                    x = x.apply(lambda x: pd.date_range(x['Start Time'], x['End Time'], freq='H'), axis=1).explode().dt.hour.value_counts().reindex(np.arange(0,24), fill_value=0)
            dates.loc[:, i] = x
    dates = dates.T
    opposite = dates.iloc[::-1]
    temp = []
    for index, row in opposite.iterrows():
        if (row == 0).all():
            temp.append(index)
    temp_start = [i for i in temp if i < pd.Timestamp(2023, 1, 1)]
    if temp_start == []: temp_start.append(dates.index[0])
    start = dates.index.get_loc(temp_start[0])
    temp_end = [i for i in temp if i > pd.Timestamp(2023, 1, 1)]
    if temp_end == []: temp_end.append(dates.index[-1])
    end = dates.index.get_loc(temp_end[len(temp_end)-1])
    dates = dates.iloc[start:end, :]
    return dates, labels


def make_date_booked(df, source):
    df = df[df['Date Booked'].notna()]
    df = df.sort_values(by='Date Booked', ascending=True).reset_index()
    df.index = df['Date Booked']
    weeks = df.resample('W').count().index
    if source == True:
        source_df = pd.DataFrame(columns=source_list, index=weeks)
        for i in source_list:
            temp_df = df[df['Source'] == i]
            x = temp_df['Date Booked'].resample('W').count()
            source_df[i] = x
        x = source_df.copy()
    if source == False:
        x = pd.DataFrame()
        temp = df['Date Booked'].resample('W').count()
        x.index = temp.index
        x['Count'] = temp
    x = x.fillna(0)
    x.index = pd.to_datetime(x.index)
    opposite = x.iloc[::-1]
    temp = []
    for index, row in opposite.iterrows():
        if (row == 0).all():
            temp.append(index)
    temp_start = [i for i in temp if i < pd.Timestamp(2023, 1, 1)]
    if temp_start == []: temp_start.append(x.index[0])
    start = x.index.get_loc(temp_start[0])
    temp_end = [i for i in temp if i > pd.Timestamp(2023, 1, 1)]
    if temp_end == []: temp_end.append(x.index[-1])
    end = x.index.get_loc(temp_end[len(temp_end)-1])
    x = x.iloc[start:end, :]
    return x

def make_date_booking(df, source):
    df = df[df['Date of Activity'].notna()]
    df.index = df['Date of Activity']
    weeks = df.resample('W').count().index
    if source == True:
        source_df = pd.DataFrame(columns=source_list, index=weeks)
        for i in source_list:
            temp_df = df[df['Source'] == i]
            x = temp_df['Date of Activity'].resample('W').count()
            source_df[i] = x
        x = source_df.copy()
    if source == False:
        x = pd.DataFrame()
        temp = df['Date of Activity'].resample('W').count()
        x.index = temp.index
        x['Count'] = temp
    x = x.fillna(0)
    x.index = pd.to_datetime(x.index)
    opposite = x.iloc[::-1]
    temp = []
    for index, row in opposite.iterrows():
        if (row == 0).all():
            temp.append(index)
    temp_start = [i for i in temp if i < pd.Timestamp(2023, 1, 1)]
    if temp_start == []: temp_start.append(x.index[0])
    start = x.index.get_loc(temp_start[0])
    temp_end = [i for i in temp if i > pd.Timestamp(2023, 1, 1)]
    if temp_end == []: temp_end.append(x.index[-1])
    end = x.index.get_loc(temp_end[len(temp_end)-1])
    x = x.iloc[start:end, :]
    return x

def choose_subplot_dimensions(k):
    if k < 4:
        return k, 1
    elif k < 11:
        return math.ceil(k/2), 2
    else:
        # I've chosen to have a maximum of 3 columns
        return math.ceil(k/3), 3


def generate_subplots(k, size, sharey, row_wise=False):
    nrow, ncol = choose_subplot_dimensions(k)
    # Choose your share X and share Y parameters as you wish:
    figure, axes = plt.subplots(nrow, ncol, layout="constrained", figsize=size, dpi=600, sharex='col', sharey=sharey)
    if not isinstance(axes, np.ndarray):
        return figure, [axes]
    else:
        # Choose the traversal you'd like: 'F' is col-wise, 'C' is row-wise
        axes = axes.flatten(order=('C' if row_wise else 'F'))
        for idx, ax in enumerate(axes[k:]):
            figure.delaxes(ax)
            # Turn ticks on for the last ax in each column, wherever it lands
            idx_to_turn_on_ticks = idx + k - ncol if row_wise else idx + k - 1
            for tk in axes[idx_to_turn_on_ticks].get_xticklabels():
                tk.set_visible(True)
        axes = axes[:k]
        return figure, axes

def hours_heat_maker(df, step):
    hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    duration = np.arange(1, 15, step)
    dates = pd.DataFrame(index=hours, columns=duration, dtype=float)
    for i in duration:
        x = df[df['Hours'] == i]
        if len(x) != 0:
            x = x.apply(lambda x: pd.date_range(x['Start Time'], x['End Time'], freq='H'), axis=1).explode().dt.hour.value_counts().reindex(np.arange(0,24), fill_value=0)
            dates.loc[:, i] = x
        if len(x) == 0:
            x = [0] * len(hours)
            dates.loc[:, i] = x
    dates = dates.T
    return dates, duration



# %% graphs

# %%% attendees

def sub_hist_attendees_studio(df, use):
    if use == False:
        return
    bins1 = [x * 5 for x in range(int(df['# of Attendees'].max()/5)+2)]
    fig, axs = generate_subplots(len(studio_list), (10,10), True, row_wise=True)
    fig.suptitle("Subplot Hist of Attendees Per Studio")
    i = 0
    for ax in axs.flat:
        x = df.index[df['Studio']==studio_list[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['# of Attendees'].dropna(), bins=bins1)
        ax.set_title(studio_list[i])
        ax.label_outer()
        i += 1
    fig.supxlabel('Attendees')
    fig.supylabel('Count')
    plt.savefig('filename.png')


def sub_hist_attendees_activities(df, use):
    if use == False:
        return
    df = attendees_activities_var(df)
    x = df.groupby('Activity')['# of Attendees'].agg(['count']).sort_values(by='count', ascending=False)
    x = x.index.to_list()
    activities_sorted = activities[x]
    bins1 = [x * 2 for x in range(0, 25)][1:]
    ticks1 = [x*10 for x in range(0, 6)]
    fig, axs = generate_subplots(len(activities.columns), (5.5, 5.5), 'row', row_wise=True)
    i = 0
    for ax in axs.flat:
        ax.label_outer()
        x = df.index[df['Activity'] == activities_sorted.columns[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['# of Attendees'], bins=bins1)
        ax.set_title(activities_sorted.columns[i])
        ax.set_xticks(ticks1)
        i += 1
    fig.supxlabel('Attendees')
    fig.supylabel('Count')
    fig.suptitle("Subplot Hist of Attendees Per Studio")
    plt.savefig('filename.png')

    fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(5.5, 3.5), dpi=600, sharex=True, sharey='row')
    fig.suptitle("Subplot Hist of Attendees Per Studio (Top 3 Uses)")
    i = 0
    for ax in axs.flat:
        x = df.index[df['Activity'] == activities_sorted.columns[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['# of Attendees'], bins=bins1)
        ax.set_title(activities_sorted.columns[i])
        ax.set_xticks(ticks1)
        i += 1
    fig.supxlabel('Attendees')
    fig.supylabel('Count')
    plt.savefig('filename.png')
    fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(5.5, 3.5), dpi=600, sharex=True, sharey='row')
    fig.suptitle("Subplot Hist of Attendees Per Studio (Lesser 3 Uses)")
    for ax in axs.flat:
        x = df.index[df['Activity'] == activities_sorted.columns[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['# of Attendees'], bins=bins1)
        ax.set_title(activities_sorted.columns[i])
        ax.set_xticks(ticks1)
        i += 1
    fig.supxlabel('Attendees')
    fig.supylabel('Count')
    plt.savefig('filename.png')


def overall_activities_attendees_pie(df, use):
    if use == False:
        return
    df = attendees_activities_var(df)
    x = df.groupby('Activity')['# of Attendees'].agg(['sum']).sort_values(by='sum', ascending=False)
    porcent = 100.*x['sum']/x['sum'].sum()
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(x.index, porcent)]
    plt.figure(dpi = 600)
    plt.pie(x['sum'], wedgeprops={"edgecolor":"k",'linewidth': 0.5})
    plt.axis('equal')
    plt.legend(labels, bbox_to_anchor=(0.85,1.025), loc="upper left")
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75)
    plt.title("Activities by Attendees Breakdown")
    plt.savefig('filename.png')


# %%% pie graphs

def pie_sources_bookings(df, use):
    if use == False:
        return
    sc = sources_count.copy()
    sc.index = ['count']
    sc = sc.sort_values(by='count', axis=1, ascending=False)
    porcent = 100.*sc.loc['count']/sc.loc['count'].sum()
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(sc.columns, porcent)]
    plt.figure(dpi = 600)
    plt.pie(sc.loc['count'], wedgeprops={"edgecolor":"k",'linewidth': 0.5})
    plt.axis('equal')
    plt.legend(labels, bbox_to_anchor=(0.85,1.025), loc="upper left")
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75)
    plt.title("Sources by Bookings Breakdown")
    plt.savefig('filename.png')


def pie_sources_bookings_sans_direct(df, use):
    if use == False:
        return
    sc = sqm.sources_count.copy()
    sc = sc[['Peerspace', 'Skedda', 'Walk-In', 'Splacer', 'Giggster', 'Liquidspace', 'Spacebase', 'Tagvenue']]
    sc.index = ['count']
    sc = sc.sort_values(by='count', axis=1, ascending=False)
    porcent = 100.*sc.loc['count']/sc.loc['count'].sum()
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(sc.columns, porcent)]
    plt.figure(dpi = 600)
    plt.pie(sc.loc['count'], wedgeprops={"edgecolor":"k",'linewidth': 0.5})
    plt.axis('equal')
    plt.legend(labels, bbox_to_anchor=(0.85,1.025), loc="upper left")
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75)
    plt.title("Sources by Bookings Breakdown Without Direct")
    plt.savefig('filename.png')


def pie_sources_hours(df, use):
    if use == False:
        return
    x = find_count_hours(df, sources_count.columns, 'Source')
    x = x.sort_values(by='sum', ascending=False)
    porcent = 100.*x['sum']/x['sum'].sum()
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(x.index, porcent)]
    plt.figure(dpi = 600)
    plt.pie(x['sum'], wedgeprops={"edgecolor":"k",'linewidth': 0.5})
    plt.axis('equal')
    plt.legend(labels, bbox_to_anchor=(0.85,1.025), loc="upper left")
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75)
    plt.title("Sources by Hours Breakdown")
    plt.savefig('filename.png')


def pie_sources_hours_sans_direct(df, use):
    if use == False:
        return
    sources_sans = ['Peerspace', 'Skedda', 'Walk-In', 'Splacer', 'Giggster', 'Liquidspace', 'Spacebase', 'Tagvenue']
    x = find_count_hours(df, sources_sans, 'Source')
    x = x.sort_values(by='sum', ascending=False)
    porcent = 100.*x['sum']/x['sum'].sum()
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(x.index, porcent)]
    plt.figure(dpi = 600)
    plt.pie(x['sum'], wedgeprops={"edgecolor":"k",'linewidth': 0.5})
    plt.axis('equal')
    plt.legend(labels, bbox_to_anchor=(0.85,1.025), loc="upper left")
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75)
    plt.title("Sources by Hours Breakdown Without Direct")
    plt.savefig('filename.png')


def sub_pie_duration_activities(df, use):
    if use == False:
        return
    df = duration_activities_var(df)
    fig, axs = plt.subplots(2, 3, layout="constrained", figsize=(15, 10), dpi=600)
    fig.suptitle("Subplot Pie of Hours Per Activity Type", size = 20)
    i = 0
    for ax in axs.flat:
        x = filter_thing(df, [activities.columns[i]], 'Activity')
        x = x.value_counts()
        x = x.droplevel('Activity')
        ax.pie(x, wedgeprops={"edgecolor":"k",'linewidth': 0.5}, labels=None)
        ax.legend(labels=get_perc(x))
        ax.set_title(activities.columns[i])
        i += 1
    plt.savefig('filename.png')


def pie_activities_bookings(df, use):
    if use == False:
        return
    ac = activities.copy()
    ac = ac.iloc[0]
    ac = ac.sort_values(ascending=False)
    porcent = 100.*ac/ac.sum()
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(ac.index, porcent)]
    plt.figure(dpi = 600)
    plt.pie(ac, wedgeprops={"edgecolor":"k",'linewidth': 0.5})
    plt.axis('equal')
    plt.legend(labels, bbox_to_anchor=(0.85,1.025), loc="upper left")
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75)
    plt.title("Bookings by Activities Breakdown")
    plt.savefig('filename.png')


def sub_pie_attendees_activities(df, use):
    if use == False:
        return
    df = attendees_activities_var(df)
    fig, axs = plt.subplots(2, 3, layout="constrained", figsize=(15, 10), dpi=600)
    fig.suptitle("Subplot Pie of Attendees Per Activity Type", size = 20)
    i = 0
    for ax in axs.flat:
        x = filter_thing(df, [activities.columns[i]], 'Activity')
        x = x.value_counts()
        x = x.droplevel('Activity')
        ax.pie(x, wedgeprops={"edgecolor":"k",'linewidth': 0.5}, labels=None)
        ax.legend(labels=get_perc(x))
        ax.set_title(activities.columns[i])
        i += 1
    plt.savefig('filename.png')


# %%% duration

def hist_dur_studio(df, use):
    if use == False:
        return
    bins1, ticks1 = calc_bins_ticks(df['Hours'], 0.5)
    plt.figure(dpi = 600)
    plt.xticks(ticks1)
    for i in studio_list:
        x = df.index[df['Studio'] == i].tolist()
        y = df[df.index.isin(x)]
        plt.hist(y['Hours'].dropna(), alpha=0.5, label=i, bins=bins1)
    plt.ylim(0, 101)
    plt.xlabel("Hours", size=14)
    plt.ylabel("Count", size=14)
    plt.title("Histogram of Hours Per Studio")
    plt.legend(loc='best')
    plt.savefig('filename.png')


def sub_hist_dur_studio(df, use):
    if use == False:
        return
    bins1, ticks1 = calc_bins_ticks(df['Hours'], 0.5)
    fig, axs = plt.subplots(3, 4, sharey='row', sharex=True, layout='constrained', figsize=(15,11.25))
    i = 0
    for ax in axs.flat:
        x = df.index[df['Studio'] == studio_name[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['Hours'].dropna(), bins=bins1)
        ax.set_xticks(ticks1)
        ax.set_title(studio_name[i])
        i += 1
    fig.supxlabel('Hours', size=14)
    fig.supylabel('Count', size=14)
    fig.suptitle("Subplot Hist Duration Per Studio", size=20)
    plt.savefig('filename.png')


def sub_hist_dur_studio_type(df, use):
    if use == False:
        return
    bins1, ticks1 = calc_bins_ticks(df['Hours'], 0.5)
    fig, axs = plt.subplots(2, 2, sharex=True, layout='constrained', figsize=(7.5, 7.5))
    i = 0
    for ax in axs.flat:
        x = df.index[df['Type'] == studio_type[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['Hours'].dropna(), bins=bins1)
        ax.set_xticks(ticks1)
        ax.set_title("Studio Type: " + str(studio_type[i]))
        i += 1
    fig.supxlabel('Hours', size=14)
    fig.supylabel('Count', size=14)
    fig.suptitle("Subplot Hist Duration Per Studio Tyoe", size=20)
    plt.savefig('filename.png')


def hist_average_dur_studio(df, use):
    if use == False:
        return
    bins1 = [x * 0.5 for x in range(0, ((10*2)+1))][1:]
    ticks1 = [x for x in range(0, 10+1)]
    plt.figure(dpi = 600)
    plt.xticks(ticks1)
    for i in studio_list:
        x = df[df['Studio'] == i]
        y = sqm.average_per_day(x, False)
        y = y['HMean']
        y.plot(kind='hist', alpha=0.5, label=i, bins=bins1)
    plt.xlabel("Hours", size=14)
    plt.ylabel("Count", size=14)
    plt.legend(loc='upper right')
    plt.title("Histogram of Hours Per Studio")
    plt.savefig('filename.png')


def sub_hist_duration_activities(df, use):
    if use == False:
        return
    df = duration_activities_var(df)
    bins1 = [x * 1 for x in range(0, 15)][1:]
    ticks1 = [x*2 for x in range(0, 8)]
    activities_df = activities.sort_values(by=activities.index[0], ascending=False, axis=1)
    fig, axs = generate_subplots(len(activities.columns), (4, 5.5), True, row_wise=True)
    fig.suptitle("Subplot Hist of Duration Per Activity Type")
    i = 0
    for ax in axs.flat:
        x = df.index[df['Activity'] == activities_df.columns[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['Hours'], bins=bins1)
        ax.set_title(activities_df.columns[i])
        ax.set_xticks(ticks1)
        i += 1
    fig.supxlabel('Hours')
    fig.supylabel('Count')
    plt.savefig('filename.png')

    fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(5.5, 3.5), dpi=600, sharex=True, sharey='row')
    fig.suptitle("Subplot Hist of Duration Per Activity Type (Top 3 Uses)")
    i = 0
    for ax in axs.flat:
        x = df.index[df['Activity'] == activities_df.columns[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['Hours'], bins=bins1)
        ax.set_title(activities_df.columns[i])
        ax.set_xticks(ticks1)
        i += 1
    fig.supxlabel('Hours')
    fig.supylabel('Count')
    plt.savefig('filename.png')
    fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(5.5, 3.5), dpi=600, sharex=True, sharey='row')
    fig.suptitle("Subplot Hist of Duration Per Activity Type (Lesser 3 Uses)")
    for ax in axs.flat:
        x = df.index[df['Activity'] == activities_df.columns[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['Hours'], bins=bins1)
        ax.set_title(activities_df.columns[i])
        ax.set_xticks(ticks1)
        i += 1
    fig.supxlabel('Hours')
    fig.supylabel('Count')
    plt.savefig('filename.png')


def overall_activities_duration_pie(df, use):
    if use == False:
        return
    df = duration_activities_var(df)
    x = df.groupby('Activity')['Hours'].agg(['sum'])
    x = x.sort_values(by='sum', ascending=False)
    porcent = 100.*x['sum']/x['sum'].sum()
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(x.index, porcent)]
    plt.figure(dpi = 600)
    plt.pie(x['sum'], wedgeprops={"edgecolor":"k",'linewidth': 0.5})
    plt.axis('equal')
    plt.legend(labels, bbox_to_anchor=(0.85,1.025), loc="upper left")
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75)
    plt.title("Activities by Hours Breakdown")
    plt.savefig('filename.png')


# %%% num bookings/made bookings


def bar_bookings_day(df, use):
    if use == False:
        return
    plt.figure(dpi = 600)
    temp = sqm.average_count_per_day(df)
    for i in temp.index:
        plt.bar(i, temp.loc[i])
    plt.xlabel("Day", size=14)
    plt.xticks(rotation=20)
    plt.ylabel("Count", size=14)
    plt.title("Bar of Average Number of Bookings Per Day")
    plt.savefig('filename.png')


def bookings_made_monthly(df, use):
    if use == False:
        return
    x = make_date_booked(df, False)
    start = pd.to_datetime(x.index[0])
    end = pd.to_datetime(x.index[-1])
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Made Over Time")
    ax.plot(x)
    ax.set(xlabel='Date', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(MonthLocator(interval=1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim([start,end])
    plt.savefig('filename.png', dpi=600)


def bookings_made_sources_monthly(df, use):
    if use == False:
        return
    x = make_date_booked(df, True)
    start = pd.to_datetime(x.index[0])
    end = pd.to_datetime(x.index[-1])
    x.index = pd.to_datetime(x.index)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Made Over Time By Source")
    ax.plot(x)
    ax.set(xlabel='Date', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(MonthLocator(interval=1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim([start,end])
    ax.legend(labels=x.columns)


def bookings_monthly(df, use):
    if use == False:
        return
    x = make_date_booking(df, False)
    start = pd.to_datetime(x.index[0])
    end = pd.to_datetime(x.index[-1])
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Over Time")
    ax.plot(x)
    ax.set(xlabel='Date (months)', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(MonthLocator(interval=1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim([start,end])
    plt.savefig('filename.png', dpi=600)


def bookings_sources_monthly(df, use):
    if use == False:
        return
    x = make_date_booking(df, True)
    start = pd.to_datetime(x.index[0])
    end = pd.to_datetime(x.index[-1])
    x.index = pd.to_datetime(x.index)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Over Time By Source")
    ax.plot(x)
    ax.set(xlabel='Date (months)', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(MonthLocator(interval=1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim([start,end])
    ax.legend(labels=x.columns)


def sub_bookings_by_source_monthly(df, use):
    if use == False:
        return
    source = make_date_booking(df, True)
    start = pd.to_datetime(source.index[0])
    end = pd.to_datetime(source.index[-1])
    date_form = DateFormatter("%m-%y")
    fig, axs = generate_subplots(len(source_list), (10,10), True, row_wise=True)
    fig.suptitle("Subplot Graph of Bookings Per Source And Date")
    i = 0
    for ax in axs.flat:
        ax.plot(source.iloc[:,i])
        ax.set_title(source_list[i])
        ax.tick_params(labelbottom=True)
        ax.xaxis.set_major_formatter(date_form)
        ax.xaxis.set_major_locator(MonthLocator(interval=1))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        ax.set_xlim([start,end])
        i += 1
    fig.supxlabel('Date')
    fig.supylabel('Count')
    plt.savefig('filename.png')


def sub_bookings_made_by_source_monthly(df, use):
    if use == False:
        return
    source = make_date_booked(df, True)
    source.index = pd.to_datetime(source.index)
    start = pd.to_datetime(source.index[0])
    end = pd.to_datetime(source.index[-1])
    date_form = DateFormatter("%m-%y")
    fig, axs = generate_subplots(len(source_list), (10,10), True, row_wise=True)
    fig.suptitle("Subplot Graph of Bookings Made Per Source And Date")
    i = 0
    for ax in axs.flat:
        ax.plot(source.iloc[:,i])
        ax.set_title(source_list[i])
        ax.tick_params(labelbottom=True)
        ax.xaxis.set_major_formatter(date_form)
        ax.xaxis.set_major_locator(MonthLocator(interval=1))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        ax.set_xlim([start, end])
        i += 1
    fig.supxlabel('Date')
    fig.supylabel('Count')
    plt.savefig('filename1.png')


def bookings_made_weekly(df, use):
    if use == False:
        return
    x = make_date_booked(df, False)
    start = pd.to_datetime(x.index[0])
    end = pd.to_datetime(x.index[-1])
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Made Over Time")
    ax.plot(x)
    ax.set(xlabel='Date', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_locator(DayLocator(interval=21))
    ax.xaxis.set_major_formatter(date_form)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim([start, end])
    plt.savefig('filename.png', dpi=600)


def bookings_made_sources_weekly(df, use):
    if use == False:
        return
    x = make_date_booked(df, True)
    start = pd.to_datetime(x.index[0])
    end = pd.to_datetime(x.index[-1])
    x.index = pd.to_datetime(x.index)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Made Over Time By Source")
    ax.plot(x)
    ax.set_ylim(0, 80)
    ax.set(xlabel='Date (weeks)', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_locator(DayLocator(interval=21))
    ax.xaxis.set_major_formatter(date_form)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim([start, end])
    ax.legend(labels=x.columns)


def bookings_weekly(df, use):
    if use == False:
        return
    x = make_date_booking(df, False)
    start = pd.to_datetime(x.index[0])
    end = pd.to_datetime(x.index[-1])
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Over Time")
    ax.plot(x.index, x['count'])
    ax.set(xlabel='Date', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_locator(DayLocator(interval=28))
    ax.xaxis.set_major_formatter(date_form)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim([start, end])
    plt.savefig('filename.png', dpi=600)


def bookings_sources_weekly(df, use):
    if use == False:
        return
    x = make_date_booking(df, True)
    start = pd.to_datetime(x.index[0])
    end = pd.to_datetime(x.index[-1])
    x.index = pd.to_datetime(x.index)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Over Time By Source")
    ax.plot(x)
    ax.set(xlabel='Date', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_locator(DayLocator(interval=28))
    ax.xaxis.set_major_formatter(date_form)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim([start, end])
    ax.legend(labels=x.columns)


def sub_bookings_activities_over_time(df, use):
    if use == False:
        return
    activities_df = bookings_activities_var(df)
    start = pd.to_datetime(activities_df.index[0])
    end = pd.to_datetime(activities_df.index[-1])
    fig, axs = generate_subplots(len(activities.columns), (15, 15), True, row_wise=True)
    fig.suptitle("Subplot of Num Bookings Per Activity Type")
    i = 0
    for ax in axs.flat:
        ax.plot(activities_df[activities_df.columns[i]])
        date_form = DateFormatter("%m-%d-%y")
        ax.xaxis.set_major_locator(DayLocator(interval=28))
        ax.xaxis.set_major_formatter(date_form)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        ax.set_xlim([start,end])
        ax.set_title(activities_df.columns[i])
        ax.axvline(pd.Timestamp('2023-01-17'), linestyle=':', color='red')
        i += 1
    fig.supxlabel('Date')
    fig.supylabel('Count')
    plt.savefig('filename.png')
    fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(10, 5), dpi=600, sharex=True, sharey='row')
    fig.suptitle("Subplot of Num Bookings Per Activity Type (Top 3 Uses)")
    i = 0
    for ax in axs.flat:
        ax.plot(activities_df[activities_df.columns[i]])
        date_form = DateFormatter("%m-%d-%y")
        ax.xaxis.set_major_locator(DayLocator(interval=56))
        ax.xaxis.set_major_formatter(date_form)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        ax.set_xlim([start,end])
        ax.set_title(activities_df.columns[i])
        ax.axvline(pd.Timestamp('2023-01-17'), linestyle=':', color='red')
        i += 1
    fig.supxlabel('Date')
    fig.supylabel('Count')
    plt.savefig('filename.png')
    fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(10, 5), dpi=600, sharex=True, sharey='row')
    fig.suptitle("Subplot of Num Bookings Per Activity Type (Lesser 3 Uses)")
    for ax in axs.flat:
        ax.plot(activities_df[activities_df.columns[i]])
        date_form = DateFormatter("%m-%d-%y")
        ax.xaxis.set_major_locator(DayLocator(interval=56))
        ax.xaxis.set_major_formatter(date_form)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        ax.set_xlim([start,end])
        ax.set_title(activities_df.columns[i])
        ax.axvline(pd.Timestamp('2023-01-17'), linestyle=':', color='red')
        i += 1
    fig.supxlabel('Date')
    fig.supylabel('Count')
    plt.savefig('filename.png')


# %%% amount used


def bar_use_studio(df, use):
    if use == False:
        return
    uses = sqm.used_per_studio(df, studio_list)
    uses.index = uses['Studio']
    plt.figure(dpi = 600)
    for i in studio_list:
        plt.bar(i, uses.loc[i, 'Used'])
        plt.ylim(0, 101)
    plt.xlabel("Studio", size=14)
    plt.ylabel("% Used", size=14)
    plt.title("Bar of Use Per Studio")
    plt.savefig('filename.png')


def sub_bar_use_studio_titled(df, use):
    if use == False:
        return
    uses = sqm.week_of_studios(df, studio_list)
    uses = uses[day_list]
    fig, axs = generate_subplots(len(uses.index), (8, 8), True, row_wise=True)
    fig.suptitle("Subplot of Use By Studio And Day")
    i = 0
    for ax in axs.flat:
        temp = uses.index[i]
        for j in uses.columns:
            ax.bar(j, uses.loc[temp, j])
        ax.set(xlabel='Studio', ylabel='% Used')
        ax.label_outer()
        ax.tick_params(labelrotation=45)
        ax.set_title(temp)
        ax.set_ylim(0, 110)
        i += 1
    plt.savefig('filename.png', dpi=600)


def sub_bar_time_used_day(df, use):
    if use == False:
        return
    df, labels = making_time_graphs(df, 'D')
    fig, axs = generate_subplots(len(labels), (8, 10), 'row', row_wise=True)
    fig.suptitle("Subplots of Part Of Day Used Per Weekday", size = 20)
    i = 0
    for ax in axs.flat:
        for j in df.columns:
            temp = df.index[i]
            ax.bar(j, df.loc[temp, j])
        ax.set_title(labels[i])
        if i < 6: i += 1
        ax.set(xlabel='Time', ylabel='Count')
        ax.set_xticks(np.arange(1, 25))
        ax.set_xlim(8, 21)
    plt.savefig('filename.png', dpi=600)


# %%% heat graphs

def heat_time_used_studio(df, use):
    if use == False:
        return
    studios = making_studio_graphs(df)
    plt.figure(dpi = 600)
    plt.pcolormesh(studios)
    plt.yticks(np.arange(0.5, len(studio_name), 1), studio_name)
    plt.xlabel("Time", size=14)
    plt.ylabel("Day", size=14)
    plt.xticks(np.arange(1, 25))
    plt.xlim(8, 21)
    plt.colorbar(label="Count")
    plt.title("Daily Heat Graph")
    plt.savefig('filename.png', dpi=600)


def heat_time_used_daily(df, use):
    if use == False:
        return
    days, labels = making_time_graphs(df, 'D')
    plt.figure(dpi = 600)
    plt.pcolormesh(days)
    plt.yticks(np.arange(0.5, len(labels), 1), labels)
    plt.xlabel("Time", size=14)
    plt.ylabel("Day", size=14)
    plt.xticks(np.arange(1, 25))
    plt.xlim(8, 21)
    plt.colorbar(label="Count")
    plt.title("Daily Heat Graph")
    plt.savefig('filename.png', dpi=600)


def heat_time_used_weekly(df, use):
    if use == False:
        return
    weeks, labels = making_time_graphs(df, 'W')
    weeks = weeks.dropna()
    leny = labels[:len(weeks)]
    labelsy = leny[::2]
    labelsx = np.arange(1, 25).tolist()
    plt.figure(dpi = 600)
    sn.heatmap(weeks, xticklabels=labelsx)
    plt.yticks(np.arange(0.5, len(leny), 2), labelsy)
    plt.xlabel("Time", size=14)
    plt.ylabel("Week", size=14)
    plt.xlim(7, 22)
    plt.title("Weekly Heat Graph")
    plt.savefig('filename.png', dpi=600)


def heat_time_used_monthly(df, use):
    if use == False:
        return
    months, labels = making_time_graphs(df, 'M')
    plt.figure(dpi = 600)
    plt.pcolormesh(months)
    plt.yticks(np.arange(0.5, len(labels), 1), labels)
    plt.xlabel("Time", size=14)
    plt.ylabel("Month", size=14)
    plt.xticks(np.arange(1, 25))
    plt.xlim(8, 21)
    plt.colorbar(label="Count")
    plt.title("Monthly Heat Graph")
    plt.savefig('filename.png', dpi=600)


def heat_time_used_weekly_by_activity(df, use):
    if use == False:
        return
    df_temp = filter_activities(df)
    labelsx = np.arange(1, 25).tolist()
    fig, axs = plt.subplots(3, 2, figsize=(10,10), layout='tight', sharex=True, sharey=True)
    i = 0
    for ax in axs.flat:
        temp = df_temp[df_temp['Activity']==activities.columns[i]]
        weeks, _ = making_time_graphs(temp, 'W')
        weeks = weeks.fillna(0)
        sn.heatmap(weeks, xticklabels=labelsx, cbar=False, ax=ax)
        ax.set_xlabel("Time", size=14)
        ax.set_ylabel("Date", size=14)
        ax.set_xlim(8, 21)
        ax.set_title(activities.columns[i])
        i += 1
    fig.suptitle("Weekly Heat Graph")
    plt.savefig('filename.png', dpi=600)


def heat_time_used_monthly_by_source(df, use):
    if use == False:
        return
    months, labels = making_time_graphs(df, 'M')
    plt.figure(dpi = 600)
    plt.pcolormesh(months)
    plt.yticks(np.arange(0.5, len(labels), 1), labels)
    plt.xlabel("Time", size=14)
    plt.ylabel("Month", size=14)
    plt.xticks(np.arange(1, 25))
    plt.xlim(8, 21)
    plt.colorbar(label="Count")
    plt.title("Monthly Heat Graph")
    plt.savefig('filename.png', dpi=600)


def time_duration_heat(df, use):
    if use == False:
        return
    df_temp = df.copy()
    df_temp = df_temp[df_temp['Hours'] != 14]
    df_temp['Hours'] = [math.ceil(x) for x in df_temp['Hours']]
    dates, duration = hours_heat_maker(df_temp, 1)
    plt.figure(dpi = 600)
    plt.pcolormesh(dates)
    plt.yticks(np.arange(0.5, len(duration), 1), duration)
    plt.xlabel("Time", size=14)
    plt.ylabel("Length of Booking", size=14)
    plt.xticks(np.arange(1, 25))
    plt.xlim(8, 21)
    plt.colorbar(label="Count")
    plt.title("Time v Duration Heat Graph (rounded to hour)")
    plt.savefig('filename.png', dpi=600)


def time_duration_heat_activity(df, use):
    if use == False:
        return
    df_temp = df.copy()
    df_temp = df_temp[df_temp['Hours'] != 14]
    df_temp['Hours'] = [math.ceil(x) for x in df_temp['Hours']]
    df_temp = df_temp[df_temp['Activity'].isna() == False]
    df_temp = filter_activities(df_temp)
    fig, axs = plt.subplots(3, 2, figsize=(10,10), layout='constrained')
    i = 0
    for ax in axs.flat:
        temp_df = df_temp[df_temp['Activity'] == activities.columns[i]]
        temp, _ = hours_heat_maker(temp_df, 1)
        im = ax.pcolormesh(temp)
        ax.set_yticks(np.arange(1,14))
        ax.set_xticks(np.arange(1, 25))
        ax.set_xlim(8, 21)
        ax.set_title(activities.columns[i])
        ax.label_outer()
        i += 1
    fig.supxlabel('Time', size=14)
    fig.supylabel('Length of Booking', size=14)
    fig.suptitle("Time v Duration Heat Graph (rounded to hour)", size=20)
    cbar = fig.colorbar(im, ax=axs.ravel().tolist(), label="Count")
    cbar.set_ticks([])
    plt.savefig('filename.png', dpi=600)


def time_duration_heat_studio(df, use):
    if use == False:
        return
    df_temp = df.copy()
    df_temp = df_temp[df_temp['Hours'] != 14]
    df_temp['Hours'] = [math.ceil(x) for x in df_temp['Hours']]
    df_temp = df_temp[df_temp['Studio'].isna() == False]
    fig, axs = plt.subplots(3, 2, figsize=(10,10), layout='constrained')
    i = 0
    for ax in axs.flat:
        temp_df = df_temp[df_temp['Studio'] == activities.columns[i]]
        temp, _ = hours_heat_maker(temp_df, 1)
        im = ax.pcolormesh(temp)
        ax.set_yticks(np.arange(1,14))
        ax.set_xticks(np.arange(1, 25))
        ax.set_xlim(8, 21)
        ax.set_title(studio_name[i])
        ax.label_outer()
        i += 1
    fig.supxlabel('Time', size=14)
    fig.supylabel('Length of Booking', size=14)
    fig.suptitle("Time v Duration Heat Graph (rounded to hour)", size=20)
    cbar = fig.colorbar(im, ax=axs.ravel().tolist(), label="Count")
    cbar.set_ticks([])
    plt.savefig('filename.png', dpi=600)


# %%% calendar heat map

def cal_map(df, use):
    if use == False:
        return
    dates = df['Date of Activity']
    dates.index = dates
    events = df['Date of Activity'].value_counts().sort_index(ascending=True)
    calplot.calplot(events, edgecolor='Black', linecolor='w', linewidth=2, fillcolor='w')

    df_filtered = filter_activities(df)
    for i in activities.columns:
        temp = df_filtered[df_filtered['Activity']==i]
        events = temp['Date of Activity'].value_counts().sort_index(ascending=True)
        if len(dates) != 0:
            calplot.calplot(events, edgecolor='Black', linecolor='w', linewidth=2, fillcolor='w', suptitle=i)


# %% filtering

bookings_df = bookings.copy()

filter_on = True
if filter_on == True:
    activities, sources_count, bookings_df = filter_stats_data(bookings_df)
df = bookings_df.copy()


# %% graphing


# attendees
sub_hist_attendees_studio(df, False)
sub_hist_attendees_activities(df, False)
overall_activities_attendees_pie(df, False)


# pie graphs
pie_sources_bookings(df, False)
pie_sources_bookings_sans_direct(df, False)
pie_sources_hours(df, False)
pie_sources_hours_sans_direct(df, False)
sub_pie_duration_activities(df, False)
pie_activities_bookings(df, False)
sub_pie_attendees_activities(df, False)


# duration
hist_dur_studio(df, False)
sub_hist_dur_studio(df, False)
sub_hist_dur_studio_type(df, False)
hist_average_dur_studio(df, False)
sub_hist_duration_activities(df, False)
overall_activities_duration_pie(df, False)

# num bookings/made bookings
bar_bookings_day(df, False)
bookings_made_monthly(df, False)
bookings_made_sources_monthly(df, False)
bookings_monthly(df, False)
bookings_sources_monthly(df, False)
sub_bookings_by_source_monthly(df, False)
sub_bookings_made_by_source_monthly(df, False)
bookings_made_weekly(df, False)
bookings_made_sources_weekly(df, False)
bookings_weekly(df, False)
bookings_sources_weekly(df, False)
sub_bookings_activities_over_time(df, False)


# amount used
bar_use_studio(df, False)
sub_bar_use_studio_titled(df, False)
sub_bar_time_used_day(df, False)


# heat graphs
heat_time_used_studio(df, False)
heat_time_used_daily(df, False)
heat_time_used_weekly(df, False)
heat_time_used_monthly(df, False)
time_duration_heat(df, False)
time_duration_heat_activity(df, False)


# calendar heat map
cal_map(df, False)


# %% for immidiate use

#duration
overall_activities_duration_pie(df, False)
sub_hist_duration_activities(df, False)

#num bookings
sub_bookings_activities_over_time(df, False)
pie_activities_bookings(df, False)

#attendees
overall_activities_attendees_pie(df, False)


# %% Test zone
