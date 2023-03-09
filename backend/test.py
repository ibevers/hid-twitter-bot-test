import gspread

gc = gspread.service_account(filename="backend/credentials/midyear-cursor-356818-324d91b7c97f.json")

sh = gc.open("twitter_bot_database")

print(sh.sheet1.get('A1'))
