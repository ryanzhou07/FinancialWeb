
import yfinance as yf
import pandas as pd
import requests
import csv
import json
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("TWELVE_DATA_API_KEY")

#Get the data from the API and write it to a file for visualization

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
FLASK_DIR = os.path.dirname(BASE_DIR) 

# Now correctly reference the static folder
STATIC_FOLDER = os.path.join(FLASK_DIR, "FinancialWeb/static")

file_path = os.path.join(STATIC_FOLDER, "trial_stock.csv")
file_path2 = "static/stock_data.json"

#Initializes stock data from TwelveData
def data_call():
    tickers = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            tickers.append(row[0])
    #TODO Integrate these back AAPL,QQQ,TRP:TSX,
    response = requests.get(url = "https://api.twelvedata.com/time_series?symbol=AAPL,BTC/USD&interval=1day&start_date=2020-03-23&end_date=2025-03-23&apikey=" + api_key)
    data = response.json()
    with open(file_path2, 'w') as f:
        json.dump(data, f, indent=4)



        
        
            
        
