#!/usr/bin/env	python3
from datetime import datetime
import math
from xmlrpc.client import Boolean
import pickle
import sys
sys.path.insert(len(sys.path), "backend/scripts")
from charles.download_tweets import get_recent_tweets

SNOWFLAKE_FACTOR = math.pow(2, 22)
SNOWFLAKE_OFFSET = 1288834974657 
TIME_DIFF_TOLERANCE = 60 #s in 1 minute
ID_RATIO_TOLERANCE = .00000001

def snowflake_to_time(id:int) -> datetime:
    """
    Converts a snowflake ID to the time it was created.
    """
    ms = id / math.pow(2, 22) + 1288834974657 + 7*3600000 #milliseconds
    time_created = datetime.fromtimestamp(ms/1000.0)
    return time_created

def time_to_snowflake(time: datetime) -> int:
    """
    Converts a time to a snowflake ID.
    """
    epoch_time = datetime(1970, 1, 1)
    delta = (time - epoch_time)
    ms = delta.total_seconds() * 1000
    id = (ms - SNOWFLAKE_OFFSET) * SNOWFLAKE_FACTOR
    return id

def dates_close(d1:datetime, d2:datetime) -> Boolean:
    diff = (d1 - d2).total_seconds()
    return diff < TIME_DIFF_TOLERANCE

def ids_close(id1:int, id2:int) -> Boolean:
    ratio = id1/id2
    return 1 - ratio < ID_RATIO_TOLERANCE

def get_test_tweets(n_tweets=10):
    tweets = ""
    try:
        tweets = pickle.load(str(n_tweets) + '_test_tweets')
    except:
        sys.path.insert(len(sys.path), "backend/scripts")
        from charles.download_tweets import get_recent_tweets
        tweets = get_recent_tweets(n_tweets=n_tweets, topic='nasa')
    return tweets

def get_id_date_dict(tweets):
    id_date_dict = {}
    for tweet in tweets['statuses']:
        time_str = tweet["created_at"].replace(' +0000', '')
        id_date_dict[tweet['id']] = datetime.strptime(time_str,"%a %b %d %H:%M:%S %Y")
    return id_date_dict


def save_test_tweets(n_tweets=10, save_path="", topic="nasa"):
    "Creates a file that stores a specified number of tweets for a given topic"
    tweets = get_recent_tweets(n_tweets=n_tweets, topic=topic)
    if save_path == "":
        save_path = str(n_tweets) + "_test_tweets"
    with open(save_path, 'wb') as fp:
        pickle.dump(tweets, fp, protocol=pickle.HIGHEST_PROTOCOL)

