# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 14:05:48 2022

@author: Skye
"""

# %% importing
import matplotlib as mpl
from matplotlib import pyplot as plt # analysis:ignore
import numpy as np  # analysis:ignore
import pandas as pd  # analysis:ignore
import warnings

from variable_work import bookings, names_unique, week_names, weekday, weekend, studio_name, studio_type, list_length, activities, equipment, sources, sources_count  # analysis:ignore

from stats_question_mark import bookers, studio_uses, average_per_studio, average_per_day, average_week_end, average_per_studio_per_day, making_one_day, studio_per_day, studio_per_week_end, order_days_booked, used_per_day, used_per_studio, week_of_studios, average_count_per_day  # analysis:ignore

from config import atlantic, pit, full_day, days_advance_low, days_advance_high, date_range, use_date, filter_on
from variable_work import use_advance_high, use_advance_low


warnings.simplefilter('ignore', FutureWarning)
mpl.rcParams['figure.dpi'] = 600
df = bookings.copy()

# %% plotting functions


def what_used():
    """
    takes values from config and outputs a string for plot subtitle

    Returns
    -------
    string : string
        descriptor of config
    """
    string = ""
    if filter_on == False:
        return string
    string = string + ("Sans:")
    if atlantic == True:
        string = string + (" Atlantic")
    if pit == True:
        string = string + (" Pit")
    if full_day == True:
        string = string + (" Full Day Bookings")
    if use_advance_low == True:
        string = string + (" " + str(days_advance_low) + " in advance")
    if use_advance_high == True:
        string = string + (" " + str(days_advance_high) + " in advance")
    if use_date == True:
        string = string + \
            (" between " + str(date_range[0]) + " and " + str(date_range[1]))
    return string


def calc_bins_ticks(column, step):
    hmin = int(column.min())
    hmax = int(column.max())
    bins1 = [x * step for x in range(hmin, ((hmax*2)+1))][1:]
    ticks1 = [x for x in range(hmin, hmax+1)]
    return bins1, ticks1


def filter_days(df, dates):
    temp = pd.DataFrame(columns=df.columns)
    df['All Day'].astype(bool)
    temp['All Day'].astype(bool)
    for a in df.index:
        for i in dates:
            if i in df.loc[a, 'Day']:
                temp.loc[a] = df.loc[a]
    return temp


# %% test zone

# hist of dur per studio
studio = studio_name
bins1, ticks1 = calc_bins_ticks(df['Hours'], 0.5)
ax = plt.figure()
plt.xticks(ticks1)
for i in studio:
    x = df.index[df['Studio'] == i].tolist()
    y = df[df.index.isin(x)]
    plt.hist(y['Hours'].dropna(), alpha=0.5, label=i, bins=bins1)
plt.xlabel("Hours", size=14)
plt.ylabel("Count", size=14)
plt.title("Histogram of Hours Per Studio")
plt.legend(loc='upper right')
plt.savefig('filename.png')


# bar of use per studio
uses = used_per_studio(df, studio_name)
uses.index = uses['Studio']
ax = plt.figure()
for i in studio_name:
    plt.bar(i, uses.loc[i, 'Used'])
plt.xlabel("Studio", size=14)
plt.ylabel("% Used", size=14)
plt.title("Bar of Use Per Studio")
plt.savefig('filename.png')


# bar use of x studios on x days
studio = ['1-1', '2-1', '2-2']
dates = ['Monday', 'Tuesday', 'Wednesday']
string1 = ", ".join(studio)
string2 = ", ".join(dates)
uses = week_of_studios(df, studio)
uses = uses[dates]
uses.plot(kind="bar", rot=0)
plt.xlabel("Studio", size=14)
plt.ylabel("% Used", size=14)
plt.title("Bar of " + string1 + " Use On " + string2)
plt.savefig('filename.png', dpi=600)


# bar of count bookings daily
ax = plt.figure()
temp = average_count_per_day(df)['mean']
for i in temp.index:
    plt.bar(i, temp.loc[i])
plt.xlabel("Day", size=14)
plt.xticks(rotation=20)
plt.ylabel("Count", size=14)
plt.title("Bar of Average Number of Bookings Per Day")
plt.savefig('filename.png')


# hist of average dur per studio
studio = studio_name
temp = average_per_day(df, 3, False)
bins1 = [x * 0.5 for x in range(0, ((10*2)+1))][1:]
ticks1 = [x for x in range(0, 10+1)]
ax = plt.figure()
plt.xticks(ticks1)
for i in studio:
    x = df.index[df['Studio'] == i].tolist()
    y = df[df.index.isin(x)]
    y = average_per_day(y, 3, False)
    y = y['HMean']
    y.plot(kind='hist', alpha=0.5, label=i, bins=bins1)
plt.xlabel("Hours", size=14)
plt.ylabel("Count", size=14)
plt.legend(loc='upper right')
plt.title("Histogram of Hours Per Studio")
plt.savefig('filename.png')
