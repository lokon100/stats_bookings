# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 11:08:07 2023

@author: Skye
"""

def sub_hist_duration_activities1(df, use, temp):
    if use == False:
        return
    df = duration_activities_var(df)
    bins1 = [x * 1 for x in range(0, 15)][1:]
    ticks1 = [x*2 for x in range(0, 8)]
    activities_df = activities.sort_values(by=activities.index[0], ascending=False, axis=1)
    fig, axs = generate_subplots(len(activities.columns), (4, 5.5), True, row_wise=True)
    fig.suptitle("Subplot Hist of Duration Per Activity Type " + str(temp))
    i = 0
    for ax in axs.flat:
        x = df.index[df['Activity'] == activities_df.columns[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['Hours'], bins=bins1)
        ax.set_title(activities_df.columns[i])
        ax.set_xticks(ticks1)
        i += 1
    fig.supxlabel('Hours')
    fig.supylabel('Count')
    plt.savefig('filename.png')

    fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(5.5, 3.5), dpi=600, sharex=True, sharey='row')
    fig.suptitle("Subplot Hist of Duration Per Activity Type (Top 3 Uses) " + str(temp))
    i = 0
    for ax in axs.flat:
        x = df.index[df['Activity'] == activities_df.columns[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['Hours'], bins=bins1)
        ax.set_title(activities_df.columns[i])
        ax.set_xticks(ticks1)
        i += 1
    fig.supxlabel('Hours')
    fig.supylabel('Count')
    plt.savefig('filename.png')
    fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(5.5, 3.5), dpi=600, sharex=True, sharey='row')
    fig.suptitle("Subplot Hist of Duration Per Activity Type (Lesser 3 Uses) "  + str(temp))
    for ax in axs.flat:
        x = df.index[df['Activity'] == activities_df.columns[i]].tolist()
        y = df[df.index.isin(x)]
        ax.hist(y['Hours'], bins=bins1)
        ax.set_title(activities_df.columns[i])
        ax.set_xticks(ticks1)
        i += 1
    fig.supxlabel('Hours')
    fig.supylabel('Count')
    plt.savefig('filename.png')


def hist_dur_studio1(df, use, temp):
    if use == False:
        return
    bins1, ticks1 = calc_bins_ticks(df['Hours'], 0.5)
    plt.figure(dpi = 600)
    plt.xticks(ticks1)
    plt.hist(df['Hours'].dropna(), bins=bins1)
    plt.ylim(0, 101)
    plt.xlabel("Hours", size=14)
    plt.ylabel("Count", size=14)
    plt.title("Histogram of Hours Per Studio" + str(temp))
    plt.savefig('filename.png')



temp = ['1-1', '1-2']
df_temp = df[df['Studio'].isin(temp)]
sub_hist_duration_activities1(df_temp, True, temp)

temp = ['2-1', '2-2', '2-3', '2-4', '2-5']
df_temp = df[df['Studio'].isin(temp)]
sub_hist_duration_activities1(df_temp, True, temp)

temp = ['3-1', '3-2', '3-3']
df_temp = df[df['Studio'].isin(temp)]
sub_hist_duration_activities1(df_temp, True, temp)

temp = ['4']
df_temp = df[df['Studio'].isin(temp)]
sub_hist_duration_activities1(df_temp, True, temp)

temp = ['3-4']
df_temp = df[df['Studio'].isin(temp)]
sub_hist_duration_activities1(df_temp, True, temp)
hist_dur_studio1(df_temp, True, temp)


import july
from july.utils import date_range
