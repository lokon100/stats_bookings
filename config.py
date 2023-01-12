# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 15:26:05 2022

@author: Skye
"""

import pandas as pd  # analysis:ignore
import numpy as np

"""file location; 1 is csv, 2 is xlsx"""
version = 1
file_location = 'C:/Users/Skye/Dropbox/Cre8ive Files/Python/Booking Stats/v0.1/Daily Bookings Log (current).csv'

"""sifting values for overall filter"""
filter_on = False

atlantic = True
pit = True
full_day = False
use_date = False
date_range = [(pd.Timestamp("September 1st 2022")).to_pydatetime(),
              (pd.Timestamp("January 23rd 2023")).to_pydatetime()]
days_advance_low = 0
days_advance_high = 0
source_filter = False # options: Direct Giggster Liquidspace Peerspace Skedda Spacebase Splacer Tagvenue Walk-In
activity_filter = False # options: Exercise, Acting, Fashion, Activity, Buisness, Religion

"""to use filters set booleans to False or input times/dates"""



"""setting up activity and equipment lists"""


# %%
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
