import os
from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import flask_admin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink
from sqlalchemy.sql import func
from flask_socketio import SocketIO, emit
import requests
import csv
import json
import pandas as pd
import yfinance as yf
import pandas as pdw
from createData import data_call
from dotenv import load_dotenv
import websocket
import threading

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

##Flask Config
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:" #Used for Testing Purposes -> Wipes data after closing app
app.config['SECRET_KEY'] = 'your secret key'
socketio = SocketIO(app)

db = SQLAlchemy(app)
api_key = os.getenv("TWELVE_DATA_API_KEY")

##SQL Config

db.init_app(app)


##database for account
class Account(db.Model):
    __tablename__ = "account"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    money = db.Column(db.Float, default = 100_000_000)
    total_value = db.Column(db.Float, default = 100_000_000)
    
    stocks = db.relationship('Trades', back_populates="account", lazy=True)
    

# Stock Names for Search
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(50))
    
#Stocks in each account
class Trades(db.Model):
    __tablename__ = "Stock_Portfolio"
    
    id = db.Column(db.Integer, primary_key = True)
    ticker = db.Column(db.String(10), index = True, nullable = False)
    shares = db.Column(db.Float,nullable = False)
    price = db.Column(db.Float, nullable = False)
    date = db.Column(db.DateTime, server_default=func.now())

    account_id = db.Column(db.Integer, ForeignKey('account.id'),nullable=False)
    account = db.relationship("Account", back_populates="stocks")
    
@app.before_request
def clear_session_if_invalid():
    username = session.get('username')
    if username:
        user = Account.query.filter_by(username=username).first()
        if not user:
            session.clear()

#Populating the Stock Table
#Finds existing symbols in database and only adds new ones into table from CSV
with app.app_context():
        db.create_all()
        with db.session.no_autoflush:  # 🔹 Prevents premature flush
            existing_symbols = {stock.symbol for stock in Stock.query.all()}  # Get all existing symbols

        with open("static/stock_info.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [header.strip() for header in reader.fieldnames]  

            for row in reader:
                symbol = row.get("Symbol", "").strip()
                
                if symbol in existing_symbols:
                    continue

                stock = Stock(
                    symbol=symbol,
                    name=row.get("Shortname", "").strip(),
                    exchange=row.get("Exchange", "").strip()
                )
                
                db.session.add(stock)
                existing_symbols.add(symbol) 

        db.session.commit()
            
#Flask-Admin
admin = Admin(app, name='Admin', template_mode='bootstrap3')

admin.add_view(ModelView(Account, db.session))
    
#Connects to Front Page
#If user in session it will display their username else it will display guest
@app.route('/')
def index():
    if 'username' in session: 
        username = session['username']
    else:
        username = 'Guest'
    return render_template('index.html', username = username)
 
#Signup Page for New Users
#Waits for Post Request to submit home then adds to account table and commits
#Redirects to Login
@app.route('/signup', methods = ('GET','POST'))
def signup():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account = Account(username=username, password=password, email=email)
        db.session.add(account)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

#Login Page for New Users
#When form submitted, it filters the Account table for username and password
#Sets session username if credientals correct and redirects to home page
@app.route('/login', methods = ('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account = Account.query.filter_by(username = username, password=password).first()
        if account and account.password == password:  # Compare passwords
            session['username'] = account.username
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

#Renders Simulator Page
@app.route('/trading', methods = ('GET','POST'))
def trading():                 
    return render_template('simulator/trading.html')

#Function to Deal with Trade Requests
@app.route('/trade', methods = ['GET','POST'])
def trade():
    data = request.get_json()
    print(data)
    account = Account.query.filter_by(username = session['username']).first()
    if(data['action'] == 'Buy'):
        if account:
            price = data['price'].replace('$', '').replace(',', '')
            if account.money >= float(price) * float(data['shares']):
                new_stock = Trades(ticker = data['symbol'], shares = data['shares'], price = price, account_id = account.id)
                db.session.add(new_stock)
                account.money -= float(price) * float(data['shares'])
                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Stock purchased successfully!'})
    elif(data['action'] == 'Sell'):
        if account:
            price = data['price'].replace('$', '').replace(',', '')
            stock = Trades.query.filter_by(ticker = data['symbol'], account_id = account.id).first()
            if stock and stock.shares >= float(data['shares']):
                stock.shares -= float(data['shares'])
                account.money += float(price) * float(data['shares'])
                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Stock sold successfully!'})
            
@app.route('/live-view')
def live_view():
    trades = Trades.query.order_by(Trades.date.desc()).all()
    return render_template('simulator/trades_live.html', trades=trades)
        
#Gets Data to be presented
#Display historical data depending on if websocket exists, first if means no websocket available
#This function will return data for the requested symbol
#TODO - Change to work with websockets and check if it is in test data
@app.route('/get-data', methods = ['Post'])
def get_data():
    symbol = request.data.decode('utf-8')
    if symbol!= 'AAPL' and symbol != 'QQQ' and symbol != 'TRP:TSX' and symbol != 'VOW3:XETR' and symbol != 'BTC/USD':
        df = pd.read_parquet("static/stock_data.parquet")
        df = df.round(2)
        df = df.groupby("Symbol").apply(lambda x: x.to_dict(orient="records")).to_dict()
        df = df[symbol]
        return jsonify(df)
    with open("static/stock_data.json", "r") as f:
        data = json.load(f)
    return jsonify(data[symbol]["values"])


#Searches for Stock in Database
#When key is pressed in search bar, queries database to look for suggestions and prints 10 of them
@app.route('/search', methods = ["GET"])
def search_stock():
    query = request.args.get("q", "").lower()

    if not query:
        return jsonify([])
    
    stocks = Stock.query.filter(
        (Stock.symbol.ilike(f"%{query}%")) | (Stock.name.ilike(f"%{query}%"))
    ).limit(10).all()

    return jsonify([
        {"symbol": s.symbol, "name": s.name} for s in stocks
    ])

@app.route('/portfolio')
def portfolio():
    return render_template('simulator/portfolio.html')


# websocket setup
ws = None

def setup_ws():
    global ws
    def on_open(ws):
        print("WebSocket opened")
    def on_message(ws, message):
        data = json.loads(message)
        socketio.emit('update', data)
    
    ws = websocket.WebSocketApp(
        "wss://ws.twelvedata.com/v1/quotes/price?apikey=REMOVED_KEY",
        on_open=on_open,
        on_message=on_message
    )
    try:
        threading.Thread(target=ws.run_forever, daemon=True).start()
    except Exception as e:
        print(f"Error starting WebSocket: {e}")
        
setup_ws()
#SocketIO Connections and Disconnections
@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")
    
#Subscribes to the Symbol When New Stock Name Chosen
@socketio.on('subscribe')
def handle_subscribe(data):
    global ws
    symbol = None
    if ws:
        symbol = data['symbol']
        message = {
            "action": "subscribe",
            "params": {
                "symbols": symbol,
                "apikey": api_key
            }
        }
        try:
            ws.send(json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")
        
    else:
        print("WebSocket is not initialized")

#Unsubscribes Old Symbol when New Stock Name is Chosen
#TODO Fix Unsubscribe for Bitcoin to APPL Chnage
@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    global ws
    if ws:
        symbol = data['symbol']
        message = {
            "action": "unsubscribe",
            "params": {
                "symbols": symbol,
                "apikey": api_key
            }
        }
        try:
            ws.send(json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")

@socketio.on('reset')
def handle_reset():
    global ws
    if ws:
        message = {
            "action": "reset",
            "params": {
                "apikey": api_key
            }
        }
        try:
            ws.send(json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")
        

#For Testing Purposes Can Be Used Later
# - > data_call()

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=8000, debug=True)
    
