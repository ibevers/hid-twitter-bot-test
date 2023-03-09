"""
Does the following:
1. Retrieve all new tweets from Twitter containing a trending keyword
2. Using the tweet metadata and a premade Model will analyze every user and predict if they are a bot or not.
3. Will update a Google spreadsheet with these predictions
"""

#Library
from ctypes import pointer
import time
from token import NUMBER
from tokenize import String
from types import NoneType
from urllib import request

#Third-party
import pandas as pd
from datetime import datetime
import calendar

#Local
import scripts.sheets as sheets
import scripts.retrieve.charles.download_tweets as dt
import scripts.retrieve.tweets as rt

CLIENT_SECRET_FILE = ""
DATABASE_SPREADSHEET_NAME = "twitter_bot_database"
AVERAGE_SHEET_NAME = "average"
SHEETS_RATE_LIMIT = 300 #requests per minute project, individuals: 60
TWITTER_RATE_PERIOD = 15 #minutes
TWEETS_PER_RATE_PERIOD = 180 #for applications, individuals: 180, v1.1 API
COLLECTION_PERIOD = 60 #minutes
N_TWEETS = 20 #per update
COLLECTION_WINDOW = 7 #days
MINS_IN_HR = 60
SAMPLES_PER_HOUR = MINS_IN_HR/TWITTER_RATE_PERIOD
TOP_TRENDS_COUNT = 1 #top n Twitter trends
HOURS_IN_DAY = 24
SAMPLES_PER_WINDOW = int(MINS_IN_HR/TWITTER_RATE_PERIOD * HOURS_IN_DAY *COLLECTION_WINDOW)
#672 assuming 15 min collection windows ^^
AVG_SHEET_RANGE = "A2:N" + str(SAMPLES_PER_WINDOW + 1) 
SEC_IN_MIN = 60
SHEET_COLS_N = 3
ROW_NAMES = ["date_created", "all_tweets", "bot_tweets"]

def set_keyword_ranges(num_words, num_rows):
    # Not set up yet for 8+ keywords. Would loop over alphabet and need to improve this function.
    # Want the format to be ['A3:CXX', 'E3:GXX',...]
    last_row = str(3 + (num_rows - 1))
    range_list = []
    for i in range(num_words):
        entry = chr(i*4+65) + '3:' + chr(i*4+2+65) + last_row
        range_list.append(entry)
    return range_list

def init_dataframes(trending_words, batch_start_time, time_inc, num_rows):
    # create a dict of dataframes. Fill with 0's
    # Columns and descriptions:
    #   Time: Time of tweets. If row 0 has time 12:00:00 and row 1 has time 12:15:00,
    #         all tweets between 12:00:00 and 12:14:59 will aggregate in row 0
    #   Total: The total number of tweets in the corresponding time batch
    #   Bots: The number of tweets that are from bots in the time batch
    blank_df = pd.DataFrame({'Time': pd.date_range(start=batch_start_time, periods=num_rows, freq=str(time_inc) + 'S'),
                             'Total': 0,
                             'Bots': 0})
    blank_df.loc[:, 'Time'] = blank_df['Time'].dt.tz_localize('UTC')
    df_dict = {}
    for keyword in trending_words:
        df_dict[keyword] = blank_df.copy()
    return df_dict

def get_ranks_to_names(trend_dict:dict) -> dict:
    """
    Creates a dictionary of top trend ranks to their names.
    """
    trend_rank_name_dict = {}
    for name in trend_dict.keys():
        rank = trend_dict[name]["rank"]
        trend_rank_name_dict[rank] = name
    return trend_rank_name_dict

def sheet_update_rank_changed(rank:int, sheet:str, trends_sheet_list:list[dict], changed_rank_sheets:set[dict]) -> None:
    """
    Updates sheets that have changed rank but are still in the top trends.
    """
    dataframe = pd.DataFrame(sheet.get_all_records()) #move data to temp
    temp_sheet_i = int(rank) + TOP_TRENDS_COUNT
    trends_sheet_list[temp_sheet_i].clear()
    trends_sheet_list[temp_sheet_i].update(\
        [dataframe.columns.values.tolist()] + dataframe.values.tolist())
    changed_rank_sheets.add(int(rank))


def update_worksheets(trend_dict:dict, database:pointer) -> None:
    """ 
    Sheets correspond to rank. Sheets are never deleted, and their rank is never 
    changed so that the links to the charts are stable. Updates sheet names to 
    reflect the new trend data they contain. Clears data for all trends 
    that are no longer in the top five. Moves data for trends that changed rank to
    the sheet corresponding to their new rank. Adds historical data for trends that entered the 
    top five in this update period.

    Parameters:
        trend_names_to_queries_dict: a dictionary with name and query values from top trends
        database: a gspread object that provides access to the database
    """
    trend_rank_name_dict = get_ranks_to_names(trend_dict)
    trends_sheet_list = database.worksheets() #sheets in as shown
    changed_rank_sheets = set({})
    for sheet in trends_sheet_list[1:1 + TOP_TRENDS_COUNT]:
        rank, name = sheet.title.split('___')
        if name == trend_rank_name_dict[rank] and rank == trend_dict[name]["rank"]: #no rank change
            pass 
        else:
            if name in trend_dict.keys() and rank != trend_dict[name]["rank"]: #rank changed
                sheet_update_rank_changed(rank, sheet, trends_sheet_list, changed_rank_sheets)
            new_title = rank + '___' + trend_rank_name_dict[rank]
            sheet.update_title(new_title)
            sheet.clear() #clear old data--will clear deranked trends
    for i in changed_rank_sheets: #move data from temp sheets
        dataframe = pd.DataFrame(trends_sheet_list[i + TOP_TRENDS_COUNT].get_all_records()) 
        trends_sheet_list[i].update(\
                    [dataframe.columns.values.tolist()] + dataframe.values.tolist())

def update_trend_sheets(time_stamp:datetime, database:pointer, trend_dict:dict, all_values:list[list], human_values:list, bot_values:list) -> datetime:
    """
    Adds a batch of data to the individual and average trend sheets.
    """
    for i, name in enumerate(trend_dict.keys()): #update trend sheet data
        query = trend_dict[name]["query"]
        agent_analysis_df = dt.download_recent_tweets(keyword=query, n_tweets=N_TWEETS)
        try:
            created_at = agent_analysis_df.iloc[:,0]
            time_stamp = created_at.index.T[0]
            values = agent_analysis_df.head(1).values.tolist()[0]
            all_values.append(values[0])
            human_values.append(values[0] - values[1])
            bot_values.append(values[1])
            values.insert(0, str(time_stamp))
            trend_sheet = database.worksheet(trend_dict[name]['rank'] + '___' + name)
            trend_sheet.append_row(values)
        except:
            pass
        assert all_values != human_values + bot_values, "Arithmetic bug " + str(all_values) + '!= ' + str(human_values) + ' + ' + str(bot_values)
    return time_stamp

def create_date_display(time_stamp:datetime, sheet_state:list[list]):
    """
    Formats the date string entered in the sheet as either "[month abbrev. (e.g. Aug)] [day]" or "[hour].

    This method is problematic when dates are discontinuous. We need a better approach in that case. 

    To-do: 
    -Decide on date format
    """
    hour = time_stamp.hour
    month = time_stamp.month
    day = time_stamp.day
    time_string = ""
    month_str_to_num_dict = {index: month for index, month in enumerate(calendar.month_abbr) if month}
    last_time_entry = ""
    try:
        last_time_entry = int(sheet_state[-1][0][0]) #the first letter
    except:
        last_time_entry = sheet_state[-1][0]
    if type(last_time_entry)==str:
        if last_time_entry == "":
            time_string = month_str_to_num_dict[month] + " " + str(day)
        elif int(last_time_entry[-1]) != day:
           time_string = month_str_to_num_dict[month] + " " + str(day) 
    elif type(last_time_entry)==int:
        if len(sheet_state)==0 or hour%HOURS_IN_DAY== 0 or last_time_entry - hour > 1:
            time_string = month_str_to_num_dict[month] + " " + str(day)
        else:
            return str(hour) + ":00"

    #Can I assume continuity?
        #No
    #in case the dates are not contiguous
    #conditions for using the month
        #dates not coniguous
            #not same
            #not same -1
            #
            #case wahere previous is text nad not continuous - ignore
                #in other words, if the previous is text, just do the time
    #first date OR contiguous and mod 24 OR not contiguous
        #Month Day
    #else
        #hour
    return time_string 

def update_average_sheet(time_stamp, database, trend_dict, all_values, human_values, bot_values):
    """
    Handles updating of the average sheet, which includes special cases like discontinuos dates.
    """
    avg_sheet = database.worksheet(AVERAGE_SHEET_NAME)
    sheet_state = avg_sheet.get(AVG_SHEET_RANGE)
    if len(sheet_state) == SAMPLES_PER_WINDOW: #remove first row data
        sheet_state = sheet_state[1:]
    all_mean = sum(human_values)/len(human_values)
    bot_mean = sum(bot_values)/len(bot_values)
    bot_proportion = 0
    if all_mean != 0:
        bot_proportion = bot_mean/all_mean
    elif bot_mean != 0:
        bot_proportion = 1.0
    time_string = create_date_display(time_stamp, sheet_state)
    new_row = [time_string] + human_values + bot_values + [all_mean] + [bot_mean] + [bot_proportion]
    sheet_state.append(new_row)
    new_sheet_state = []
    for row in sheet_state:
        row = [row[0]] + [int(x) for x in row[1:11]] + [float(x) for x in row[11:]]
        new_sheet_state.append(row)
    database.values_update(
        "average!" + AVG_SHEET_RANGE,
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values':new_sheet_state
        }
    )

def write_batch_to_sheets(database, trend_dict):
    """
    Gets a summary of the bot activity for the period of the form 
    (date, all_tweets, bot_tweets). Updates both the trend sheet and the
    average data sheet
    """
    time_stamp = ""
    all_values = []
    human_values = []
    bot_values = []
    time_stamp = update_trend_sheets(time_stamp, database, trend_dict, all_values, human_values, bot_values)
    update_average_sheet(time_stamp, database, trend_dict, all_values, human_values, bot_values)
    #avg_sheet.update(AVG_SHEET_RANGE, sheet_state)
    #avg_sheet.format("B2", { "numberFormat": { "type": "NUMBER","pattern": "#,##0" }})
    # { 
    #     "userEnteredFormat":{
    #         "type": "NUMBER",
    #         "pattern": "#.##"
    #     }
    # })
    #avg_sheet.format("L2:N673", {{
    #    "type": enum (NUMBER),
    #    "pattern": string
    #}})
    hi = 1

def main():
    """
    """
    assert TWITTER_RATE_PERIOD/COLLECTION_PERIOD*TOP_TRENDS_COUNT*N_TWEETS < TWEETS_PER_RATE_PERIOD, "You cannot collect tweets at this rate"
    database = sheets.get_database(DATABASE_SPREADSHEET_NAME)
    count = 1
    while True:
    # Charles: Not sure if there are any issues keeping the connection to the google sheet open for a long period.
    # Charles: Have not come across anything in limited research. If there is an issue and connection gets lost,
    # Charles: will need to set up some check or loop for this.
    #google_sheet = get_sheet_from_drive()
        top_trends = rt.get_top_trends()
        trend_dict = rt.get_trend_dict(TOP_TRENDS_COUNT, top_trends)
        update_worksheets(trend_dict, database)
        write_batch_to_sheets(database, trend_dict)
        print(str(count) + " database updates completed")
        count += 1
        timeout_period = COLLECTION_PERIOD * SEC_IN_MIN
        time.sleep(timeout_period)

if __name__=='__main__':
    main()