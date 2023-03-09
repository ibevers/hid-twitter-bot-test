import pickle 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import botometer


file = open('test.pkl', 'rb')
df = pickle.load(file)

twitter_app_auth = {
    'consumer_key': 'zzYIMt2JmFdwZWK2qRrEcWL75',
    'consumer_secret': 'Cj5CX5b3o9fJIHWaTexZ3ERSW6rMNFRtbpKTVvUrEjGFQeuXiB',
    'access_token': '1088230607870705664-TnpsNV7xT3FrtVqShf2azzXdSkVj27',
    'access_token_secret': '9GF8JT3EsG942VRJQPdCNZRg7vQO7Iq8NhL45A263rBab',
}
rapidapi_key = '04c96be8b9msh30a2b8957700538p155b9djsn37aef731713b'
bom = botometer.Botometer(wait_on_ratelimit=True, rapidapi_key=rapidapi_key, **twitter_app_auth)

result = bom.check_account('@clayadavis')
print(result)

def add_threshold_column(pd, threshold):
    if pd['botometer'] >= threshold:
        return 1
    else:
        return 0

# def botometer_column(pd):
#     id = pd['id']
#     result = bom.check_account(id)
#     score = result["cap"]["universal"]
#     if score > 0.5:
#         return 0
#     else:
#         return 1

# Threshold for determing whether it is bot generated
THRESHOLD = [0.5, 0.6, 0.7, 0.8, 0.9]
file = open('feature_df.pkl', 'rb')
df = pickle.load(file)

# df = df.drop(df.index[1000:])
# with open('feature_df.pkl', 'wb') as temp:
#     pickle.dump(df, temp)

with open('botometer_list.pkl', 'rb') as read:
    boto = pickle.load(read)

df_boto = pd.DataFrame(boto, columns = ['botometer'])

for threshold in THRESHOLD:
    column_threshold = str(threshold) + ' Threshold'
    df_boto[column_threshold] = df_boto.apply(lambda row: add_threshold_column(row, threshold), axis = 1)

# for i in id:
#     result = bom.check_account(i)
#     score = result["cap"]["universal"]
#     boto.append(score)
 
# with open('botometer_list.pkl', 'wb') as temp:
#     pickle.dump(boto, temp)

# for threshold in THRESHOLD:
#     column_threshold = str(threshold) + ' Threshold'
#     df[column_threshold] = df.apply(lambda row: add_threshold_column(row, threshold), axis = 1)

# print(bom.check_account(df['id'].iloc[0])["cap"]["universal"])

# df["botometer"] = df.apply(lambda row: botometer_column(row), axis = 1)

df_boto = df_boto.iloc[: , -5:]

fifty_thresh = df_boto['0.5 Threshold'].value_counts()
sixty_thresh = df_boto['0.6 Threshold'].value_counts()
seventy_thresh = df_boto['0.7 Threshold'].value_counts()
eighty_thresh = df_boto['0.8 Threshold'].value_counts()
ninety_tresh = df_boto['0.9 Threshold'].value_counts()

count_pd = pd.concat([fifty_thresh, sixty_thresh, seventy_thresh, eighty_thresh, ninety_tresh], axis = 1)

count_pd = count_pd.rename(index={0: "Real Account", 1: "Bot Account"})


index = ['0.5 Threshold', '0.6 Threshold', '0.7 Threshold', '0.8 Threshold', '0.9 Threshold']

# Normalize the columns so we can see the proportions
count_pd[index] = count_pd[index].apply(lambda x: (x / (x.sum())))

# Transpose the dataframe 

count_pd = count_pd.T
count_pd.plot(kind='bar', 
                    stacked=True, 
                    figsize=(10, 6))

plt.xlabel("Threshold")
plt.ylabel("Proportion")
                 
plt.show()


# print(df.groupby(['0.5 Threshold']).value_counts())
#for each threshold show proportion labeled as human or bot bar charts
