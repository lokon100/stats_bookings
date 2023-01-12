# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 15:26:05 2022

@author: Skye
"""

import pandas as pd
import numpy as np

"""file location; 1 is csv, 2 is xlsx"""
version = 1
file_location = 'C:/Users/Skye/Dropbox/Cre8ive Files/Python/Booking Stats/v1.0/Daily Bookings Log.csv'

"""sifting values for overall filter"""
studio_list = []
use_studio = False

day_list = []
use_weekday = False

source_list = []
use_source = False

activity_list = []
use_activity = False

atlantic = False

pit = False

full_day = False

date_range = [(pd.to_datetime("August 1st 2022")), (pd.to_datetime("October 23rd 2023"))]
use_date = False

days_advance_low = 0
days_advance_high = 0
use_advance_low = True
use_advance_high = True


# %% filtering lists

def make_filter_lists(df, array):
    for i, a in enumerate(array):
        if len(a) < len(df):
            while len(a) < len(df):
                a.append(np.nan)
        if len(a) > len(df.index):
            df = df.reindex(list(range(len(a))))
        df.iloc[:, i] = a
    return df


activities = pd.DataFrame(
    columns=['Exercise', 'Acting', 'Fashion', 'Activity', 'Buisness', 'Religion'])
temp_list = [['dance', 'rehearsal', 'yoga', 'meditation', 'martial', 'soloist', 'fight',
              'ballet', 'taekwondo', 'choreo'],
             ['improv', 'rehearsal', 'comedy', 'acting', 'reading', 'cast', 'performance',
              'sketch'],
             ['fitting', 'model', 'fashion'],
             ['workshop', 'lesson', 'audition', 'photo', 'video', 'film', 'shoot',
              'course', 'meetup', 'meet-up', 'event', 'art', 'shop', 'wedding', 'craft'],
             ['meeting', 'team', 'group', 'interview', 'lecture', 'buisness',
              'development', 'training', 'network', 'retreat', 'summit'],
             ['religious', 'prayer', 'church', 'service']]
activities = make_filter_lists(activities, temp_list)

equipment = pd.DataFrame(columns=['Default', 'Extra', 'Sound', 'Setup', 'Fashion'])
temp_list = [['chair', 'table'], ['projector', 'whiteboard', 'ring', 'light', 'tv'],
             ['speaker', 'music', 'sound', 'mic'], ['classroom', 'boardroom', 'circle'],
             ['changing', 'screen', 'rack', 'hangar']]
equipment = make_filter_lists(equipment, temp_list)
