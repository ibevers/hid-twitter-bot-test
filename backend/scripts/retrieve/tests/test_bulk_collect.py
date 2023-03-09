

from datetime import datetime
import sys
sys.path.insert(len(sys.path), "backend/scripts/retrieve")
from util import *

TEST_TWEETS_N = ['3, 10, 30, 100, 200']

def basic_test_snowflake_to_time():
    "Ensures that the actual time and estimated time are close enough"
    for n in TEST_TWEETS_N:
        tweets = get_test_tweets(n_tweets=n)
        id_date_dict = get_id_date_dict(tweets)
        for id in id_date_dict:
            time = id_date_dict[id]
            sf_time = snowflake_to_time(id)
            assert dates_close(time, sf_time), f"test 1: {time} {sf_time}"

def basic_test_time_to_snowflake():
    "Ensures that the actual id and the estimated id are close enough"
    for n in TEST_TWEETS_N:
        tweets = get_test_tweets(n_tweets=n)
        id_date_dict = get_id_date_dict(tweets)
        print(type(tweets))
        for id in id_date_dict.keys():
            time = id_date_dict[id]
            id_estimate = time_to_snowflake(time)
            assert ids_close(id, id_estimate)

basic_test_snowflake_to_time()
basic_test_time_to_snowflake()


