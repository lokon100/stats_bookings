# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 16:27:49 2023

@author: Skye
"""

import pandas as pd
import numpy as np

def add_row(df, add, name, studio, hours, start, end):
    x = len(df)
    for i, a in enumerate(add):
        df.loc[(i+x)] = [name, a, studio, hours, pd.to_datetime(start), pd.to_datetime(end)]
    return df


# %% making long bookings data

long_bookings = pd.DataFrame(columns=['Name', 'Date', 'Studio', 'Num Hours', 'Start', 'End'])

# %%% Pit Bookings

pit = pd.date_range("20230101", "20230630")
long_bookings = add_row(long_bookings, pit, 'The Pit', '1-2', 24, '00:00:00', '23:00:00')

# %%% Atlantic Bookings

# spring 2023
two_five = pd.date_range("20230123", "20230505")
mon = pd.date_range("20230123", "20230601", freq='W-MON')
wed = pd.date_range("20230123", "20230601", freq='W-WED')
long_bookings = add_row(long_bookings, two_five, 'Atlantic Theater Company', '2-5', 24, '00:00:00', '23:00:00')
studios = ['1-1', '2-3', '2-4', '4']
for i in studios:
    long_bookings = add_row(long_bookings, mon, 'Atlantic Theater Company', i, 9.5, '8:30:00', '18:00:00')
    long_bookings = add_row(long_bookings, wed, 'Atlantic Theater Company', i, 9.5, '8:30:00', '18:00:00')


# summer 2023
two_five = pd.date_range("20230706", "20230808")
mon = pd.date_range("20230710", "20230804", freq='W-MON')
tues = pd.date_range("20230710", "20230804", freq='W-TUE')
wed = pd.date_range("20230710", "20230804", freq='W-WED')
thurs = pd.date_range("20230710", "20230804", freq='W-THU')
fri = pd.date_range("20230710", "20230804", freq='W-FRI')
long_bookings = add_row(long_bookings, two_five, 'Atlantic Theater Company', '2-5', 24, '00:00:00', '23:00:00')
studios = ['1-1', '2-4', '4']
for i in studios:
    long_bookings = add_row(long_bookings, mon, 'Atlantic Theater Company', i, 9.5, '8:30:00', '18:00:00')
    long_bookings = add_row(long_bookings, tues, 'Atlantic Theater Company', i, 9.5, '8:30:00', '18:00:00')
    long_bookings = add_row(long_bookings, wed, 'Atlantic Theater Company', i, 9.5, '8:30:00', '18:00:00')
    long_bookings = add_row(long_bookings, thurs, 'Atlantic Theater Company', i, 9.5, '8:30:00', '18:00:00')
    long_bookings = add_row(long_bookings, fri, 'Atlantic Theater Company', i, 9.5, '8:30:00', '18:00:00')


# %% to send to main df

def add_many_rows(df):
    col = df.columns.tolist()
    temp = pd.DataFrame(columns=col)
    for i, a in enumerate(long_bookings.index):
        temp.loc[i] = ['Direct', np.nan, long_bookings.loc[a, 'Date'], long_bookings.loc[a, 'Start'], long_bookings.loc[a, 'End'], long_bookings.loc[a, 'Studio'], long_bookings.loc[a, 'Name'], np.nan, np.nan, 'improv',  np.nan, np.nan, long_bookings.loc[a, 'Num Hours']]
    df = pd.concat([df, temp], ignore_index=True)
    return df
