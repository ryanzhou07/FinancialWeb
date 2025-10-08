"""
Simple setup script for a fresh PostgreSQL database
Creates tables and populates with initial stock data
"""

import os
import sys
from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(__file__))

from app.database import db
from app.models import *
from api import create_app

# Load environment variables
load_dotenv()

def setup_database():
    """Create all tables in PostgreSQL"""
    print("🚀 Setting up fresh PostgreSQL database...")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Populate stock data from CSV
            populate_stock_data()
            
            # Create some default categories
            create_default_categories()
            
            print("✅ Database setup completed successfully!")
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False
    
    return True

def populate_stock_data():
    """Populate stock symbols from CSV file"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'static', 'stock_info.csv')
        
        if not os.path.exists(csv_path):
            print(f"⚠️  Stock CSV file not found: {csv_path}")
            return
        
        # Read CSV data
        df = pd.read_csv(csv_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Insert data into database
        stock_count = 0
        for _, row in df.iterrows():
            symbol = row.get("Symbol", "").strip()
            name = row.get("Shortname", "").strip()
            exchange = row.get("Exchange", "").strip()
            
            if symbol:  # Only add if symbol exists
                # Check if stock already exists
                existing = Stock.query.filter_by(symbol=symbol).first()
                if not existing:
                    stock = Stock(
                        symbol=symbol,
                        name=name,
                        exchange=exchange,
                        is_active=True
                    )
                    db.session.add(stock)
                    stock_count += 1
        
        db.session.commit()
        print(f"✅ Added {stock_count} stocks to database")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to populate stock data: {e}")

def create_default_categories():
    """Create default transaction categories"""
    try:
        # Income categories
        income_categories = [
            {"name": "Salary", "type": TransactionType.INCOME},
            {"name": "Freelance", "type": TransactionType.INCOME},
            {"name": "Investment Returns", "type": TransactionType.INCOME},
            {"name": "Other Income", "type": TransactionType.INCOME}
        ]
        
        # Expense categories
        expense_categories = [
            {"name": "Food & Dining", "type": TransactionType.EXPENSE},
            {"name": "Transportation", "type": TransactionType.EXPENSE},
            {"name": "Housing", "type": TransactionType.EXPENSE},
            {"name": "Utilities", "type": TransactionType.EXPENSE},
            {"name": "Healthcare", "type": TransactionType.EXPENSE},
            {"name": "Entertainment", "type": TransactionType.EXPENSE},
            {"name": "Shopping", "type": TransactionType.EXPENSE},
            {"name": "Other Expenses", "type": TransactionType.EXPENSE}
        ]
        
        # Investment categories
        investment_categories = [
            {"name": "Stock Purchase", "type": TransactionType.INVESTMENT},
            {"name": "Stock Sale", "type": TransactionType.INVESTMENT},
            {"name": "Real Estate", "type": TransactionType.INVESTMENT},
            {"name": "Cryptocurrency", "type": TransactionType.INVESTMENT}
        ]
        
        all_categories = income_categories + expense_categories + investment_categories
        
        category_count = 0
        for cat_data in all_categories:
            # Check if category already exists
            existing = Category.query.filter_by(
                name=cat_data["name"], 
                type=cat_data["type"]
            ).first()
            
            if not existing:
                category = Category(
                    name=cat_data["name"],
                    type=cat_data["type"],
                    is_active=True
                )
                db.session.add(category)
                category_count += 1
        
        db.session.commit()
        print(f"✅ Created {category_count} default categories")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to create default categories: {e}")

def main():
    """Main setup function"""
    print("📋 KarsFinance Database Setup")
    print("=" * 40)
    
    # Check environment variables
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/postgres')
    print(f"Database URL: {database_url}")
    
    # Test database connection
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Make sure PostgreSQL is running:")
        print("   docker-compose up -d postgres")
        print("   OR install PostgreSQL locally and update DATABASE_URL")
        sys.exit(1)
    
    # Setup database
    if setup_database():
        print("\n🎉 Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the API server: python api.py")
        print("2. Test the API: http://localhost:8000")
        print("3. Set up React frontend (see frontend-setup.md)")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
