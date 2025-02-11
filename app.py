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
import requests
import csv
import json
import yfinance as yf
import pandas as pd
from createData import data_call

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:" #Used for Testing Purposes -> Wipes data after closing app
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'your secret key'


finnhub_url = 'https://finnhub.io/api/v1/'
token_finnhub = 'your token'

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
    
    stocks = db.relationship('Stock_Portfolio', back_populates="account", lazy=True)
    

# Stock Names for Search
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(50))
    
#Stocks in each account
class Stock_Portfolio(db.Model):
    __tablename__ = "Stock_Portfolio"
    
    id = db.Column(db.Integer, primary_key = True)
    ticker = db.Column(db.String(10),nullable = False)
    shares = db.Column(db.Float,nullable = False)
    account_id = db.Column(db.Integer, ForeignKey('account.id'),nullable=False)
    
    account = db.relationship("Account", back_populates="stocks")
    
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
                #Adds stock to table in session
                
                db.session.add(stock)
                existing_symbols.add(symbol)  # Add symbol to list of existing

        db.session.commit()

##Flask-Admin
admin = Admin(app, name='Admin', template_mode='bootstrap3')

admin.add_view(ModelView(Account, db.session))

##Connects to Front Page
@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
    else:
        username = 'Guest'
    return render_template('index.html', username = username)
 
#Signup Page for New Users
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
    return render_template('trading.html')

#Gets Data to be presented
@app.route('/get-data', methods = ['Post'])
def get_data():
    symbol = request.data.decode('utf-8')
    df = pd.read_parquet("static/stock_data.parquet")
    df = df.round(2)
    df = df.groupby("Symbol").apply(lambda x: x.to_dict(orient="records")).to_dict()
    df = df[symbol]
    return jsonify(df)

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
    return render_template('portfolio.html')

if __name__ == '__main__':
    app.run(debug=True)
    
