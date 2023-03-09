"functions related to google sheets"
import gspread

def get_database(database_name):
    google_drive = gspread.service_account(filename="backend/credentials/twitter-bot-database.json") #authenticate
    database = google_drive.open(database_name)
    return database

def get_rank_n_trend_sheet(rank, trend_sheets):
    for sheet in trend_sheets:
        if sheet.title[0] == str(rank):
            return sheet


