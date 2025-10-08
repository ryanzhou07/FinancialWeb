"""
KarsFinance Flask API Backend
Main API application entry point
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv

from app.database import db
from app.routes import api_bp
from app.websocket_handlers import socketio

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    # SQLAlchemy works with both SQLite and PostgreSQL - just change the connection string
    # For PostgreSQL: postgresql://user:password@host:port/database
    # For SQLite: sqlite:///database.db
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/postgres')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # CORS configuration for React frontend
    CORS(app, origins=[
        "http://localhost:3000",  # React default port
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ])
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        """Root endpoint"""
        return jsonify({
            'message': 'KarsFinance API',
            'version': '1.0.0',
            'docs': '/api/docs'
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'service': 'KarsFinance API'})
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # For development
    socketio.run(app, host='127.0.0.1', port=8000, debug=True)
