"""
API routes for KarsFinance Flask application
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.database import db
from app.models import Account, Stock, Portfolio, Ledger
from app.auth import hash_password, verify_password, create_access_token, verify_token
import os
import json
import pandas as pd

# Create blueprint for API routes
api_bp = Blueprint('api', __name__)

def token_required(f):
    """Decorator to require JWT token authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Extract token from "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Verify token and get user info
            data = verify_token(token)
            current_user_id = data['sub']
            current_user = Account.query.get(current_user_id)
            
            if not current_user or not current_user.is_active:
                return jsonify({'message': 'User not found or inactive'}), 401
                
        except Exception as e:
            return jsonify({'message': f'Token is invalid: {str(e)}'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Authentication routes
@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Check if user already exists
        if Account.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
        
        if Account.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        # Create new user
        password_hash = hash_password(data['password'])
        new_user = Account(
            username=data['username'],
            email=data['email'],
            password_hash=password_hash
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(data={'sub': new_user.id})
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('username', 'password')):
            return jsonify({'message': 'Username and password required'}), 400
        
        # Find user by username or email
        user = Account.query.filter(
            (Account.username == data['username']) | (Account.email == data['username'])
        ).first()
        
        if not user or not verify_password(data['password'], user.password_hash):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Account is inactive'}), 401
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(data={'sub': user.id})
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@api_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user information"""
    return jsonify({'user': current_user.to_dict()}), 200

# Stock routes
@api_bp.route('/stocks/search', methods=['GET'])
def search_stocks():
    """Search for stocks by symbol or name"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify([]), 200
    
    stocks = Stock.query.filter(
        (Stock.symbol.ilike(f'%{query}%')) | (Stock.name.ilike(f'%{query}%'))
    ).limit(10).all()
    
    return jsonify([stock.to_dict() for stock in stocks]), 200

@api_bp.route('/stocks/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """Get stock information by symbol"""
    stock = Stock.query.filter_by(symbol=symbol.upper()).first()
    
    if not stock:
        return jsonify({'message': 'Stock not found'}), 404
    
    return jsonify(stock.to_dict()), 200

# Portfolio routes
@api_bp.route('/portfolio', methods=['GET'])
@token_required
def get_portfolio(current_user):
    """Get user's portfolio holdings"""
    holdings = Portfolio.query.filter_by(account_id=current_user.id).all()
    return jsonify([holding.to_dict() for holding in holdings]), 200

@api_bp.route('/portfolio/holdings/<ticker>', methods=['GET'])
@token_required
def get_holding_details(current_user, ticker):
    """Get details for a specific holding"""
    holding = Portfolio.query.filter_by(
        account_id=current_user.id, 
        ticker=ticker.upper()
    ).first()
    
    if not holding:
        return jsonify({'message': 'Holding not found'}), 404
    
    return jsonify(holding.to_dict()), 200

# Trading routes
@api_bp.route('/trading/buy', methods=['POST'])
@token_required
def buy_stock(current_user):
    """Buy stock shares"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('ticker', 'shares', 'price')):
            return jsonify({'message': 'Missing required fields'}), 400
        
        ticker = data['ticker'].upper()
        shares = float(data['shares'])
        price = float(data['price'])
        total_cost = shares * price
        
        # Check if user has enough money
        if current_user.money < total_cost:
            return jsonify({'message': 'Insufficient funds'}), 400
        
        # Update user's money
        current_user.money -= total_cost
        
        # Add to portfolio or update existing holding
        existing_holding = Portfolio.query.filter_by(
            account_id=current_user.id,
            ticker=ticker
        ).first()
        
        if existing_holding:
            # Update existing holding (average cost calculation)
            total_shares = existing_holding.shares + shares
            total_value = (existing_holding.shares * existing_holding.price) + total_cost
            existing_holding.price = total_value / total_shares
            existing_holding.shares = total_shares
        else:
            # Create new holding
            new_holding = Portfolio(
                account_id=current_user.id,
                ticker=ticker,
                shares=shares,
                price=price
            )
            db.session.add(new_holding)
        
        # Add to ledger
        new_ledger_entry = Ledger(
            account_id=current_user.id,
            ticker=ticker,
            shares=shares,
            price=price,
            buy_or_sell='Buy'
        )
        db.session.add(new_ledger_entry)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Stock purchased successfully',
            'holding': existing_holding.to_dict() if existing_holding else new_holding.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Purchase failed: {str(e)}'}), 500

@api_bp.route('/trading/sell', methods=['POST'])
@token_required
def sell_stock(current_user):
    """Sell stock shares"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('ticker', 'shares', 'price')):
            return jsonify({'message': 'Missing required fields'}), 400
        
        ticker = data['ticker'].upper()
        shares_to_sell = float(data['shares'])
        price = float(data['price'])
        total_proceeds = shares_to_sell * price
        
        # Find existing holding
        holding = Portfolio.query.filter_by(
            account_id=current_user.id,
            ticker=ticker
        ).first()
        
        if not holding:
            return jsonify({'message': 'No holding found for this stock'}), 404
        
        if holding.shares < shares_to_sell:
            return jsonify({'message': 'Insufficient shares to sell'}), 400
        
        # Update holding
        holding.shares -= shares_to_sell
        
        # Remove holding if no shares left
        if holding.shares == 0:
            db.session.delete(holding)
        
        # Update user's money
        current_user.money += total_proceeds
        
        # Add to ledger
        new_ledger_entry = Ledger(
            account_id=current_user.id,
            ticker=ticker,
            shares=shares_to_sell,
            price=price,
            buy_or_sell='Sell'
        )
        db.session.add(new_ledger_entry)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Stock sold successfully',
            'proceeds': total_proceeds
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Sale failed: {str(e)}'}), 500

# Ledger routes
@api_bp.route('/ledger', methods=['GET'])
@token_required
def get_ledger(current_user):
    """Get user's transaction ledger"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    ledger_entries = Ledger.query.filter_by(account_id=current_user.id)\
        .order_by(Ledger.date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'entries': [entry.to_dict() for entry in ledger_entries.items],
        'total': ledger_entries.total,
        'pages': ledger_entries.pages,
        'current_page': page
    }), 200

# Data fetching routes (from original app.py)
@api_bp.route('/data/<path:symbol>', methods=['GET', 'OPTIONS'])
def get_stock_data(symbol):
    """Get historical stock data for a symbol"""
    if request.method == 'OPTIONS':
        # Let CORS middleware add the appropriate headers
        return ('', 204)

    normalized_symbol = symbol.upper()

    # Support common alternate separators like BTC/USD -> BTCUSD
    clean_symbol = normalized_symbol.replace('/', '').replace('-', '')

    try:
        # Try to get data from JSON file first
        file_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'stock_data.json')
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)

            # Exact match first
            if normalized_symbol in data and "values" in data[normalized_symbol]:
                return jsonify(data[normalized_symbol]["values"]), 200

            # Try cleaned version (for symbols containing separators)
            if clean_symbol in data and "values" in data[clean_symbol]:
                return jsonify(data[clean_symbol]["values"]), 200
        
        # Fallback: return empty data structure
        return jsonify({
            "message": "No historical data available for this symbol",
            "symbol": normalized_symbol,
            "values": []
        }), 200
        
    except Exception as e:
        return jsonify({
            "message": f"Error fetching data: {str(e)}",
            "symbol": normalized_symbol,
            "values": []
        }), 500

@api_bp.route('/portfolio/live', methods=['GET'])
@token_required
def get_live_portfolio(current_user):
    """Get live portfolio data with current values"""
    try:
        holdings = Portfolio.query.filter_by(account_id=current_user.id).all()
        
        portfolio_data = {
            'holdings': [holding.to_dict() for holding in holdings],
            'total_cash': current_user.money,
            'total_value': current_user.total_value,
            'user_id': current_user.id
        }
        
        return jsonify(portfolio_data), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching portfolio: {str(e)}'}), 500
