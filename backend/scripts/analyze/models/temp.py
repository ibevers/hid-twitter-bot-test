

import pickle








load_path = "/Users/isaacbevers/humanid/twitter-bot-activity-website/backend/scripts/analyze/models/Bot_Model_1.sav"
tweets_path = "/Users/isaacbevers/humanid/twitter-bot-activity-website/backend/data/3_test_tweets"

loaded_model = pickle.load(open(load_path, 'rb'))
loaded_tweets = pickle.load(open(tweets_path, 'rb'))
for tweet in loaded_tweets['statuses']:
    print("\n\n\n\n\n\n")
    print(tweet)
threshold = 0.4
predicted_proba = loaded_model.predict_proba()
predicted = (predicted_proba [:,1] >= threshold).astype('int')



hi = 10