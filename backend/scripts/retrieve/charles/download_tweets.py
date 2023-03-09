
# Standard library imports
import time
from datetime import datetime
import os
import pickle

# Third-party imports
import requests
import pandas as pd
import numpy as np
import botometer

#Local application imports
import scripts.retrieve.charles.utilities as util
import scripts.retrieve.charles.create_model_features as cmf
import credentials.twitter_cred as keys

#os.system("export PYTHONPATH='${PYTHONPATH}:'/Users/isaacbevers/humanid/twitter-bot-activity-website/backend")
#import scripts.retrieve.charles.create_model_features

CONSUMER_KEY = keys.CONSUMER_KEY
CONSUMER_SECRET = keys.CONSUMER_SECRET_KEY
ACCESS_TOKEN = keys.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = keys.ACCESS_TOKEN_SECRET
BEARER_TOKEN = keys.BEARER_TOKEN
MODEL_PATH = "backend/scripts/retrieve/charles/Bot_Model_1.sav"
THRESHOLD = 0.5
twitter_app_auth = {
    'consumer_key': 'zzYIMt2JmFdwZWK2qRrEcWL75',
    'consumer_secret': 'Cj5CX5b3o9fJIHWaTexZ3ERSW6rMNFRtbpKTVvUrEjGFQeuXiB',
    'access_token': '1088230607870705664-TnpsNV7xT3FrtVqShf2azzXdSkVj27',
    'access_token_secret': '9GF8JT3EsG942VRJQPdCNZRg7vQO7Iq8NhL45A263rBab',
}
rapidapi_key = '04c96be8b9msh30a2b8957700538p155b9djsn37aef731713b'
bom = botometer.Botometer(wait_on_ratelimit=True, rapidapi_key=rapidapi_key, **twitter_app_auth)

def auth():
    return BEARER_TOKEN

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def get_recent_tweets(bearer_token=BEARER_TOKEN, topic='nasa', max_id = None, n_tweets=5):
    # "Subtract 1 from the lowest Tweet ID returned from the previous request and use this for the value of max_id.
    # It does not matter if this adjusted max_id is a valid Tweet ID, or if it corresponds with a Tweet posted by
    # a different user - the value is just used to decide which Tweets to filter."
    # 100 is the max as of Feb 3, 2021

    url = f'https://api.twitter.com/1.1/search/tweets.json?q={topic}&result_type=recent&count={n_tweets}'
    if max_id != None:
        url = url + f'&max_id={str(max_id)}'
    headers = create_headers(bearer_token)
    json_response = connect_to_endpoint(url, headers)
    return json_response

def dict_flatten(d, parent_key='', sep='_'):
    # https: // stackoverflow.com / questions / 6027558 / flatten - nested - dictionaries - compressing - keys
    items = []

    # loop for dictionaries
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, (dict, list)):
                items.extend(dict_flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))

    # loop for lists
    elif isinstance(d, list):
        for element in d:
            if isinstance(element, dict):
                items.extend(dict_flatten(element, parent_key, sep=sep).items())
            else:
                items.append((parent_key, d))
                # print("How'd I get here?")
    return dict(items)

def rate_limit_compliance(time_data=None, type='timeline', verbose=False):
    # Rate limits from https://developer.twitter.com/en/docs/twitter-api/

    # Occasional delay to be applied to prevent exceeding rate limit.
    # Just a saftey margin that makes us not have to check every single iteration for rate limits.
    safety_delay = 30  # seconds

    # Rate and Limits need to match up.
    # For instance the timeline first limit of 100000 corresponds to its first rate of 60*60*24.
    rate_dict = {'timeline': {'rates': [60*60*24, 60*15], 'limits': [100000, 1500]},
                 'tweets': {'rates': [60*15], 'limits': [450]},
                 'user_lookup': {'rates': [60*15], 'limits': [900]},
                 'test': {'rates': [4, 60, 100], 'limits': [2, 5, 7]}}  # Just used for testing purposes

    # First time through
    max_limit = max(rate_dict[type]['limits'])
    if time_data == None:
        requests_performed = 1
        time_list = np.zeros(max_limit-1)
        time_list[0] = time.time()
        start_time = time_list[0]

        # Just a wrapper for the 3 objects to be returned every time: requests_performed, time_list, and start_time
        time_data = [requests_performed, time_list, start_time]
        return time_data

    # Unpack the list
    requests_performed, time_list, start_time = time_data

    # Cycle through each pair of rate and limit to verify we meet rate limit compliance. If not, delay.
    for rate, limit in zip(rate_dict[type]['rates'], rate_dict[type]['limits']):
        cur_time = time.time()
        # this calculation still works when we have not reached the larger limits
        # because the default time value is 0 corresponding to the year 1970
        compare_time_entry = (requests_performed - (limit - 1)) % (max_limit-1)
        elapsed_time = cur_time - time_list[compare_time_entry]
        if elapsed_time < rate + safety_delay:
            time_delay = (rate - elapsed_time) + 2*safety_delay
            if verbose:
                print(f"\nA Twitter rate limit has been reached. The program has been paused for {round(time_delay/60, 2)} minutes.")
            time.sleep(time_delay)
            if verbose:
                print(f"The program has been unpaused.")

    time_list_entry = requests_performed % (max_limit-1)
    time_list[time_list_entry] = time.time()

    # Increment the number of requests performed
    requests_performed = requests_performed + 1

    time_data = [requests_performed, time_list, start_time]
    return time_data

def current_progress(starting_time, oldest_time):
    '''
    :param starting_time: the first tweet time gathered. Will be roughly when the program is launched.
    :param oldest_time: most recent tweet received. will be older than starting_time
    :return: total_progress in terms of percent
    '''
    # We can retrieve tweets over 1 week (and ~a day). that corresponds to the seconds below.
    max_seconds = 60*60*24*8
    dt_format = '%a %b %d %H:%M:%S %z %Y'
    st = datetime.strptime(starting_time, dt_format)
    ot = datetime.strptime(oldest_time, dt_format)

    total_progress = (st-ot)/max_seconds/pd.Timedelta(seconds=1)
    return 100*total_progress

def printProgressBar(percent, prefix = '', suffix = '', length = 80, fill = '█', printEnd = ""):
    percent_dec = round(percent/100, 3)
    filledLength = int(length * percent_dec)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {round(percent, 2)}% {suffix}', end = printEnd)

def download_recent_tweets(keyword = None, n_tweets=5):
    """
    accepts either a keyword(will expand to accept multiple later), or a hashtag(never implemented actually).
    """

    load_path = MODEL_PATH
    loaded_model = pickle.load(open(load_path, 'rb'))

    rate_type = 'tweets'
    batch_size = 10
    progress_frequency = 2
    verbose = False
    rate_limit_verbose = True

    bearer_token = auth()
    date_str = datetime.now().strftime("%m-%d-%Y")

    tweets_list = []
    overall_df = pd.DataFrame()
    human_id_set = set()
    bot_id_set = set()
    time_data = None
    min_id = None
    starting_time = None
    printProgressBar(0)
    try:
        # Ensure properly following Twitter API rate limits
        time_data = rate_limit_compliance(type=rate_type, verbose=rate_limit_verbose)
        raw_tweets = get_recent_tweets(bearer_token, topic=keyword, max_id=min_id, n_tweets=n_tweets)

        # with open('raw_tweets.py', 'rb') as read:
        #     obj = pickle.load(read)

        # with open('raw_tweets.py', 'wb') as temp:
        #     obj = pd.concat([obj, raw_tweets])
        #     pickle.dump(obj, temp)

        # with open('raw_tweets.pkl', 'wb') as temp:
        #     pickle.dump(raw_tweets, temp)

        # Convert the raw json to a list of dictionaries.
        cur_tweets = [dict_flatten(tweet) for tweet in raw_tweets['statuses']]
        # Then reduce each dictionary to just the features desired.
        reduced_cur_tweets = [{k: tweet.get(k, None) for k in util.ALL_PULLED_FEATURES} for tweet in cur_tweets]
        # Store the data in our growing list
        tweets_list.extend(reduced_cur_tweets)

        # First time we have results, store the first tweet time for the progress bar
        if starting_time == None:
            starting_time = tweets_list[0]['created_at']

        # set up the next search
        tweet_ids = [tweet['id'] for tweet in reduced_cur_tweets]
        min_id = min(tweet_ids) - 1

        if time_data[0]%progress_frequency == 0:
            cp = current_progress(starting_time=starting_time, oldest_time=tweets_list[-1]['created_at'])
            printProgressBar(cp)
        # Save in Batches of 10*100 tweets and reset tweet_list to limit memory
        if time_data[0]%batch_size == 0:

            # Tweets from list -> DataFrame
            tweet_df = pd.DataFrame(tweets_list)
            tweets_list = []
            # Extract just the needed features for predicting, and the user_id for merging
            prediction_set = tweet_df[util.USER_PRED_FEATURES].copy()
            prediction_set.columns = util.PRED_FEATURES

            # If a user tweeted twice, they will be a duplicate here. No point in predicting them twice.
            prediction_set = prediction_set.drop_duplicates(subset=['id'])
            feature_df = cmf.create_feature_df(prediction_set)

            feature_df['oob_preds'] = loaded_model.predict(feature_df.drop(columns=['id']))
            # ----------------------- Merge the predictions with our Data -----------------------
            # rename id in feature_df to user_id
            feature_df = feature_df.rename(columns={"id": "user_id"})
            tweet_df = feature_df[['user_id', 'oob_preds']].merge(
                tweet_df, how='left', left_on='user_id', right_on='user_id')
            # ----------------------- Append human_ids and bot_ids to our sets  -----------------------
            bot_id_set.update(tweet_df[tweet_df['oob_preds'] == 1]['user_id'].values)
            human_id_set.update(tweet_df[tweet_df['oob_preds'] == 0]['user_id'].values)
            # ----------------------- Get the hour of each tweet -----------------------
            tweet_df['created_at_dt'] = pd.to_datetime(tweet_df['created_at'])
            tweet_df['created_at_hour'] = tweet_df['created_at_dt'].apply(lambda x: x.replace(minute=0, second=0))
            # ----------------------- Reduce to an aggregate df of just the hour and bot/total tweets -------------
            temp = tweet_df.groupby(['created_at_hour', 'oob_preds']).size().reset_index(name='Count').copy()
            temp_gps = temp.groupby(['created_at_hour'])
            batch_df = temp_gps.apply(lambda df, a: sum(df[a]), 'Count').to_frame(name="Total_Tweets")
            batch_df['Bot_Tweets'] = temp_gps.apply(lambda df, a, b: sum(df[a] * df[b]), 'oob_preds', 'Count')
            #  ----------------------- Append and combine this batch with the overall df -----------------------
            overall_df = overall_df.append(batch_df)
            overall_df = overall_df.groupby(overall_df.index).sum()

        # Check API rate limits and try getting the next batch of tweets
        #time_data = rate_limit_compliance(time_data=time_data, type=rate_type, verbose=rate_limit_verbose)
        #try:
        #    raw_tweets = get_recent_tweets(bearer_token, topic=keyword, max_id=min_id)
        #except Exception as e:
        #    error_num = str(e).split(',', 2)[0][1:]
        #    # Exceeded Twitter's rate limits. Investigate why if this occurs.
        #    if error_num == '429':
        #        print(f"\nBackup time delay used. A 15-minute pause has started to comply with Twitter rate limits.")
        #        time.sleep(15*60)
        #        print(f"The program has been unpaused.")
        #        time_data = rate_limit_compliance(time_data=time_data, type=rate_type, verbose=rate_limit_verbose)
        #        raw_tweets = get_recent_tweets(bearer_token, topic=keyword, max_id=min_id)
        #    else:
        #        print(f"Exiting Program. Error: {e}")
        #        raw_tweets['statuses'] = []

        # End of retrieving data. If there are unsaved tweets, append them to the database
        if len(tweets_list) > 0:
            # Save things
            tweet_df = pd.DataFrame(tweets_list)
            # Extract just the needed features for predicting, and the user_id for merging
            prediction_set = tweet_df[util.USER_PRED_FEATURES].copy()
            prediction_set.columns = util.PRED_FEATURES

            # If a user tweeted twice, they will be a duplicate here. No point in predicting them twice.
            prediction_set = prediction_set.drop_duplicates(subset=['id'])
            feature_df = cmf.create_feature_df(prediction_set)

            #feature_df['oob_preds'] = loaded_model.predict(feature_df.drop(columns=['id']))

            # Gets probability of being a bot
            #feature_df['oob_preds'] = loaded_model.predict_proba(feature_df.drop(columns=['id']))[:, 1]

            # Gets probability of being a bot using botometer api 
            feature_df = botometer_column(feature_df, THRESHOLD)

            #with open('feature_df.pkl', 'rb') as read:
            #    obj = pickle.load(read)

            #with open('feature_df.pkl', 'wb') as temp:
            #    obj = pd.concat([obj, feature_df])
            #    pickle.dump(obj, temp)
            
            # with open('test.pkl', 'wb') as temp:
            #     pickle.dump(feature_df, temp)


            # if (feature_df['prob_bot'] > THRESHOLD):
            #     feature_df['oob_preds'] = 1
            # else:
            #      feature_df['oob_preds'] = 0

            #INSERT HERE Save as feature_df as PKL file 
            #1st Save each batch (5) as a PKL File
            #2nd calculate prob 

            # ----------------------- Merge the predictions with our Data -----------------------
            # rename id in feature_df to user_id
            feature_df = feature_df.rename(columns={"id": "user_id"})
            tweet_df = feature_df[['user_id', 'oob_preds']].merge(
                tweet_df, how='left', left_on='user_id', right_on='user_id')
            # ----------------------- Append human_ids and bot_ids to our sets  -----------------------
            bot_id_set.update(tweet_df[tweet_df['oob_preds'] == 1]['user_id'].values)
            human_id_set.update(tweet_df[tweet_df['oob_preds'] == 0]['user_id'].values)
            # ----------------------- Get the hour of each tweet -----------------------
            tweet_df['created_at_dt'] = pd.to_datetime(tweet_df['created_at'])
            tweet_df['created_at_hour'] = tweet_df['created_at_dt'].apply(lambda x: x.replace(minute=0, second=0))
            # ----------------------- Reduce to an aggregate df of just the hour and bot/total tweets -------------
            temp = tweet_df.groupby(['created_at_hour', 'oob_preds']).size().reset_index(name='Count').copy()
            temp_gps = temp.groupby(['created_at_hour'])
            batch_df = temp_gps.apply(lambda df, a: sum(df[a]), 'Count').to_frame(name="Total_Tweets")
            batch_df['Bot_Tweets'] = temp_gps.apply(lambda df, a, b: sum(df[a] * df[b]), 'oob_preds', 'Count')
            #  ----------------------- Append and combine this batch with the overall df -----------------------
            overall_df = pd.concat([overall_df, batch_df], axis=0, join='outer')
            overall_df = overall_df.groupby(overall_df.index).sum()
            return overall_df
    except Exception as e:
        print(f" Encountered error: {e}")


def botometer_classification(pd, threshold):
# Assigns 1 or 0 by comparing the botometer api's probability to the given threshold
    id = pd['id']
    result = bom.check_account(id)
    score = result["cap"]["universal"]
    if score > threshold:
        return 1
    else:
        return 0

def botometer_column(pd, threshold):    
    pd["oob_preds"] = pd.apply(lambda row: botometer_classification(row, threshold), axis = 1)
    return pd

if __name__ == "__main__":
    overall_df = download_recent_tweets(keyword='ukraine', n_tweets=10)
    print(overall_df)
