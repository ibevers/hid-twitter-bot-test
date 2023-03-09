import botometer
import pickle 

twitter_app_auth = {
    'consumer_key': 'zzYIMt2JmFdwZWK2qRrEcWL75',
    'consumer_secret': 'Cj5CX5b3o9fJIHWaTexZ3ERSW6rMNFRtbpKTVvUrEjGFQeuXiB',
    'access_token': '1088230607870705664-TnpsNV7xT3FrtVqShf2azzXdSkVj27',
    'access_token_secret': '9GF8JT3EsG942VRJQPdCNZRg7vQO7Iq8NhL45A263rBab',
}
rapidapi_key = '04c96be8b9msh30a2b8957700538p155b9djsn37aef731713b'

file = open('raw_tweets.pkl', 'rb')
df = pickle.load(file)
tweets = df["statuses"]

bom = botometer.Botometer(wait_on_ratelimit=True, rapidapi_key=rapidapi_key, **twitter_app_auth)
# result = bom.check_account('@clayadavis')
blt = botometer.BotometerLite(rapidapi_key=rapidapi_key)
blt_twitter = botometer.BotometerLite(rapidapi_key=rapidapi_key, **twitter_app_auth)

id_list = []
tweet_list = tweets
for i, tweet in enumerate(tweet_list):
    user = tweet['user']
    id_list.append(user['id'])
    #result = bom.check_account(user['id'])
    #print(i)
    #print(result)
    # id_list.append(tweet['id'])

screen_name_list = ['yang3kc', 'onurvarol', 'clayadavis']
# blt_scores = blt_twitter.check_accounts_from_screen_names(screen_name_list)

# # Prepare a list of user_ids you want to check.
# # The list should contain no more than 100 user_ids.
user_id_list = [1133069780917850112, 77436536, 1548959833]
for id in screen_name_list:
    print(bom.check_account(id))
#blt_scores = blt_twitter.check_accounts_from_user_ids(user_id_list)


#blt_scores = blt.check_accounts_from_tweets(tweet_list)

# print(result)
