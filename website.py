from lib2to3 import refactor

import streamlit.components.v1 as components
import streamlit as st
import numpy as np
import pandas as pd
import codecs

#import gspread

from backend.scripts.sheets import get_database
from backend.scripts.sheets import get_rank_n_trend_sheet

PAGE_HTML = "index.html"
file = codecs.open(PAGE_HTML, 'r')
page = file.read()
components.html(page, width=1000, height=1000, scrolling=True)


DATABASE_SPREADSHEET_NAME = "twitter_bot_database"

#
database = get_database(DATABASE_SPREADSHEET_NAME)
trend_sheets = database.worksheets()
top_trend_sheet = get_rank_n_trend_sheet(1, trend_sheets)

top_trend_data = top_trend_sheet.get_all_values()

components.html()

with open('style.css') as f:
    st.markdown(f"<style>{(f.read())}</style>", unsafe_allow_html=True)

top_trend_data = pd.DataFrame(top_trend_data)
top_trend_data = top_trend_data.iloc[: , 1:]  #get rid of first columnn
#TO DO: Add dates back in
top_trend_data = top_trend_data.drop(index=0) #drop first row
top_trend_data.columns = ['all tweets', 'bot tweets'] #add labels
top_trend_data = top_trend_data.astype(int) #convert to int
#print(top_trend_data)
#print(top_trend_data)
#print(top_trend_data)

st.area_chart(top_trend_data)

