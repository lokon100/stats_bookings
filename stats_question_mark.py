# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 13:34:04 2022

@author: Skye
"""

import pandas as pd
import numpy as np

from variable_work import bookings, names_unique, studio_name, studio_type, week_names, weekday, weekend, list_length, equipment, sources  # analysis:ignore

from filtering import filter_stats_data, source_list, studio_list, day_list # analysis:ignore

bookings_df = bookings.copy()

filter_on = True
if filter_on == True:
    activities, sources_count, bookings_df = filter_stats_data(bookings_df)
df = bookings_df.copy()


# %% Bookers
"""Bookers, number and duration"""


def bookers(df, dates):
    """getting the number of bookings and duration per person"""
    df = df[(df['Date of Activity'] > dates[0]) & (df['Date of Activity'] < dates[1])]
    df = df[['Name', 'Hours']]
    df = df.groupby('Name').agg(['count', 'sum']).droplevel(0, axis=1)
    sorted_names_bookings = (df.sort_values('count', ascending=False)).iloc[:10]
    sorted_names_hourly = (df.sort_values('sum', ascending=False)).iloc[:10]
    #print top 10
    print("Top 10 By Bookings")
    num = 1
    for i in sorted_names_bookings.index:
        print(str(num) + ": " + i + "\t" +
              str(sorted_names_bookings.loc[i, 'count']))
        num += 1
    print("Top 10 By Hours")
    num = 1
    for i in sorted_names_hourly.index:
        print(str(num) + ": " + i + "\t" +
              str(sorted_names_hourly.loc[i, 'sum']))
    return df


def bookers_month(df, dates):
    """getting the number of bookings and duration per person per month"""
    df = df[['Date of Activity', 'Name', 'Hours']]
    df = df[(df['Date of Activity'] > dates[0]) & (df['Date of Activity'] < dates[1])]
    df['Date of Activity'] = df['Date of Activity'].dt.month
    df = df.groupby(['Date of Activity', 'Name']).agg(['count', 'sum']).droplevel(0, axis=1)
    df.reset_index(inplace=True, level=['Date of Activity', 'Name'])
    df = (df.sort_values(by='Date of Activity', ascending=True))
    df['Date of Activity'] = pd.to_datetime(df['Date of Activity'], format='%m').dt.month_name()
    df.to_csv("bookers.csv")
    return df


# %% Studio Use
"""Studios, number of uses per studio and type"""


def studio_uses(df, dates, print_bool):
    """adding up the total uses of studios"""
    df = df[(df['Date of Activity'] > dates[0]) & (df['Date of Activity'] < dates[1])]
    studio_use = df['Studio'].value_counts().sort_index(ascending=True)
    if print_bool == True:
        print("Total Uses Of Studios")
        for i in studio_use.index:
            print("Studio " + str(i) + "\t" + str(studio_use[i]))
    return studio_use


# %% Average Duration/Days Prev/Num Of Bookings
"""Average duration/days prev of bookings, by studio, studio type, day of week and weekday/end"""


def average_per_studio(df, name_type, print_bool):
    """calculating average by studio
    use = (1) duration or (2) days prev, or (3) for both"""
    temp = df[[name_type, 'Hours', 'Days Prev']]
    studio_cols = temp.groupby('Studio').agg(['mean', 'sum'])
    studio_cols.columns = ['HMean', 'HSum', 'PMean', 'PSum']
    if print_bool == True:
        print("Duration Average")
        for i in studio_cols.index:
            print(str(i) + "\t" + str(round(studio_cols.loc[i, 'HMean'], 2)))
        print("Days Prev Average")
        for i in studio_cols.index:
            print(str(i) + "\t" + str(round(studio_cols.loc[i, 'PMean'], 2)))
    return studio_cols


def average_per_day(df, print_bool):
    """calculating average by day of week"""
    temp = df[['Day', 'Hours', 'Days Prev']]
    day_cols = temp.groupby('Day').agg(['mean', 'sum']).droplevel(0, axis=1)
    day_cols.columns = ['HMean', 'HSum', 'PMean', 'PSum']
    day_cols['Count'] = average_count_per_day(df)['mean']
    if print_bool == True:
        print("Duration Average")
        for i in day_cols.index:
            print(str(i) + "\t" + str(round(day_cols.loc[i, 'HMean'], 2)))
        print("Days Prev Average")
        for i in day_cols.index:
            print(str(i) + "\t" + str(round(day_cols.loc[i, 'PMean'], 2)))
        print("Bookings Per Day Average")
        for i in day_cols.index:
            print(str(i) + "\t" + str(round(day_cols.loc[i, 'Count'], 2)))
    return day_cols


def average_week_end(df, print_bool):
    """calculating average by weekday/end"""
    per_day = average_per_day(df, False)
    average_weekday = per_day[['HMean', 'PMean']].loc[weekday]
    weekday_calc = average_weekday.mean()
    average_weekend = per_day[['HMean', 'PMean']].loc[weekend]
    weekend_calc = average_weekend.mean()
    if print_bool == True:
        print("Duration Average")
        print("Weekday" + "\t" + "Duration: "
              + str(round(weekday_calc.loc['HMean'], 2)))
        print("Weekend" + "\t" + "Duration: "
              + str(round(weekend_calc.loc['HMean'], 2)))
        print("Days Prev Average")
        print("Weekday" + "\t" + "Days Prev: "
              + str(round(weekday_calc.loc['PMean'], 2)))
        print("Weekend" + "\t" + "Days Prev: "
              + str(round(weekend_calc.loc['PMean'], 2)))
    return average_weekday, average_weekend


def average_per_studio_per_day(df, print_bool):
    """calculating average by studio (type)"""
    temp = df[['Studio', 'Day', 'Hours', 'Days Prev']]
    studio_cols = temp.groupby(['Studio', 'Day']).agg(
        ['mean', 'sum', 'count']).droplevel(0, axis=1)
    studio_cols.columns = ['DurMean', 'DurSum',
                           'DurCount', 'PrevMean', 'PrevSum', 'PrevCount']
    if print_bool == True:
        print("Average Duration")
        for i in studio_name:
            studio = studio_cols[['DurMean', 'DurSum', 'DurCount']].loc[i]
            print("\n" + "Studio " + i)
            print(round(studio, 2))
        print("\n Average Prev Days")
        for i in studio_name:
            studio = studio_cols[['PrevMean', 'PrevSum', 'PrevCount']].loc[i]
            print("\n" + "Studio " + i)
            print(round(studio, 2))
    return studio_cols


def average_count_per_day(df):
    week = week_names
    temp = pd.DataFrame(index=df['Date of Activity'])
    temp = pd.DataFrame(temp.index.normalize().value_counts())
    temp.index = temp.index.day_name()
    temp1 = temp.groupby(temp.index).agg(['mean', 'sum']).droplevel(0, axis=1)
    #temp1['mean'] = round(temp1['mean'], 2)
    temp1 = temp1.reindex(week)
    return temp1


# %% When Booked Most
"""When studios and types are booked the most"""


def making_one_day(df, day, name_type):
    """making one day list"""
    studio_day = df[['Day', name_type, 'Hours']]
    studio_day = studio_day.loc[studio_day['Day'] == day]
    studio_day = studio_day[[name_type, 'Hours']]  # for one weekday
    studio_day = studio_day.groupby([name_type]).agg(
        ['mean', 'count']).droplevel(0, axis=1)
    return studio_day

def making_one_studio(df, studio, name_type):
    """making one day list"""
    studio_day = df[['Day', name_type, 'Hours']]
    studio_day = studio_day.loc[studio_day[name_type] == studio]
    temp = studio_day[['Day', 'Hours']]
    temp = temp.groupby(['Day']).agg(['mean', 'count']).droplevel(0, axis=1)
    return temp


def studio_per_day(df, name_type, print_bool):
    """calculating per day most booked studio"""
    week_calc = pd.DataFrame(
        columns=['max studio', 'max hours', 'count studio', 'count bookings'])
    for day in week_names:
        day_studios = making_one_day(df, day, name_type)
        max_hours = day_studios['mean'].idxmax()
        max_bookings = day_studios['count'].idxmax()
        week_calc.loc[day] = [max_hours, day_studios['mean'][max_hours],
                              max_bookings, day_studios['count'][max_bookings]]
    if print_bool == True:
        for i in week_calc.index:
            print(str(i) + ":" + "\t" + "top by hour: Studio "
                  + str(week_calc.loc[i, 'max studio']) + " "
                  + str(round(week_calc.loc[i, 'max hours'], 2))
                  + "\t" + "top by booking: Studio "
                  + str(week_calc.loc[i, 'count studio']) + " "
                  + str(round(week_calc.loc[i, 'count bookings'], 2)))
    return week_calc


def day_per_studio(df, name_type, print_bool):
    """calculating per day most booked studio"""
    studio_calc = pd.DataFrame(
        columns=['max day', 'max hours', 'count day', 'count bookings'])
    for studio in studio_list:
        day_studios = making_one_studio(df, studio, name_type)
        max_hours = day_studios['mean'].idxmax()
        max_bookings = day_studios['count'].idxmax()
        studio_calc.loc[studio] = [max_hours, day_studios['mean'][max_hours],
                              max_bookings, day_studios['count'][max_bookings]]
    if print_bool == True:
        for i in studio_calc.index:
            print(str(i) + ":" + "\t" + "top by hour: "
                  + str(studio_calc.loc[i, 'max day']) + " "
                  + str(round(studio_calc.loc[i, 'max hours'], 2))
                  + "\t" + "top by booking: "
                  + str(studio_calc.loc[i, 'count day']) + " "
                  + str(round(studio_calc.loc[i, 'count bookings'], 2)))
    return studio_calc


# %% Days Booked Most
"""Order of Days Booked Most"""


def order_days_booked(df, print_bool):
    days_booked = df[['Day', 'Hours']]
    days_bookings = pd.DataFrame(columns=['Hours', 'Bookings', 'HMean'])
    calc = days_booked.groupby(['Day']).agg(['mean']).droplevel(0, axis=1)
    for day in week_names:
        day_of = days_booked.loc[days_booked['Day'] == day]
        days_bookings.loc[day] = [day_of['Hours'].sum(), day_of['Day'].count(),
                                  calc.loc[day, 'mean']]
    bookings_hours = (days_bookings.sort_values('Hours', ascending=False))
    bookings_count = (days_bookings.sort_values('Bookings', ascending=False))
    bookings_mean = (days_bookings.sort_values('HMean', ascending=False))

    if print_bool == True:
        print("By hours booked: ")
        for i in bookings_hours.index:
            print(str(i) + " " + str(round(bookings_hours.loc[i, 'Hours'])))
        print("By number of bookings: ")
        for i in bookings_count.index:
            print(str(i) + " " + str(round(bookings_count.loc[i, 'Bookings'])))
        print("By average hours booked: ")
        for i in bookings_count.index:
            print(str(i) + " " + str(round(bookings_mean.loc[i, 'HMean'], 2)))
    return days_bookings


# %% Percentage Used
"""Utilization Percentage"""


def open_hours(day):
    if day in weekday:
        return 14
    if day == 'Saturday':
        return 13
    if day == 'Sunday':
        return 9


def used_per_day(df, studios):
    by_day_average = pd.DataFrame()
    df_studio = df[df['Studio'].isin(studios)]
    for i in week_names:
        day = df_studio[df_studio['Day'] == i]
        y = day.groupby(day['Date of Activity'].dt.date)['Hours'].agg('count')
        z = day.groupby(day['Date of Activity'].dt.date)['Hours'].agg('sum')
        day_df = pd.DataFrame(columns=['sum', 'count', 'used'], index=z.index)
        day_df['sum'] = z
        day_df['count'] = y
        for j, a in enumerate(day_df.index):
            hours_total = day_df.iloc[j]['count'] * open_hours(i)
            used = round(((day_df.iloc[j]['sum']/hours_total)*100), 2)
            if used > 100: used = 100
            day_df.loc[a, 'used'] = used
        used_list = (day_df['used']).tolist()
        dates = pd.Series(day_df.index)
        if len(dates) < len(by_day_average):
            while len(used_list) < len(by_day_average):
                used_list.append(np.nan)
        if len(dates) > len(by_day_average):
            by_day_average = by_day_average.reindex(dates.index)
        by_day_average[i] = dates
        strname = i + "Used"
        by_day_average[strname] = used_list
    return by_day_average


def used_per_studio(df, s):
    by_studio_average = pd.DataFrame(columns=['Studio', 'Used'])
    for i, a in enumerate(s):
        studio = df[df['Studio'] == a]
        sum_studio = float((studio.groupby(studio['Studio'])['Hours'].agg('sum')))
        hours_total = 14 * len(studio)
        used = round(((sum_studio/hours_total)*100), 2)
        if used > 100: used = 100
        by_studio_average.loc[i] = [a, used]
    return by_studio_average


def week_of_studios(df, studios):
    used = pd.DataFrame(columns = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], index= studios)
    for i in studios:
        week = used_per_day(df, [i])
        week = week[['SundayUsed', 'MondayUsed', 'TuesdayUsed', 'WednesdayUsed', 'ThursdayUsed', 'FridayUsed', 'SaturdayUsed']]
        week.columns = week_names
        week = week.mean()
        used.loc[i] = week
    return used
