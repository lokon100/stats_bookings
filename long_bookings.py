# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 16:27:49 2023

@author: Skye
"""

import pandas as pd
import numpy as np

def add_row(df, add, name, studio, hours):
    x = len(df)
    for i, a in enumerate(add):
        df.loc[(i+x)] = [name, a, studio, hours]
    return df


two_five = pd.date_range("20230123", "20230605")
mon = pd.date_range("20230123", "20230601", freq='W-MON')
wed = pd.date_range("20230123", "20230601", freq='W-WED')
pit = pd.date_range("20220924", "20230401")

long_bookings = pd.DataFrame(columns=['Name', 'Date', 'Studio', 'Num Hours'])
long_bookings = add_row(long_bookings, two_five, 'Atlantic Theater Studio', '2-5', 24)
studios = ['1-1', '2-4', '4', '2-3']
for i in studios:
    long_bookings = add_row(long_bookings, mon, 'Atlantic Theater Studio', i, 9.5)
    long_bookings = add_row(long_bookings, wed, 'Atlantic Theater Studio', i, 9.5)
long_bookings = add_row(long_bookings, pit, 'The Pit', '2-1', 24)


def add_many_rows(df):
    col = df.columns.tolist()
    temp = pd.DataFrame(columns=col)
    for i, a in enumerate(long_bookings.index):
        temp.loc[i] = ['Direct', np.nan, long_bookings.loc[a, 'Date'], np.nan, np.nan, long_bookings.loc[a, 'Studio'], long_bookings.loc[a, 'Name'], np.nan, np.nan, 'improv',  np.nan, np.nan, long_bookings.loc[a, 'Num Hours']]
    df = pd.concat([df, temp], ignore_index=True)
    return df
