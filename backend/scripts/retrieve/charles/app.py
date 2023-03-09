import os
from time import sleep
from download_tweets import download_recent_tweets
from tweet_analysis import analyze

Version = 2.00
Model = 'Twitter_Bot_App_Bulk/Bot_Model_1'
if __name__ == "__main__":
    try:
        print("Twitter Bot Application!")
        print(f"Ver. {Version}")
        print(f"Model: {Model}\n")
        sleep(3)

        # ---------- GET the search term from the user and CREATE a folder for this search term if it does not already exist
        keyword = input('Please enter a keyword:')
        save_path = os.path.join(os.pardir, keyword)
        sleep(1)
        try:
            os.mkdir(save_path)
            print(f"Folder '{keyword}' has been created. \n")
            sleep(1)
            print(f"Files will be saved to the newly created folder: {keyword} \n")
        except:
            print(f"Files will be saved to existing folder named: {keyword} \n")
        sleep(3)

        # ---------- Retrieve & Reduce Tweets
        print("Retrieving Tweets")
        df, bot_ids, human_ids = download_recent_tweets(keyword=keyword, model_name=Model, save_path=save_path, test=False)
        print('Data Retrieval Complete. Beginning Analysis.\n')

        # ---------- Analyze Tweets
        analyze(df, bot_ids, human_ids, keyword)
        print('Analysis Complete. Closing this Window.\n')
        sleep(3)


    except Exception as e:
        print(f" Encountered error: {e}")
        print(f" Exiting Program.")
        sleep(10)