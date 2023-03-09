#from Google_Doc_Method.keys import BEARER_TOKEN
#import scripts.constants as const
#from analyze.create_model_features import create_feature_df
#from asyncio import constants
#from pyparsing import col
from typing import OrderedDict
import tweepy
import pandas as pd
import pytz
from datetime import timedelta
from datetime import datetime
from tweepy.auth import OAuthHandler


# CONSUMER_KEY = "iDKkou5UDzUKhx2bGwCkqOGwe" 
# CONSUMER_SECRET = "ou1uP0poin8pcTqNvdbbFTHrYFwrxQfv6x1VuhIEdTLXSg2xLk"
# ACCESS_TOKEN = "1549082875667947520-LIQNtc5Gpgl2XMBse1w1X8BR1lm54v"
# ACCESS_TOKEN_SECRET = 'csCm6DNFBIpEVBhoGLQrffDkCGZqa78f5SZpRmtL3JnZC'

CONSUMER_KEY = "zzYIMt2JmFdwZWK2qRrEcWL75"
CONSUMER_SECRET_KEY = "Cj5CX5b3o9fJIHWaTexZ3ERSW6rMNFRtbpKTVvUrEjGFQeuXiB"

ACCESS_TOKEN = "1088230607870705664-TnpsNV7xT3FrtVqShf2azzXdSkVj27"
ACCESS_TOKEN_SECRET = "9GF8JT3EsG942VRJQPdCNZRg7vQO7Iq8NhL45A263rBab"

#Charles -- dev verified
BEARER_TOKEN ='AAAAAAAAAAAAAAAAAAAAAPUcKgEAAAAA6tsBbkgJdsF1%2FnkaMtFcFzLKbOw%3DwvkcYNWGRkXBULNYjFwKQAdXbRbDmYt3rO2qlZ2TraxVK0JlzX'



RECENT_TWEET_SEARCH_USER_LIMIT = 180 #https://developer.twitter.com/en/docs/twitter-api/rate-limits
RECENT_TWEET_SEARCH_APP_LIMIT = 450 #https://developer.twitter.com/en/docs/twitter-api/rate-limits
TWITTER_COLLECTION_PERIOD = 15 #minutes--this is the period to which rate limits apply
TWITTER_RECENT_COLLECTION_WINDOW = 7 #days
GLOBAL_WOEID = 1 #https://blog.twitter.com/engineering/en_us/a/2010/woeids-in-twitters-trends

def authenticate():
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    #auth = tweepy.OAuth2BearerHandler(BEARER_TOKEN)
    return tweepy.API(auth)

def get_time_window(collection_period):
    utc=pytz.UTC
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=collection_period)
    end_time = utc.localize(end_time)
    start_time = utc.localize(start_time)
    return {"start_time":start_time, "end_time":end_time}

def retrieve_tweets(query:str, n_trends:int, collection_period:int) -> list[tweepy.api]:
    """
    Gets the maximum number of recent tweets retrievable in the update window divided 
    by the number of trends. Calculates the start time and end time of the collection
    period. Discards any tweets created outside the collection window.

    Parameters:
        query: a search query for retrieving tweets from the Twitter API
        n_trends: the number of trends being searched for in this collection period
        collection_period: how often the database is updated
    
    Returns:
        tweets: the collected tweets
    """
    api = authenticate()

    #Change to RECENT_TWEET_SEARCH_APP_LIMIT based on credentials used
    #num_tweets_to_collect = int(\
        #((TWITTER_COLLECTION_PERIOD/collection_period)*RECENT_TWEET_SEARCH_USER_LIMIT)/n_trends)
    print("TEMP REMOVE ME TWEETS 57ish")
    query='fern'
    num_tweets_to_collect = 10
    tweets = api.search_tweets(q=query, count=num_tweets_to_collect, result_type="recent")
    time_window = get_time_window(collection_period) #(start_time, end_time)
    for i, tweet in enumerate(tweets):
        if tweet.created_at < time_window["start_time"] or tweet.created_at > time_window['end_time']:
            tweets.remove(i)
    return tweets

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

def get_model_param_data_from_tweets(raw_tweets):
    flat_tweets = []

    
    #tweets_list = []
    #overall_df = pd.DataFrame()
    #human_id_set = set()
    #bot_id_set = set()
    #time_data = None
    #min_id = None
    #starting_time = None
    ## Ensure properly following Twitter API rate limits
    #print(const.ALL_PULLED_FEATURES)
    #while len(raw_tweets['statuses'])>0:
    #    # Convert the raw json to a list of dictionaries.
    #    cur_tweets = [dict_flatten(tweet) for tweet in raw_tweets['statuses']]
    #    # Then reduce each dictionary to just the features desired.
    #    reduced_cur_tweets = [{k: tweet.get(k, None) for k in const.ALL_PULLED_FEATURES} for tweet in cur_tweets]
    #    # Store the data in our growing list
    #    tweets_list.extend(reduced_cur_tweets)


    #    # Tweets from list -> DataFrame
    #    tweet_df = pd.DataFrame(tweets_list)
    #    tweets_list = []
    #    # Extract just the needed features for predicting, and the user_id for merging
    #    prediction_set = tweet_df[const.USER_PRED_FEATURES].copy()
    #    prediction_set.columns = const.PRED_FEATURES

    #    # If a user tweeted twice, they will be a duplicate here. No point in predicting them twice.
    #    prediction_set = prediction_set.drop_duplicates(subset=['id'])
    #    feature_df = create_feature_df(prediction_set)
    #    return feature_df
    """
    MODEL_INPUT_FEATURES = 
    ['statuses_count', 
    'followers_count', 
    'friends_count', 
    'favourites_count', 
    'listed_count',
    'default_profile', 
    'profile_use_background_image', 
    'verified', 
    
    'tweet_freq',
    'followers_growth_rate', 
    'friends_growth_rate', 
    'favourites_growth_rate', 
    'listed_growth_rate',
    'followers_friends_ratio', 
    'name_length', 
    'screen_name_length', 
    'name_digits',
    'screen_name_digits', 
    'description_length']
    """
    for tweet in raw_tweets:
        flat_tweet = []
        flat_tweet.append(tweet.user.statuses_count)
        flat_tweet.append(tweet.user.followers_count)
        flat_tweet.append(tweet.user.friends_count)
        flat_tweet.append(tweet.favorite_count)
        flat_tweet.append(tweet.user.listed_count)
        flat_tweet.append(tweet.user.default_profile)
        flat_tweet.append(tweet.user.profile_use_background_image)
        flat_tweet.append(tweet.user.verified)

        flat_tweet.append(tweet.id)
        flat_tweet.append(tweet.created_at)
        flat_tweet.append(tweet.user.name)
        flat_tweet.append(tweet.user.screen_name)
        flat_tweet.append(tweet.user.description)



        flat_tweets.append(flat_tweet)
    return flat_tweets

def get_relevant_tweets_df(query:str, n_trends:int, collection_period:int, const) -> pd.DataFrame:
    raw_tweets = retrieve_tweets(query, n_trends, collection_period)
    tweet_features = get_model_param_data_from_tweets(raw_tweets)
    tweet_features_df = pd.DataFrame(tweet_features)
    tweet_features_df.columns = const.USER_PRED_FEATURES
    return tweet_features_df


def get_top_trends():
    api = authenticate()
    trends_seen = set({})
    unique_trends = []
    # trends_available = api.available_trends()
    # top_trends = api.trends_place(id=GLOBAL_WOEID)
    top_trends = api.trends_place(id=GLOBAL_WOEID)
    for trend in top_trends[0]['trends']:
        if trend['name'] not in trends_seen:
            unique_trends.append(trend)
            trends_seen.add(trend['name'])
    return unique_trends

def get_trend_dict(n_trends:int, top_trends:list) -> dict:
    """
    Creates a dictionary of trend names to ranks for the top n ranks.
    """
    trend_dict = {}
    for trend_rank in range(n_trends):
        trend_name = top_trends[trend_rank]["name"]
        trend_query = top_trends[trend_rank]["query"]
        trend_dict[trend_name] = {'query':trend_query, 'rank':str(trend_rank + 1)}
    return trend_dict


