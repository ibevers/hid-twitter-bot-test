import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pickle
import pandas as pd

from dateutil.parser import parse
from datetime import datetime

import os
from os import listdir
from os.path import isfile, join

import utilities as util
from create_model_features import create_feature_df

from time import sleep
verbose = True

def analyze(df, bot_ids, human_ids, keyword):
    # keyword = input_folder.split('\\')[-1]
    # # ----------------------- Retrieve and verify existence of 1 database in given folder -----------------------
    # db_filename = db_files[0]
    # file_date = db_filename.split('.')[0]  # Will be used for some save names
    # ----------------------- Load Tweet Data -----------------------

    # ----------------------- Get Statistics -----------------------
    # Tweets
    bot_tweets = df['Bot_Tweets'].sum()
    total_tweets = df['Total_Tweets'].sum()
    human_tweets = total_tweets - bot_tweets

    # Users
    bot_users = len(bot_ids)
    human_users = len(human_ids)
    total_users = human_users + bot_users

    # Dataset Info
    first_day = df.index[0].strftime('%b %d')
    last_day = df.index[-1].strftime('%b %d')

    # Create a dataframe column of hourly dates between the first and last tweet
    first_hour = df.index.values[0]
    last_hour = df.index.values[-1]
    hourly_df = pd.DataFrame(
        {'Time': pd.date_range(first_hour, last_hour, freq='1H', closed='left')}
    )
    # Merge the two dataframes. This guarantees we do not skip an hour if there are no tweets.
    plotting_df = df.reset_index(drop=False)
    plotting_df['created_at_hour'] = pd.to_datetime(plotting_df['created_at_hour'], utc=True)
    hourly_df['Time'] = pd.to_datetime(hourly_df['Time'], utc=True)
    plotting_df = plotting_df.merge(hourly_df, how='right', left_on='created_at_hour', right_on='Time', sort=True,
                                    copy=True)
    plotting_df = plotting_df.drop(columns=['created_at_hour'])

    # Prep the plotting dataframe for plotting
    plotting_df = plotting_df.sort_values(by=['Time'])
    plotting_df['Hour'] = plotting_df['Time'].dt.strftime('%b %d, %I %p')
    plotting_df['Day'] = plotting_df['Time'].dt.strftime('%b %d')

    # Indices for the zoomed in plot
    max_total_tweet_idx = plotting_df['Total_Tweets'].idxmax()
    max_total_hour = plotting_df.iloc[max_total_tweet_idx]['Hour']
    max_bot_tweet_idx = plotting_df['Bot_Tweets'].idxmax()
    max_bot_hour = plotting_df.iloc[max_bot_tweet_idx]['Hour']
    lower_index = max(min(max_total_tweet_idx - 2, max_bot_tweet_idx - 2), 0)
    upper_index = min(max(max_total_tweet_idx + 2, max_bot_tweet_idx + 2), plotting_df.shape[0] - 1)
    # Convert the index to the hour.
    plotting_df = plotting_df.set_index('Hour')

    # Create the zoomed_df as a subset of the plotting_df
    zoomed_df = plotting_df.iloc[lower_index:upper_index + 1]

    # ----------------------- Set up the basic plot -----------------------
    with sns.axes_style('darkgrid'):
        fig, ax = plt.subplots()

    sns.color_palette("tab10")
    sns.lineplot(data=plotting_df)
    plt.xticks(rotation=20)
    plt.fill_between(plotting_df.index, plotting_df.Total_Tweets, alpha=0.7)
    plt.fill_between(plotting_df.index, plotting_df.Bot_Tweets, alpha=0.7)
    plt.ylabel('Number of Hourly Tweets')
    plt.title(f'{keyword} Tweets from {first_day} to {last_day}')

    legend = plt.legend()
    frame = legend.get_frame()
    frame.set_facecolor('white')

    # Unfortunately redundant code to remove a 'FixedFormatter' warning.
    # Ideally the commented line below would have no warning.
    # ax.set_xticklabels(plotting_df.Day)
    ticks_loc = ax.get_xticks()
    ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
    ax.set_xticklabels(ax.set_xticklabels(plotting_df.Day.values))

    for n, label in enumerate(ax.xaxis.get_ticklabels()):
        true_label = plotting_df.index[n]
        # if '12 AM' not in true_label and n != 0:
        if '12 AM' not in true_label:
            label.set_visible(False)
    # ----------------------- Saving basic plot -----------------------
    file_date = last_day.replace(' ', '-')
    plt.savefig('../' + keyword + '/' + 'basic_trend-' + file_date + ".png")
    # ----------------------- Set up the zoomed plot -----------------------
    with sns.axes_style('darkgrid'):
        fig, ax = plt.subplots()

    sns.color_palette("tab10")
    sns.lineplot(data=zoomed_df)
    plt.xticks(rotation=20)
    plt.fill_between(zoomed_df.index, zoomed_df.Total_Tweets, alpha=0.7)
    plt.fill_between(zoomed_df.index, zoomed_df.Bot_Tweets, alpha=0.7)

    plt.ylabel('Number of Hourly Tweets')
    plt.title(f'{keyword} Tweets from {first_day} to {last_day}')

    legend = plt.legend()
    frame = legend.get_frame()
    frame.set_facecolor('white')

    # Unfortunately redundant code to remove a 'FixedFormatter' warning.
    # Ideally the commented line below would have no warning.
    # ax.set_xticklabels(zoomed_df.Day)
    ticks_loc = ax.get_xticks()
    ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
    ax.set_xticklabels(ax.set_xticklabels(zoomed_df.Day.values))

    plt.axvline(x=max_total_hour, ls='--', color='black', label=max_total_hour)
    plt.text(max_total_hour, ax.get_ybound()[1]*3/4, max_total_hour)
    plt.axvline(x=max_bot_hour, ls='--', color='red', label=max_bot_hour)
    plt.text(max_bot_hour, ax.get_ybound()[1]/2, max_bot_hour)

    for n, label in enumerate(ax.xaxis.get_ticklabels()):
        true_label = zoomed_df.index[n]
        # if '12 AM' not in true_label and n != 0:
        if '12 AM' not in true_label:
            label.set_visible(False)
    # ----------------------- Saving zoomed plot -----------------------
    plt.savefig('../' + keyword + '/' + 'zoomed_trend-' + file_date + ".png")
    # ----------------------- Save basic statistics -----------------------
    file2write = open('../' + keyword + '/' + 'basic_stats-' + file_date + ".txt", 'w')
    file2write.write(f"------------------ Background Info ------------------ \n")
    file2write.write(f"First day of data: {'-'.join(first_day.split(' '))} \n")
    file2write.write(f"Last day of data: {'-'.join(last_day.split(' '))} \n \n")

    file2write.write(f"------------------ Tweet Info ------------------ \n")
    file2write.write(f"Number of total tweets: {total_tweets}   ->  100.00% \n")
    file2write.write(f"Number of human tweets: {human_tweets}   ->  {round(100 * human_tweets / total_tweets, 2)}% \n")
    file2write.write(f"Number of bot tweets: {bot_tweets}   ->  {round(100 * bot_tweets / total_tweets, 2)}% \n \n")

    file2write.write(f"------------------ User Info ------------------ \n")
    file2write.write(f"Number of total users: {total_users}   ->  100.00% \n")
    file2write.write(f"Number of human users: {human_users}   ->  {round(100 * human_users / total_users, 2)}% \n")
    file2write.write(f"Number of bot users: {bot_users}   ->  {round(100 * bot_users / total_users, 2)}% \n \n")
    file2write.close()

if __name__ == "__main__":
    keyword = 'chess'
    Model = 'Bot_Model_1'
    external_load_path = 'D:/Saved_Data/Python_Files/PycharmProjects/Twitter_Bot_Files/data/processed/tweets_by_topic/' + keyword + '/'
    analysis(input_folder=external_load_path, model_name=Model)
