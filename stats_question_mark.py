# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 13:34:04 2022

@author: Skye
"""

import pandas as pd
import numpy as np

from variable_work import bookings, names_unique, studio_name, studio_type, week_names, weekday, weekend, list_length, activities, equipment, sources, sources_count  # analysis:ignore

df = bookings.copy()


# %% Bookers
"""Bookers, number and duration"""


def bookers(df, names_bool, top_names_bool):
    """getting the number of bookings and duration per person"""
    df = df[['Name', 'Hours']]
    df = df.groupby('Name').agg(['count', 'sum']).droplevel(0, axis=1)
    length = len(df)
    if names_bool == True:
        for i in range(length):
            print(df.index[i] + "\t" + str(df.loc[i, 'count']) +
                  "\t" + str(bookers.loc[i, 'sum']))
    sorted_names_bookings = (df.sort_values('count', ascending=False)).iloc[:10]
    sorted_names_hourly = (df.sort_values('sum', ascending=False)).iloc[:10]
    if top_names_bool == True:
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


# %% Studio Use
"""Studios, number of uses per studio and type"""


def studio_uses(df, name_type, print_bool):
    """adding up the total uses of studios"""
    studio_use = df[name_type].value_counts().sort_index(ascending=True)
    if print_bool == True:
        print("Total Uses Of Studios")
        for i in studio_use.index:
            print("Studio " + str(i) + "\t" + str(studio_use[i]))
    return studio_use


# %% Average Duration/Days Prev Of Bookings
"""Average duration/days prev of bookings, by studio, studio type, day of week and weekday/end"""


def average_per_studio(df, use, name_type, print_bool):
    """calculating average by studio
    use = (1) duration or (2) days prev, or (3) for both"""
    temp = df[[name_type, 'Hours', 'Days Prev']]
    studio_cols = temp.groupby(name_type).agg(['mean', 'sum'])
    studio_cols.columns = ['HMean', 'HSum', 'PMean', 'PSum']
    print_use = temp.groupby(name_type).agg(['mean']).droplevel(1, axis=1)
    if print_bool == True:
        if use == 1 or use == 3:
            print("Duration Average")
            for i in print_use.index:
                print(name_type + " " + str(i) + "\t" +
                      str(round(print_use.loc[i, 'Hours'], 2)))
        if use == 2 or use == 3:
            print("Days Prev Average")
            for i in print_use.index:
                print(name_type + " " + str(i) + "\t" +
                      str(round(print_use.loc[i, 'Days Prev'], 2)))
    return studio_cols


def average_per_day(df, use, print_bool):
    """calculating average by day of week
    use = (1) duration or (2) days prev, or (3) for both"""
    temp = df[['Day', 'Hours', 'Days Prev']]
    day_cols = temp.groupby('Day').agg(['mean', 'sum']).droplevel(0, axis=1)
    day_cols.columns = ['HMean', 'HSum', 'PMean', 'PSum']
    print_use = temp.groupby('Day').agg(['mean']).droplevel(1, axis=1)
    if print_bool == True:
        if use == 1 or use == 3:
            print("Duration Average")
            for i, a in enumerate(week_names):
                print(str(a) + "\t" + str(round(print_use.loc[a, 'Hours'], 2)))
        if use == 2 or use == 3:
            print("Days Prev Average")
            for i, a in enumerate(week_names):
                print(str(a) + "\t" + str(round(print_use.loc[a, 'Days Prev'], 2)))
    return day_cols


def average_week_end(df, use, print_bool):
    """calculating average by weekday/end
    use = (1) duration or (2) days prev, or (3) for both"""
    per_day = average_per_day(df, use, False)
    average_weekday = per_day[['HMean', 'PMean']].loc[weekday]
    weekday_calc = average_weekday.mean()
    average_weekend = per_day[['HMean', 'PMean']].loc[weekend]
    weekend_calc = average_weekend.mean()
    if print_bool == True:
        if use == 1 or use == 3:
            print("Duration Average")
            print("Weekday" + "\t" + "Duration: "
                  + str(round(weekday_calc.loc['HMean'], 2)))
            print("Weekend" + "\t" + "Duration: "
                  + str(round(weekend_calc.loc['HMean'], 2)))
        if use == 2 or use == 3:
            print("Days Prev Average")
            print("Weekday" + "\t" + "Days Prev: "
                  + str(round(weekday_calc.loc['PMean'], 2)))
            print("Weekend" + "\t" + "Days Prev: "
                  + str(round(weekend_calc.loc['PMean'], 2)))
    return average_weekday, average_weekend


def average_per_studio_per_day(df, use, print_bool):
    """calculating average by studio (type)
    index = (1) duration or (2) days prev, or (3) for both"""
    temp = df[['Studio', 'Day', 'Hours', 'Days Prev']]
    studio_cols = temp.groupby(['Studio', 'Day']).agg(
        ['mean', 'sum', 'count']).droplevel(0, axis=1)
    studio_cols.columns = ['DurMean', 'DurSum',
                           'DurCount', 'PrevMean', 'PrevSum', 'PrevCount']
    if print_bool == True:
        if use == 1 or use == 3:
            print("Average Duration")
            for i in studio_name:
                studio = studio_cols[['DurMean', 'DurSum', 'DurCount']].loc[i]
                print("\n" + "Studio " + i)
                print(round(studio, 2))
        if use == 1 or use == 3:
            print("\n Average Prev Days")
            for i in studio_name:
                studio = studio_cols[['PrevMean', 'PrevSum', 'PrevCount']].loc[i]
                print("\n" + "Studio " + i)
                print(round(studio, 2))
    return studio_cols


def average_count_per_day(df):
    temp = pd.DataFrame(index=df['Date of Activity'])
    temp = pd.DataFrame(temp.index.normalize().value_counts())
    temp.index = temp.index.day_name()
    temp1 = temp.groupby(temp.index).agg(['mean', 'sum']).droplevel(0, axis=1)
    temp1['mean'] = round(temp1['mean'], 2)
    temp1 = temp1.reindex(week_names)
    return temp1


# %% When Booked Most
"""When studios and types are booked the most"""


def making_one_day(df, day, name_type):
    """making one day list"""
    studio_day = df[['Day', name_type, 'Hours']]
    studio_day = studio_day.loc[studio_day['Day'] == day]
    studio_day = studio_day[[name_type, 'Hours']]  # for one weekday
    studio_day = studio_day.groupby([name_type]).agg(
        ['sum', 'count']).droplevel(0, axis=1)
    return studio_day


def studio_per_day(df, name_type, print_bool):
    """calculating per day most booked studio"""
    week_calc = pd.DataFrame(
        columns=['max studio', 'max hours', 'count studio', 'count bookings'])
    for day in week_names:
        day_studios = making_one_day(df, day, name_type)
        max_hours = day_studios['sum'].idxmax()
        max_bookings = day_studios['count'].idxmax()
        week_calc.loc[day] = [max_hours, day_studios['sum'][max_hours],
                              max_bookings, day_studios['count'][max_bookings]]
    if print_bool == True:
        for i in week_calc.index:
            print(str(i) + ":" + "\t" + "top by hour: Studio " + str(week_calc.loc[i, 'max studio']) + " " + str(
                week_calc.loc[i, 'max hours']) + "\t" + "top by booking: Studio " + str(week_calc.loc[i, 'count studio']) + " " + str(week_calc.loc[i, 'count bookings']))
    return week_calc


def studio_per_week_end(df, range_name, range_var, print_bool):
    """calculating by weekday and weekend most booked studio type"""
    days = studio_per_day(df, "Studio", False)
    week_series = days.loc[range_var]
    week_calc = pd.DataFrame(
        columns=['max studio', 'max hours', 'count studio', 'count bookings'])
    max_hours = week_series['max hours'].idxmax()
    max_bookings = week_series['count bookings'].idxmax()
    week_calc.loc[range_name] = week_series.loc[max_hours, 'max studio'],
    week_series.loc[max_hours, 'max hours'],
    week_series.loc[max_bookings, 'count studio'],
    week_series.loc[max_bookings, 'count bookings']
    if print_bool == True:
        print(range_name + ":" + "\t" + "top by hour: " + range_name + " "
              + week_calc.loc[range_name, 'max studio'] + " "
              + str(round(week_calc.loc[range_name, 'max hours'], 1))
              + "\t top by booking: " + range_name + " "
              + week_calc.loc[range_name, 'count studio'] + " "
              + str(round(week_calc.loc[range_name, 'count bookings'])))
    return week_calc


# %% Days Booked Most
"""Order of Days Booked Most"""


def order_days_booked(df, print_bool):
    days_booked = df[['Day', 'Hours']]
    days_bookings = pd.DataFrame(columns=['hours', 'bookings'])
    for day in week_names:
        day_of = days_booked.loc[days_booked['Day'] == day]
        days_bookings.loc[day] = [day_of['Hours'].sum(), day_of['Day'].count()]
    bookings_hours = (days_bookings.sort_values('hours', ascending=False))
    bookings_count = (days_bookings.sort_values('bookings', ascending=False))

    if print_bool == True:
        print("By hours booked: ")
        for i in bookings_hours.index:
            print(str(i) + " " + str(bookings_hours.loc[i, 'hours']))
        print("By number of bookings: ")
        for i in bookings_count.index:
            print(str(i) + " " + str(round(bookings_count.loc[i, 'bookings'])))
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
