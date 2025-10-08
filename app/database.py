"""
Database configuration for Flask API
SQLAlchemy works with both SQLite and PostgreSQL - only the connection string changes
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy (same ORM for both SQLite and PostgreSQL)
db = SQLAlchemy()