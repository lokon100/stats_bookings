# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 15:26:05 2022

@author: Skye
"""

import pandas as pd
import numpy as np

"""file location; 1 is csv, 2 is xlsx"""
version = 1
file_location = 'C:/Users/Skye/Dropbox/Cre8ive Files/Daily Bookings Log (current).csv'

"""sifting values for overall filter"""
studio_list = []
use_studio = False

day_list = []
use_weekday = False

source_list = []
use_source = False

activity_list = []
use_activity = False

names = False
names_list = ['atlantic theater company', 'the pit', 'abigail m.']

pit = False

full_day = False

date_range = [(pd.to_datetime("January 1st 2023")), (pd.to_datetime("December 31st 2023"))]
use_date = False

days_advance_low = 0
days_advance_high = 0
use_advance_low = False
use_advance_high = False


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
    columns=['Exercise', 'Acting', 'Fashion', 'Activity', 'Religion', 'Office'])
temp_list = [['dance', 'yoga', 'meditation', 'martial', 'soloist', 'fight',
              'ballet', 'taekwondo', 'choreo', 'taichi', 'fitness', 'dancing', 'pilates',
              'salsa', 'practice', 'capoeira'],
             ['improv', 'comedy', 'acting', 'reading', 'cast', 'performance',
              'sketch', 'theater', 'read', 'sing', 'script', 'scene', 'callback', 'band',
              'audition', 'rehearsal', 'waiting room'],
             ['fitting', 'model', 'fashion', 'wardrobe', 'make up', 'costume'],
             ['audition', 'photo', 'video', 'film', 'shoot',
              'meetup', 'meet-up', 'meet up', 'event', 'art', 'shop', 'wedding',
              'craft', 'catwalk', 'movie', 'paint', 'game', 'headshot'],
             ['religious', 'prayer', 'church', 'service', 'worship', 'bible'],
             ['course', 'workshop', 'lesson', 'meeting', 'team', 'group', 'interview',
              'lecture', 'buisness', 'development', 'training', 'network', 'retreat',
              'summit', 'class', 'zoom', 'test', 'planning', 'interview', 'work',
              'working', 'call', 'market', 'buisness', 'study', 'presentation', 'offsite',
              'off-site', 'project', 'conference', 'session', 'mentor', 'therapy',
              'panel', 'discussion', 'distribution', 'office']]
activities = make_filter_lists(activities, temp_list)

equipment = pd.DataFrame(columns=['Default', 'Extra', 'Sound', 'Setup', 'Fashion'])
temp_list = [['chair', 'table'], ['projector', 'whiteboard', 'ring', 'light', 'tv'],
             ['speaker', 'music', 'sound', 'mic'], ['classroom', 'boardroom', 'circle'],
             ['changing', 'screen', 'rack', 'hangar']]
equipment = make_filter_lists(equipment, temp_list)
