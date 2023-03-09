After realizing that the Real-Time_Streaming method for hosting our trending app would not work due to CPU Usage issues,
I am trying to set up the following pipeline:
1. python code hosted on pythonanywhere (hopefully get the CPU usage below 2000 CPU sec per day for $5/monthly)
    - This code will retrieve data from twitter in batches (maybe every 15-30minutes), analyze it, and send data to a
    google spreadsheet. This data will just be the limited columns needed for plotting: Time, Total_Tweets, Bot_Tweets
2. Use a plugin like AwesomeTable (https://awesome-table.com/) to create a plot and embed link
3. Copy/Paste the link to the wordpress site.

(4/22/2021) Currently the framework is set up and functional using the scratch.py and cred.json files. The file
'scratch.py' generates random data and updates a google spreadsheet with this data. This data is embedded into a test
wordpress site (https://discoveringdatascience.com/index.php/2021/04/21/testing-embedding/). When the website is
refreshed, the plot is correctly updating with the most recent random data in the google doc.

Next Steps:

0. Extend scratch.py, AwesomeTable, and the wordpress demo to work with multiple plots (Ideally 3+ trending plots)
1. Write a program that analyzes the Twitter data and supplies the analyzed data rather than random data to the Google Doc.
2. Hosting this program on a website such as pythonanywhere, Amazon EC2, Google Cloud, etc.
3. Improving the aesthetics of the plot. Currently just shows the bare minimum of plotting ability.

4. Include more information with the plots such as overall bot percentage,
detecting periods of above normal bot activity maybe?, other ideas
