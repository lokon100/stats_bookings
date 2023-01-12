# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 17:22:58 2023

@author: Skye
"""

import pandas as pd

from config import studio_list, day_list, source_list, activity_list, use_activity, use_advance_high, use_advance_low, use_source, use_date, atlantic, pit, full_day, date_range, days_advance_low, days_advance_high, use_weekday, use_studio, activities

from variable_work import studio_name, week_names, sources

activity_list = activity_list
studio_list = studio_list
day_list = day_list
source_list = source_list

if use_activity == False: activity_list = activities
if use_studio == False: studio_list = studio_name
if use_weekday == False: day_list = week_names
if use_source == False: source_list = sources


def filter_stats_data(dataframe):
    df = dataframe.copy()
    drop_list = total_check(df)
    df = df.drop(drop_list)
    return df


def total_check(df):
    afilter = afilter_fun()
    drop_list = []
    for i in df.index:
        if (check_atlantic(df.loc[i, 'Name']) and
            check_pit(df.loc[i, 'Name']) == True and
            check_full_day(df.loc[i, 'All Day'], df.loc[i, 'Hours']) == True and
            check_advance(df.loc[i, 'Days Prev']) == True and
            check_date(df.loc[i, 'Date of Activity']) == True and
            check_source(df.loc[i, 'Source']) == True and
            check_activity(df.loc[i, 'Activity'], afilter) == True and
            check_day(df.loc[i, 'Day']) == True and
            check_studio(df.loc[i, 'Studio']) == True) == False:
            drop_list.append(i)
    return drop_list


def afilter_fun():
    if use_activity == True:
        print(True)
        return activities.loc[1:, activity_list]
    else:
        return pd.DataFrame()

def check_atlantic(x):
    if pd.isna(x):
        return True
    if atlantic == True:
        if "atlantic" not in x.lower():
            return True
        else:
            return False
    else:
        return True


def check_pit(x):
    if pd.isna(x):
        return True
    if pit == True:
        if "the pit" in x.lower():
            return False
        else:
            return True
    else:
        return True


def check_full_day(x, y):
    if pd.isnull(x):
        x = False
        if pd.isnull(y):
            return True
    if pd.isnull(y):
        y = False
    if full_day:
        if x == False:
            if y == 14:
                return False
            else:
                return True
        else:
            return False
    else:
        return True


def check_advance(x):
    if pd.isna(x):
        return True
    if use_advance_low != True:
        if use_advance_high == True:
            if x >= days_advance_low:
                if x <= days_advance_high:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return True
    else:
        return False


def check_date(x):
    if pd.isna(x):
        return True
    if use_date == True:
        if date_range[0] <= x <= date_range[1]:
            return True
        else:
            return False
    else:
        return True


def check_source(x):
    if use_source == True:
        if pd.isna(x):
            return False
        for i in source_list:
            if i.lower() in x.lower():
                return True
        else:
            return False
    else:
        return True


def check_activity(x, afilter):
    if use_activity == True:
        if pd.isna(x):
            return False
        for i in afilter:
            for j in afilter[i]:
                if pd.isna(j):
                    pass
                elif j.lower() in x.lower():
                    return True
        else:
            return False
    else:
        return True


def check_day(x):
    if use_weekday == True:
        if pd.isna(x):
            return False
        for i in day_list:
            if i.lower() in x.lower():
                return False
        else:
            return False
    else:
        return True


def check_studio(x):
    if use_studio == True:
        if pd.isna(x):
            return False
        for i in studio_list:
            if i.lower() in x.lower():
                return False
        else:
            return False
    else:
        return True
