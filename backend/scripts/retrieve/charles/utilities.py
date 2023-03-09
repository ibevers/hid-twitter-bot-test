# List of features required as input to the function 'create_feature_df'
PRED_FEATURES = ['id', 'created_at', 'statuses_count', 'followers_count', 'friends_count', 'favourites_count',
                       'listed_count', 'name', 'screen_name', 'description', 'profile_use_background_image',
                       'default_profile', 'verified']

# Identical to PRED_FEATURES but with the prefix 'user_' on all features
USER_PRED_FEATURES = ['user_' + feature for feature in PRED_FEATURES]

# Features used exclusively for analysis purposes
ANALYSIS_FEATURES = ['created_at']

# Specifying that the unique tweet id must be saved for pagination
PAGINATION_FEATURE = ['id']  # The unique tweet id

# All features that should be saved from the twitter json
ALL_PULLED_FEATURES = USER_PRED_FEATURES + ANALYSIS_FEATURES + PAGINATION_FEATURE

# Would like to incorporate these features into a future model. Unused currently and not saved to reduce memory.
# INTERESTING_FEATURES = ['created_at', 'text', 'source', 'user_url', 'retweeted_status_id', 'in_reply_to_status_id', 'in_reply_to_user_id']

# Features required for our model
MODEL_INPUT_FEATURES = ['statuses_count', 'followers_count', 'friends_count', 'favourites_count', 'listed_count',
                     'default_profile', 'profile_use_background_image', 'verified', 'tweet_freq',
                     'followers_growth_rate', 'friends_growth_rate', 'favourites_growth_rate', 'listed_growth_rate',
                     'followers_friends_ratio', 'name_length', 'screen_name_length', 'name_digits',
                     'screen_name_digits', 'description_length']
