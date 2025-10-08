"""
Database models for KarsFinance
Updated for PostgreSQL with enhanced security and structure
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import db
import enum
from datetime import datetime

class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""
    INCOME = "Income"
    EXPENSE = "Expense"
    INVESTMENT = "Investment"

class Account(db.Model):
    """User account model with enhanced security"""
    __tablename__ = "account"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # bcrypt hashed password
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    last_login = db.Column(db.DateTime)
    
    # Financial defaults
    money = db.Column(db.Float, default=100_000)  # Portfolio cash
    total_value = db.Column(db.Float, default=100_000)  # Total portfolio value
    
    # Relationships
    stocks = relationship("Portfolio", back_populates="account", cascade="all, delete-orphan")
    ledger = relationship("Ledger", back_populates="account", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'email_verified': self.email_verified,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'money': self.money,
            'total_value': self.total_value
        }

class Stock(db.Model):
    """Stock symbols and information"""
    __tablename__ = "stock"
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'exchange': self.exchange,
            'is_active': self.is_active
        }

class Portfolio(db.Model):
    """User's stock holdings"""
    __tablename__ = "portfolio"
    
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False, index=True)
    shares = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Average cost
    date = db.Column(db.DateTime, server_default=func.now())
    
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    account = relationship("Account", back_populates="stocks")

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'shares': self.shares,
            'price': self.price,
            'date': self.date.isoformat() if self.date else None,
            'account_id': self.account_id
        }

class Ledger(db.Model):
    """Transaction history for all trades"""
    __tablename__ = "ledger"
    
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False, index=True)
    shares = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    buy_or_sell = db.Column(db.String(10), nullable=False)
    date = db.Column(db.DateTime, server_default=func.now())
    
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    account = relationship("Account", back_populates="ledger")

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'shares': self.shares,
            'price': self.price,
            'buy_or_sell': self.buy_or_sell,
            'date': self.date.isoformat() if self.date else None,
            'account_id': self.account_id
        }

class Category(db.Model):
    """Transaction categories"""
    __tablename__ = "category"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(SQLEnum(TransactionType), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Self-referential relationship for hierarchical categories
    parent = relationship("Category", remote_side=[id])
    children = relationship("Category", back_populates="parent")

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value if self.type else None,
            'parent_id': self.parent_id,
            'is_active': self.is_active
        }

class Transaction(db.Model):
    """Enhanced transaction model for comprehensive financial tracking"""
    __tablename__ = "transaction"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    type = db.Column(SQLEnum(TransactionType), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category")

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.value if self.type else None,
            'category_id': self.category_id,
            'amount': self.amount,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BudgetTarget(db.Model):
    """Budget targets for spending categories"""
    __tablename__ = "budget_target"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    monthly_amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'monthly_amount': self.monthly_amount,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CreditAccount(db.Model):
    """Credit accounts for credit score simulation"""
    __tablename__ = "credit_account"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # Credit Card, Loan, Mortgage
    credit_limit = db.Column(db.Float, nullable=False)
    current_balance = db.Column(db.Float, default=0)
    interest_rate = db.Column(db.Float, nullable=False)
    opened_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_type': self.account_type,
            'credit_limit': self.credit_limit,
            'current_balance': self.current_balance,
            'interest_rate': self.interest_rate,
            'opened_date': self.opened_date.isoformat() if self.opened_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PaymentEvent(db.Model):
    """Payment events for credit score calculation"""
    __tablename__ = "payment_event"
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("credit_account.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False)  # On-Time, Late, Missed
    created_at = db.Column(db.DateTime, server_default=func.now())

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'amount': self.amount,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Property(db.Model):
    """Real estate properties"""
    __tablename__ = "property"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    property_type = db.Column(db.String(50))  # Single Family, Condo, Townhouse
    purchase_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    annual_income = db.Column(db.Float, default=0)
    annual_expenses = db.Column(db.Float, default=0)
    current_mortgage_balance = db.Column(db.Float, default=0)
    interest_rate = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'address': self.address,
            'property_type': self.property_type,
            'purchase_price': self.purchase_price,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'annual_income': self.annual_income,
            'annual_expenses': self.annual_expenses,
            'current_mortgage_balance': self.current_mortgage_balance,
            'interest_rate': self.interest_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
