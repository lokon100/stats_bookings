# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 14:00:42 2022

@author: Skye
"""

import pandas as pd
import numpy as np

from config import file_location as file_loc
from config import activities, equipment

from long_bookings import add_many_rows


# %% importing function

def import_csv(file_location):
    file_data = pd.read_csv(file_location, encoding='ANSI')

    file_parsed = file_data[['Source', 'Date Booked', 'Date of Activity', 'Start Time',
                             'End Time', 'Studio', 'Name', 'Event Name', '# of Attendees', 'Activity', 'Equipment', 'Days Prev', 'Hours']]
    file_parsed = file_parsed.iloc[:(file_parsed['Date Booked'].last_valid_index())]
    file_parsed = add_many_rows(file_parsed)
    file_fixed = format_df(file_parsed)
    for col in file_fixed:
        file_fixed[col] = file_fixed[col].convert_dtypes()
    file_fixed = file_fixed.sort_values(by='Date of Activity', ascending=True)
    file_fixed = (file_fixed.reset_index()).iloc[: , 1:]
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
    if val == 1 or val == '1':
        return '1-1'
    else:
        return str(val).title().strip()


def prev_check(days_prev):
    if days_prev >= 0:
        return int(days_prev)
    else:
        return np.nan


def real_check(date_booking):
    if pd.isnull(date_booking) == True:
        return date_booking
    else:
        try:
            return pd.to_datetime(date_booking)
        except:
            pass


def name_event(name, event):
    if pd.isnull(name) == True:
        return str(event).title().strip()
    if "atlantic" in str(name).lower():
        return("Atlantic Theatre Company")
    else:
        return str(name).title().strip()


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


def time_format(time, complete, se):
    if pd.isnull(time):
        return time
    if pd.to_datetime(time) < pd.to_datetime("20200123"):
        return np.nan
    if complete == True:
        if se == 'start':
            return pd.to_datetime('00:00:00')
        if se == 'end':
            return pd.to_datetime('23:00:00')
    else:
        return pd.to_datetime(time)

def source_check(source):
    if pd.isnull(source) == True: return source
    source = str(source).title().strip()
    if 'walk' in source.lower():
        return "Walk-In"
    else:
        return source


def format_df(dataframe):
    df = dataframe.copy()
    drop_list = []
    for i in df.index:
        if pd.isna(df.loc[i, 'Start Time']):
            drop_list.append(i)
        df.loc[i, 'Source'] = source_check(df.loc[i, 'Source'])
        df.loc[i, 'Date Booked'] = real_check(df.loc[i, 'Date Booked'])
        df.loc[i, 'Date of Activity'] = real_check(df.loc[i, 'Date of Activity'])
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
        df.loc[i, 'Start Time'] = time_format(df.loc[i, 'Start Time'], df.loc[i, 'All Day'], 'start')
        df.loc[i, 'End Time'] = time_format(df.loc[i, 'End Time'], df.loc[i, 'All Day'], 'end')
    df = df.drop(drop_list)
    df = df.drop(['Event Name'], axis=1)
    return df

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

equipment_count = df_string_in(bookings['Equipment'], equipment)
equipment = pd.concat([equipment_count, equipment]).reset_index(drop = True)
