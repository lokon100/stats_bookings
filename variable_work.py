# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 14:00:42 2022

@author: Skye
"""

import csv  # analysis:ignore
import pandas as pd  # analysis:ignore
import numpy as np  # analysis:ignore
from operator import itemgetter  # analysis:ignore

from config import atlantic, pit, full_day, days_advance_low, days_advance_high, date_range, use_date, filter_on, source_filter, activity_filter, activities, equipment
from config import file_location as file_loc  # analysis:ignore

from long_bookings import long_bookings, add_many_rows


# %% importing function

def import_csv(file_location):
    file_data = pd.read_csv(file_location, encoding='ISO 8859-1')

    file_parsed = file_data[['Source', 'Date Booked', 'Date of Activity', 'Start Time',
                             'End Time', 'Studio', 'Name', 'Event Name', '# of Attendees',
                             'Activity', 'Equipment', 'Days Prev', 'Hours']]
    file_parsed = file_parsed.iloc[:(file_parsed['Date Booked'].last_valid_index())]
    file_parsed = add_many_rows(file_parsed)
    file_fixed = format_df(file_parsed)
    if filter_on == True:
        file_fixed = filter_stats_data(file_fixed)
    for col in file_fixed:
        file_fixed[col] = file_fixed[col].convert_dtypes()
    return file_fixed


# %% functions to work on data in dataframe

def completeish(duration):  # if booking was full day
    if duration >= 12 or duration <= 0:
        return True
    else:
        return False


def attendees_format(attendees):
    if pd.isnull(attendees) == True:
        return attendees
    tester = 0
    try:
        tester = int(attendees)
    except ValueError:
        return np.nan
    return tester


def string_and_nan_format(val):
    if pd.isnull(val) == True:
        return val
    else:
        return str(val)


def prev_check(days_prev):  # check how I did this
    if days_prev >= 0:
        return int(days_prev)
    else:
        return np.nan


def real_check(date_booking):
    if pd.isnull(date_booking) == True:
        return date_booking
    else:
        return pd.to_datetime(date_booking)


def name_event(name, event):
    if pd.isnull(name) == True:
        return event
    else:
        return name


def type_check(studio):
    if pd.isnull(studio):
        return studio
    else:
        return str(studio[0])


def day_week(date):
    if pd.isnull(date) == True:
        return date
    else:
        return date.day_name()


def hours_check(hours):
    if hours < 1:
        return 1
    if hours > 14:
        return 14
    else:
        return round(float(hours), 1)


def time_format(time):
    if pd.isnull(time):
        return time
    else:
        return pd.to_datetime(time).hour

def source_check(source):
    if pd.isnull(source) == True: return source
    source = str(source)
    if 'walk' in source.lower():
        return "Walk-In"
    else:
        return source


def format_df(dataframe):
    df = dataframe.copy()
    for i in df.index:
        df.loc[i, 'Source'] = source_check(df.loc[i, 'Source'])
        df.loc[i, 'Date Booked'] = real_check(df.loc[i, 'Date Booked'])
        df.loc[i, 'Date of Activity'] = real_check(
            pd.to_datetime(df.loc[i, 'Date of Activity']))
        df.loc[i, 'Studio'] = string_and_nan_format(df.loc[i, 'Studio'])
        df.loc[i, 'Type'] = type_check(df.loc[i, 'Studio'])
        df.loc[i, 'Name'] = name_event(df.loc[i, 'Name'], df.loc[i, 'Event Name'])
        df.loc[i, '# of Attendees'] = attendees_format(df.loc[i, '# of Attendees'])
        df.loc[i, 'Activity'] = string_and_nan_format(df.loc[i, 'Activity'])
        df.loc[i, 'Equipment'] = string_and_nan_format(df.loc[i, 'Equipment'])
        df.loc[i, 'Days Prev'] = prev_check(df.loc[i, 'Days Prev'])
        df.loc[i, 'Hours'] = hours_check(df.loc[i, 'Hours'])
        df.loc[i, 'All Day'] = completeish(df.loc[i, 'Hours'])
        df.loc[i, 'Day'] = day_week(df.loc[i, 'Date of Activity'])
        df.loc[i, 'Start Time'] = time_format(df.loc[i, 'Start Time'])
        df.loc[i, 'End Time'] = time_format(df.loc[i, 'End Time'])
    '''drop_list = []
    for i in df.index:
        if df.loc[i, 'Date of Activity'] == "delete me":
            drop_list.append(i)
        if df.loc[i, 'Days Prev'] == "delete me":
            drop_list.append(i)
        if pd.isnull(df.loc[i, 'Studio']) == True:
            drop_list.append(i)
    df = df.drop(drop_list)'''
    return df


# %% filtering
use_advance_low = True
use_advance_high = True
use_source = True
use_activity = True
if days_advance_low == 0:
    use_advance_low = False
if days_advance_high == 0:
    use_advance_high = False
if source_filter == False:
    use_source = False
if activity_filter == False:
    use_activity = False

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
            check_activity(df.loc[i, 'Activity'], afilter) == True) == False:
            drop_list.append(i)
    return drop_list


def afilter_fun():
    if use_activity == True:
        return activities.loc[1:, activity_filter]
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
        if (x >= date_range[0]) and (x <= date_range[1]) == True:
            return True
        else:
            return False
    else:
        return True


def check_source(x):
    if use_source == True:
        if pd.isna(x):
            return False
        for i in source_filter:
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


def df_string_in(df_col, df_strings):
    string_count = pd.DataFrame(columns = df_strings.columns.tolist())
    for i in df_strings:
        temp = df_strings[i].dropna().tolist()
        count = sum(any(m in L.lower() for m in temp) for L in df_col.dropna())
        string_count.loc[0, i] = count
    return string_count


def list_string_in(df_col, list_string):
    string_count = pd.DataFrame(columns = list_string)
    for i in list_string:
        count = [i in L.lower() for L in df_col.dropna()]
        count = len([s for s in df_col.dropna() if i.lower() in s.lower()])
        string_count.loc[0, i] = count
    return string_count


# %% making the variables

bookings = import_csv(file_loc)

list_length = len(bookings)

"""get list of individuals - no repeats"""
names_unique = bookings.Name.dropna().unique().tolist()

week_names = ["Sunday", "Monday", "Tuesday",
              "Wednesday", "Thursday", "Friday", "Saturday"]
weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
weekend = ["Saturday", "Sunday"]
studio_name = sorted(bookings.Studio.dropna().unique().tolist())
studio_type = sorted(bookings.Type.dropna().unique().tolist())
sources = sorted(bookings.Source.dropna().unique().tolist())


# %% filtering lists


activities_count = df_string_in(bookings['Activity'], activities)
activities = pd.concat([activities_count, activities]).reset_index(drop = True)

equipment_count = df_string_in(bookings['Equipment'], equipment)
equipment = pd.concat([equipment_count, equipment]).reset_index(drop = True)

sources_count = list_string_in(bookings['Source'], sources)
