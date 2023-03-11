"""
Does the following:
1. Retrieve all new tweets from Twitter containing a trending keyword
2. Using the tweet metadata and a premade Model will analyze every user and predict if they are a bot or not.
3. Will update a Google spreadsheet with these predictions
"""

#Library
import time

#Third-party
from datetime import datetime

#Local
import scripts.sheets as sheets
import scripts.retrieve.charles.download_tweets as dt
import scripts.retrieve.tweets as rt

#multiple mode constants
DATABASE_SPREADSHEET_NAME = "twitter_bot_database"
SHEETS_RATE_LIMIT = 300 #requests per minute project, individuals: 60
TWITTER_RATE_PERIOD = 15 #minutes
TWEETS_PER_RATE_PERIOD = 180 #for applications, individuals: 180, v1.1 API

COLLECTION_PERIOD = 6 * 60 #minutes
N_TWEETS = 100 #per update
COLLECTION_WINDOW = 7 #days
MINS_IN_HR = 60
SAMPLES_PER_HOUR = MINS_IN_HR/TWITTER_RATE_PERIOD
TOP_TRENDS_COUNT = 1 #top n Twitter trends
HOURS_IN_DAY = 24
SEC_IN_MIN = 60

def write_batch_to_sheets(database, trend_dict):
    """
    Updates the database with a batch of tweets
    """
    for name in trend_dict.keys(): #update trend sheet data
        query = trend_dict[name]["query"]
        agent_analysis_df = dt.download_recent_tweets(keyword=query, n_tweets=N_TWEETS)
        created_at = agent_analysis_df.iloc[:,0]
        time_stamp = created_at.index.T[0]
        values = agent_analysis_df.head(1).values.tolist()[0]
        values.insert(0, name)
        values[1] = values[1] - values[2] #calculate n human
        database = database.worksheet("database")
        if database.row_count >= 30: #if length of sheet == 30
            data = database.batch_get( ('A2:C10',) )[0]
            database.batch_update([{
                'range': 'A1:C9',
                'values': data,
            }, {
                'range': 'A10:C10',
                'values': [values],
            }], value_input_option="USER_ENTERED")
        else:
            database.append_row(values)
    return time_stamp

def main():
    assert TWITTER_RATE_PERIOD/COLLECTION_PERIOD*TOP_TRENDS_COUNT*N_TWEETS < TWEETS_PER_RATE_PERIOD, "You cannot collect tweets at this rate"
    database = sheets.get_database(DATABASE_SPREADSHEET_NAME)
    count = 1
    while True:
        try: #to ensure it doesn't stop running
            top_trends = rt.get_top_trends()
            trend_dict = rt.get_trend_dict(TOP_TRENDS_COUNT, top_trends)
            write_batch_to_sheets(database, trend_dict)
            print(str(count) + " database updates completed")
            count += 1
            print("sleeping for " + str(COLLECTION_PERIOD) + " minutes")
            time.sleep(COLLECTION_PERIOD * SEC_IN_MIN)
        except:
            print("Likely API issue: sleeping for " + str(MINS_IN_HR) + " minutes")
            time.sleep(MINS_IN_HR * SEC_IN_MIN)

if __name__=='__main__':
    main()
