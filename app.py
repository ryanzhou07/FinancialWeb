import os
from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
import flask_admin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink
from sqlalchemy.sql import func
import requests

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'your secret key'


finnhub_url = 'https://finnhub.io/api/v1/'
alphavantage_url = 'https://www.alphavantage.co/query?'
token_finnhub = 'your token'
token_alphavantage = 'your token'

##SQL Config
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

##database
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

with app.app_context():
        db.create_all()
        
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
@app.route('/simulator')
def simulator():
    return render_template('simulator.html')

if __name__ == '__main__':
    app.run(debug=True)
    