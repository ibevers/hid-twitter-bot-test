PURPOSE:
The purpose of the'Twitter_Bot_App_Bulk' folder was to create an executable file that anyone in the content team
other than the programmer could run locally to gather Twitter data. The app gathers all tweets from Twitter covering the
past ~7days with a specified keyword, analyzes the users to determine if they are bots or not, and produces a small
report. The app worked, is currently on the humanID shared drive:
https://drive.google.com/drive/folders/10azfruoCAcWG8Cj1hXo3fqKXjtyENAXD

INSTRUCTIONS:
The app is created using pyinstaller: https://www.pyinstaller.org/
To create the app follow these steps:
1. in terminal go to the top level directory 'Twitter_Bot_App_Bulk' and type the command that is in the file
    'pyinstaller_command.txt'
2. pyinstaller should generate a 'build' and a 'dist' folder. The 'app.exe' file should be in the dist folder. Copy/Paste
    the bot model (for example 'Bot_Model_1.sav') into the dist folder.
3. To run the app simply double click on the app.exe file.

NEXT STEPS:
This was made with the first Bot detection model, and needs to be updated to use a better model (Currently 3,01) and the
code should be updated to use a threshold of 0.20 (Model 1 did not use a threshold).

The current plan for creating a real-time trending graphic involves using the same Twitter endpoint that is used for
this application. Likely we will want to prioritize the real-time app, and will not be using this executable file.
Rather than splitting the api calls between an executable app and the real-time app and hurting both, it is likely best
to just require anyone that wants to use the executable app to get their own Twitter Developer
credentials (should only take a few days). These credentials could be put in place of the 'keys.py' file's current
credentials. An even better approach would then be to improve the app to have a nice GUI that asks the user to
input their Twitter credentials so nobody's API calls interfere with anyone else's.



