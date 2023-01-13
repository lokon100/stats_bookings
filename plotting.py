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

import variable_work as vw
from variable_work import bookings, week_names, weekday, weekend, studio_name, studio_type, activities, equipment, sources_count, sources  # analysis:ignore

from filtering import filter_stats_data, source_list, studio_list, activity_list, day_list # analysis:ignore

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



def edit_df(df, studio_bool, studio_list, day_bool, day_list, source_bool, source_list, full_day, atlantic, pit):
    if studio_bool == True:
        df = filter_thing(df, studio_list, 'Studio')
    if day_bool == True:
        df = filter_thing(df, day_list, 'Day')
    if source_bool == True:
        df = filter_thing(df, source_list, 'Source')
    df = df.sort_values(by='Date of Activity', ascending=True)
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


def duration_activities_var(df):
    df = df[['Hours', 'Activity']]
    df = df[df['Hours'].notna()]
    df = df[df['Activity'].notna()]
    for i in activities.columns:
        filter_list = activities[i].dropna()[1:].tolist()
        change_list = []
        change_list.extend(df.loc[(df.apply(lambda x: any(m in str(v).lower()  for v in x.values for m in filter_list), axis=1))].index.tolist())
        df.loc[change_list, 'Activity'] = i
    df = filter_thing(df, activities.columns, 'Activity')
    return df

def attendees_activities_var(df):
    df = df[['# of Attendees', 'Activity']]
    df = df[df['# of Attendees'].notna()]
    df = df[df['Activity'].notna()]
    for i in activities.columns:
        filter_list = activities[i].dropna()[1:].tolist()
        change_list = []
        change_list.extend(df.loc[(df.apply(lambda x: any(m in str(v).lower()  for v in x.values for m in filter_list), axis=1))].index.tolist())
        df.loc[change_list, 'Activity'] = i
    df = filter_thing(df, activities.columns, 'Activity')
    return df

def making_time_graphs(df, frame):
    hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
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
    return dates, labels


def make_date_booked(df, source):
    df = df[df['Date Booked'].notna()]
    weeks = pd.date_range(df['Date Booked'].min(), df['Date Booked'].max(), freq='W-MON').strftime('%m/%d/%Y').tolist()
    if source == True:
        source_df = pd.DataFrame(columns=source_list, index=weeks)
        for i in source_list:
            temp_df = date_per_source(df, i)
            x = pd.DataFrame(temp_df['Date Booked'].sub(pd.to_timedelta(temp_df['Date Booked'].dt.dayofweek, unit='D')).value_counts(sort=False))
            source_df[i] = x['Date Booked']
        x = source_df.copy()
    if source == False:
        x = pd.DataFrame(df['Date Booked'].sub(pd.to_timedelta(df['Date Booked'].dt.dayofweek, unit='D')).value_counts(sort=False))
        x.columns = ['count']
        x = x.sort_index(ascending=True)
    x = x.fillna(0)
    return weeks, x

def make_date_booking(df, source):
    df = df[df['Date of Activity'].notna()]
    weeks = pd.date_range(df['Date of Activity'].min(), df['Date of Activity'].max(), freq='W-MON').strftime('%m/%d/%Y').tolist()
    if source == True:
        source_df = pd.DataFrame(columns=source_list, index=weeks)
        for i in source_list:
            temp_df = date_per_source(df, i)
            x = pd.DataFrame(temp_df['Date of Activity'].sub(pd.to_timedelta(temp_df['Date of Activity'].dt.dayofweek, unit='D')).value_counts(sort=False))
            source_df[i] = x['Date of Activity']
        x = source_df.copy()
    if source == False:
        x = pd.DataFrame(df['Date of Activity'].sub(pd.to_timedelta(df['Date of Activity'].dt.dayofweek, unit='D')).value_counts(sort=False))
        x.columns = ['count']
        x = x.sort_index(ascending=True)
    x = x.fillna(0)
    return weeks, x

def date_per_source(df, source):
    df = df[df['Source'] == source]
    return df


# %% graphs

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
    fig, axs = plt.subplots(3, 4, layout="constrained", figsize=(10, 6), dpi=600, sharey='row')
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


def bar_bookings_day(df, use):
    if use == False:
        return
    plt.figure(dpi = 600)
    temp = sqm.average_count_per_day(df)['mean']
    for i in temp.index:
        plt.bar(i, temp.loc[i])
    plt.xlabel("Day", size=14)
    plt.xticks(rotation=20)
    plt.ylabel("Count", size=14)
    plt.title("Bar of Average Number of Bookings Per Day")
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
        y = sqm.average_per_day(x, 3, False)
        y = y['HMean']
        y.plot(kind='hist', alpha=0.5, label=i, bins=bins1)
    plt.xlabel("Hours", size=14)
    plt.ylabel("Count", size=14)
    plt.legend(loc='upper right')
    plt.title("Histogram of Hours Per Studio")
    plt.savefig('filename.png')


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


def sub_hist_attendees_studio(df, use):
    if use == False:
        return
    bins1 = [x * 5 for x in range(int(df['# of Attendees'].max()/5)+2)]
    fig, axs = plt.subplots(4, 3, layout="constrained", figsize=(10, 7.5), dpi=600, sharex='col', sharey=True)
    fig.suptitle("Subplot Hist of Attendees Per Studio")
    i = 0
    for ax in axs.flat:
        x = df.index[df['Studio']==studio_list[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['# of Attendees'].dropna(), bins=bins1)
        ax.set_title(studio_list[i])
        i += 1
    fig.supxlabel('Hours')
    fig.supylabel('Count')
    plt.savefig('filename.png')


def sub_hist_duration_activities(df, use):
    if use == False:
        return
    df = duration_activities_var(df)
    bins1 = [x * 1 for x in range(0, 15)][1:]
    ticks1 = [x*2 for x in range(0, 8)]
    activities_df = activities.sort_values(by=activities.index[0], ascending=False, axis=1)
    fig, axs = plt.subplots(2, 3, layout="constrained", figsize=(5.5, 3.5), dpi=600, sharex=True, sharey='row')
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


def sub_hist_attendees_activities(df, use):
    if use == False:
        return
    df = attendees_activities_var(df)
    bins1 = [x * 1 for x in range(0, ((10*2)+1))][1:]
    ticks1 = [x*5 for x in range(0, 7)]
    fig, axs = plt.subplots(2, 3, layout="constrained", figsize=(5.5, 3.5), dpi=600, sharey=True, sharex=True)
    fig.suptitle("Subplot Hist of Attendees Per Activity Type")
    i = 0
    for ax in axs.flat:
        ax.label_outer()
        x = df.index[df['Activity'] == activities.columns[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['# of Attendees'], bins=bins1)
        ax.set_title(activities.columns[i])
        ax.set_xticks(ticks1)
        i += 1
    fig.supxlabel('Hours')
    fig.supylabel('Count')
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


def overall_activities_attendees_pie(df, use):
    if use == False:
        return
    df = attendees_activities_var(df)
    x = df.groupby('Activity')['# of Attendees'].agg(['sum'])
    x = x.sort_values(by='sum', ascending=False)
    porcent = 100.*x['sum']/x['sum'].sum()
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(x.index, porcent)]
    plt.figure(dpi = 600)
    plt.pie(x['sum'], wedgeprops={"edgecolor":"k",'linewidth': 0.5})
    plt.axis('equal')
    plt.legend(labels, bbox_to_anchor=(0.85,1.025), loc="upper left")
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75)
    plt.title("Activities by Attendees Breakdown")
    plt.savefig('filename.png')


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
    labelsy = leny[::4]
    plt.figure(dpi = 600)
    plt.pcolormesh(weeks)
    plt.yticks(np.arange(0.5, len(leny), 4), labelsy)
    plt.xlabel("Time", size=14)
    plt.ylabel("Week", size=14)
    plt.xticks(np.arange(1, 25))
    plt.xlim(8, 21)
    plt.colorbar(label="Count")
    plt.title("Daily Heat Graph")
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
    plt.title("Daily Heat Graph")
    plt.savefig('filename.png', dpi=600)


def sub_bar_time_used_day(df, use):
    if use == False:
        return
    df, labels = making_time_graphs(df, 'D')
    fig, axs = plt.subplots(2, 4, layout="constrained", figsize=(18, 10), dpi=600, sharey='row')
    fig.delaxes(axs[1,3])
    fig.suptitle("Subplots of Part Of Day Used Per Weekday", size = 20)
    i = 0
    for ax in axs.flat:
        for j in df.columns:
            temp = df.index[i]
            ax.bar(j, df.loc[temp, j])
        if i < 6: i += 1
        ax.set(xlabel='Time', ylabel='Count')
        ax.set_title(df.index[i])
        ax.set_xticks(np.arange(1, 25))
        ax.set_xlim(8, 21)
    plt.savefig('filename.png', dpi=600)


def bookings_made_monthly(df, use):
    if use == False:
        return
    weeks, x = make_date_booked(df, False)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Made Over Time")
    ax.plot(x.index, x['count'])
    ax.set(xlabel='Date (months)', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(MonthLocator(interval=1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_ylim(0, x['count'].max()+10)
    plt.savefig('filename.png', dpi=600)


def bookings_made_sources_monthly(df, use):
    if use == False:
        return
    weeks, x = make_date_booked(df, True)
    x.index = pd.to_datetime(x.index)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Made Over Time By Source")
    ax.plot(x)
    ax.set_ylim(0, 80)
    ax.set(xlabel='Date (months)', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(MonthLocator(interval=1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.legend(labels=x.columns)


def bookings_monthly(df, use):
    if use == False:
        return
    weeks, x = make_date_booking(df, False)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Over Time")
    ax.plot(x.index, x['count'])
    ax.set(xlabel='Date (months)', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(MonthLocator(interval=1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_ylim(0, x['count'].max()+10)
    plt.savefig('filename.png', dpi=600)


def bookings_sources_monthly(df, use):
    if use == False:
        return
    weeks, x = make_date_booking(df, True)
    x.index = pd.to_datetime(x.index)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Over Time By Source")
    ax.plot(x)
    ax.set_ylim(0, 60)
    ax.set(xlabel='Date (months)', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(MonthLocator(interval=1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.legend(labels=x.columns)


def bookings_made_weekly(df, use):
    if use == False:
        return
    weeks, x = make_date_booked(df, False)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Made Over Time")
    ax.plot(x.index, x['count'])
    ax.set(xlabel='Date (weeks)', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_locator(DayLocator(interval=21))
    ax.xaxis.set_major_formatter(date_form)
    ax.set_ylim(0, x['count'].max()+10)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    plt.savefig('filename.png', dpi=600)


def bookings_made_sources_weekly(df, use):
    if use == False:
        return
    weeks, x = make_date_booked(df, True)
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
    ax.legend(labels=x.columns)


def bookings_weekly(df, use):
    if use == False:
        return
    weeks, x = make_date_booking(df, False)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Over Time")
    ax.plot(x.index, x['count'])
    ax.set(xlabel='Date (weeks)', ylabel='Count')
    date_form = DateFormatter("%m-%d-%y")
    ax.xaxis.set_major_locator(DayLocator(interval=21))
    ax.xaxis.set_major_formatter(date_form)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_ylim(0, x['count'].max()+10)
    plt.savefig('filename.png', dpi=600)


def bookings_sources_weekly(df, use):
    if use == False:
        return
    weeks, x = make_date_booking(df, True)
    labels = weeks[::2]
    x.index = pd.to_datetime(x.index)
    fig, ax = plt.subplots(layout="constrained")
    fig.suptitle("Num Bookings Over Time By Source")
    ax.plot(x)
    ax.set_ylim(0, 60)
    ax.set(xlabel='Date (weeks)', ylabel='Count')
    ax.set_xticks(pd.to_datetime(labels))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.legend(labels=x.columns)



# %% filtering

bookings_df = bookings.copy()

filter_on = True
if filter_on == True:
    bookings_df = filter_stats_data(bookings_df)
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
sub_pie_attendees_activities(df, False)


# duration
hist_dur_studio(df, False)
hist_average_dur_studio(df, False)
sub_hist_duration_activities(df, False)
overall_activities_duration_pie(df, False)


# num bookings/made bookings
bar_bookings_day(df, False)
bookings_made_monthly(df, False)
bookings_made_sources_monthly(df, False)
bookings_monthly(df, False)
bookings_sources_monthly(df, False)
bookings_made_weekly(df, False)
bookings_made_sources_weekly(df, False)
bookings_weekly(df, False)
bookings_sources_weekly(df, False)


# amount used
bar_use_studio(df, False)
sub_bar_use_studio_titled(df, False)
sub_bar_time_used_day(df, False)
# heat graphs
heat_time_used_daily(df, False)
heat_time_used_weekly(df, False)
heat_time_used_monthly(df, False)
