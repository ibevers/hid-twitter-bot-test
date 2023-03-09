import pandas as pd
from datetime import datetime
import numpy as np


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

def safe_division(a, b):
    return a/max(1, b)

def create_feature_df(raw_df, const): #POTENTIALLY SOURCE OF ANALYSIS BUG
    """
    :param raw_df: raw dataframe of twitter data (flattened though).
    :return: df of features and a column of 'id'
    """
    df = raw_df.copy()
    dt_now = datetime.now()
    # ---------------------- Check for required columns/print to console any missing columns ----------------------
    needed_columns = set(const.PRED_FEATURES)
    input_columns = set(df.columns)
    set_overlap = needed_columns.intersection(input_columns)

    if set_overlap != needed_columns:
        print(f"Issue: Not all required columns provided to function 'create_feature_df'.")
        print(f"Missing features: {needed_columns - set_overlap}")
        return -3

    # ---------------------- Prepping columns for Quick Feature Making ----------------------
    # Using the 'created_at' feature to determine the amount of hours since account creation
    df['user_age'] = pd.to_datetime(df['created_at'])
    df['user_age'] = df['user_age'].dt.tz_localize(None).values
    df['user_age'] = (dt_now - df['user_age']) / np.timedelta64(1, 'h')

    # Removing non english characters
    # df['cleaned_screen_name'] = df['screen_name'].str.encode('ascii', 'ignore').str.decode('ascii')
    # df['cleaned_name'] = df['name'].str.encode('ascii', 'ignore').str.decode('ascii')

    # Replace invalid cells that contain 'nan' entries with either empty strings or 0's.
    df['name'] = df['name'].fillna('')
    df['screen_name'] = df['screen_name'].fillna('')
    df['description'] = df['description'].fillna('')
    # ---------------------- Making Features ----------------------
    df['tweet_freq'] = df.apply(lambda x: safe_division(x['statuses_count'], x['user_age']), axis=1)
    df['followers_growth_rate'] = df.apply(lambda x: safe_division(x['followers_count'], x['user_age']), axis=1)
    df['friends_growth_rate'] = df.apply(lambda x: safe_division(x['friends_count'], x['user_age']), axis=1)
    df['favourites_growth_rate'] = df.apply(lambda x: safe_division(x['favourites_count'], x['user_age']), axis=1)
    df['listed_growth_rate'] = df.apply(lambda x: safe_division(x['listed_count'], x['user_age']), axis=1)
    df['followers_friends_ratio'] = df.apply(lambda x: safe_division(x['followers_count'], x['friends_count']), axis=1)

    # df['cleaned_name_length'] = df['cleaned_name'].str.len()
    # df['cleaned_screen_name_length'] = df['cleaned_screen_name'].str.len()
    df['name_length'] = df['name'].str.len()
    df['screen_name_length'] = df['screen_name'].str.len()

    # df['cleaned_name_digits'] = df['cleaned_name'].str.count('[0123456789]')
    # df['cleaned_screen_name_digits'] = df['cleaned_screen_name'].str.count('[0123456789]')
    df['name_digits'] = df['name'].str.count('[0123456789]')
    df['screen_name_digits'] = df['screen_name'].str.count('[0123456789]')

    df['description_length'] = df['description'].str.len()
    df['description_length'].fillna(value=0, inplace=True)

    # Keeping only columns of interest
    keep_columns = const.MODEL_INPUT_FEATURES + ['id']
    return df[keep_columns]


if __name__ == "__main__":
    print('create feature df')
