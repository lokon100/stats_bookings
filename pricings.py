# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 17:07:48 2023

@author: Skye
"""

import pandas as pd
import matplotlib.pyplot as plt

from variable_work import bookings


# %% functions

def make_2(df):
    temp = ['2-1', '2-2', '2-3', '2-4', '2-5']
    df = df.loc[df['Studio'].isin(temp)]
    studio_2 = df.sort_values(by='Date of Activity',ascending=True)
    studio_2 = studio_2.reset_index(drop=True)
    return studio_2

def make_3(df):
    temp = ['3-1', '3-2', '3-3', '3-4']
    df = df.loc[df['Studio'].isin(temp)]
    studio_3 = df.sort_values(by='Date of Activity',ascending=True)
    studio_3 = studio_3.reset_index(drop=True)
    return studio_3

def hourly_daily(df):
    hourly = df.loc[df['Hours'] <= 8]
    hourly = hourly.sort_values(by='Date of Activity',ascending=True)
    hourly = hourly.reset_index(drop=True)
    daily = df.loc[df['Hours'] >= 8]
    daily = daily.reset_index(drop=True)
    daily = daily.sort_values(by='Date of Activity',ascending=True)
    return hourly, daily

def find_consec(df):
    day = pd.Timedelta('1d')
    in_block = (df['Date of Activity'].diff(-1) == -day) | (df['Date of Activity'].diff() == day)
    filt = df.loc[in_block]
    breaks = filt["Date of Activity"].diff() != day
    groups = breaks.cumsum()
    consec = filt.assign(group=groups.values)
    return consec


# %% defining variables

cols = ['Source', 'Date of Activity', 'Start Time', 'End Time', 'Studio', 'Name', 'Activity', 'Hours', 'Type', 'Day']
bookings = bookings[cols]

studio_2 = make_2(bookings)
hourly_2, daily_2 = hourly_daily(studio_2)

studio_3 = make_3(bookings)
hourly_3, daily_3 = hourly_daily(studio_3)



# %%

df = daily_2.copy()
df['group'] = ""

def grouped_dates(df):               # returns dataframe of consecutive dates, grouped
    names = df.Name.dropna().unique().tolist()
    consec_dates = pd.DataFrame()
    for i in names:
        tester = df.loc[df['Name'] == i]
        tester = tester.drop_duplicates(subset=['Date of Activity'], keep='first')
        if tester is not None:
            tester = find_consec(tester)
            tester['group'] = i + tester['group'].astype(str)
            consec_dates = pd.concat([consec_dates, tester])
    counting = consec_dates.value_counts('group')
    return consec_dates, counting

consec, counting = grouped_dates(df)
weekly = counting[(counting <= 25) & (counting >= 5)]
weekly = consec[consec['group'].isin(weekly.index)]

monthly = counting[counting > 25]
monthly = consec[consec['group'].isin(monthly.index)]


df = studio_2.copy()
df['group'] = ""
df.loc[hourly_2.index, 'group'] = 'hourly'
df.loc[daily_2.index, 'group'] = 'daily'
df.loc[weekly.index, 'group'] = 'weekly'
df.loc[monthly.index, 'group'] = 'monthly'


plt.figure()
df['group'].value_counts().plot(kind='bar')
