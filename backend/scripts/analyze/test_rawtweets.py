import pickle 

file = open('raw_tweets.pkl', 'rb')
df = pickle.load(file)
print(df)