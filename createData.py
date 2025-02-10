
import yfinance as yf
import pandas as pd
import requests
import csv
import json
import os

#Get the data from the API and write it to a file for visualization


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
FLASK_DIR = os.path.dirname(BASE_DIR) 

# Now correctly reference the static folder
STATIC_FOLDER = os.path.join(FLASK_DIR, "static")

file_path = os.path.join(STATIC_FOLDER, "data.json")


def data_call():
    tickers = ['AAPL', 'GOOGL', 'AMZN' , 'TSLA' , 'NVDA', 'PYPL', 'ADBE', 'NFLX']
    try:
        data = yf.download(tickers, period = '5y', threads=False, interval = '1mo',group_by='ticker')
        data = data.reset_index()
        data['Date']= data['Date'].astype(str)
        data.dropna(inplace = True)
        data = data.to_dict(orient = "records")
        with open('static/data.json', "w") as f:
            json.dump(data, f, indent=4)
            f.close()
    except:
        print("Error")
        data = None
        with open('static/data.json', "w") as f:
            json.dump(data, f, indent=4)
            f.close()
    
    
        
        