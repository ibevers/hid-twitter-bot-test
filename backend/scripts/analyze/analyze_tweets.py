"""
Any functions that rely on the machine learning model.
"""

import pickle
from tkinter import constants
import pandas as pd
from analyze.create_model_features import create_feature_df


MODEL_ONE_PATH = "update-database/analyze/models/Bot_Model_1.sav"
MODEL_THREE_PATH = "update-database/analyze/models/Bot_Model_3.sav"
def analyze_tweets(tweet_df, const):
    """
    Feeds the data for each model parameter into the model and returns a dataframe of 
    with columns time_period, human_count, and bot_count

    Parameters:
        relevant_tweets_df: a dataframe with all of the data from some tweets for the 
                            model parameters
    Returns:
        tweet_analysis
    """
    
     # End of retrieving data. If there are unsaved tweets, append them to the database
    if tweet_df.shape[0] > 0:

        # Extract just the needed features for predicting, and the user_id for merging
        prediction_set = tweet_df[const.USER_PRED_FEATURES].copy()
        prediction_set.columns = const.PRED_FEATURES

        # If a user tweeted twice, they will be a duplicate here. No point in predicting them twice.
        prediction_set = prediction_set.drop_duplicates(subset=['id'])
        feature_df = create_feature_df(prediction_set, const)

        #Load model
        load_path = MODEL_ONE_PATH
        loaded_model = pickle.load(open(load_path, 'rb'))
        feature_df['oob_preds'] = loaded_model.predict(feature_df.drop(columns=['id']))
        # ----------------------- Merge the predictions with our Data -----------------------
        # rename id in feature_df to user_id
        feature_df = feature_df.rename(columns={"id": "user_id"})
        tweet_df = feature_df[['user_id', 'oob_preds']].merge(
            tweet_df, how='left', left_on='user_id', right_on='user_id')
#######################################TEMP#####################################
#        dfeature_df = create_feature_df(prediction_set, const)
#
#        #Load model
#        dload_path = MODEL_THREE_PATH
#        dloaded_model = pickle.load(open(dload_path, 'rb'))
#        dfeature_df['oob_preds'] = dloaded_model.predict(dfeature_df.drop(columns=['id']))
#        # ----------------------- Merge the predictions with our Data -----------------------
#        # rename id in feature_df to user_id
#        dfeature_df = dfeature_df.rename(columns={"id": "user_id"})
#        dtweet_df = dfeature_df[['user_id', 'oob_preds']].merge(
#            tweet_df, how='left', left_on='user_id', right_on='user_id')
#
#
#        hi =0
#
#
#
##########################################################################################
        bot_id_set = set()
        human_id_set = set()

        bot_id_set.update(tweet_df[tweet_df['oob_preds'] == 1]['user_id'].values)
        human_id_set.update(tweet_df[tweet_df['oob_preds'] == 0]['user_id'].values)

        # ----------------------- Append human_ids and bot_ids to our sets  -----------------------
        bot_id_set.update(tweet_df[tweet_df['oob_preds'] == 1]['user_id'].values)
        human_id_set.update(tweet_df[tweet_df['oob_preds'] == 0]['user_id'].values)
        # ----------------------- Get the hour of each tweet -----------------------
        tweet_df['created_at_dt'] = pd.to_datetime(tweet_df['user_created_at'])
        tweet_df['created_at_hour'] = tweet_df['created_at_dt'].apply(lambda x: x.replace(minute=0, second=0))
        # ----------------------- Reduce to an aggregate df of just the hour and bot/total tweets -------------
        temp = tweet_df.groupby(['created_at_hour', 'oob_preds']).size().reset_index(name='Count').copy()
        temp_gps = temp.groupby(['created_at_hour'])
        batch_df = pd.DataFrame()
        batch_df = temp_gps.apply(lambda df, a: sum(df[a]), 'Count').to_frame(name="Total_Tweets")
        batch_df['Bot_Tweets'] = temp_gps.apply(lambda df, a, b: sum(df[a] * df[b]), 'oob_preds', 'Count')
        batch_df['created_at_hour'] = tweet_df.get('user_created_at')[0] #maybe buggy
        #  ----------------------- Append and combine this batch with the overall df -----------------------
        #overall_df = overall_df.append(batch_df)
        #overall_df = overall_df.groupby(overall_df.index).sum()

        #for col in batch_df.columns:
        #    print(col)
        #print(batch_df.shape)
        #print(batch_df.info)
        return batch_df
        #print("empty dataframe")
