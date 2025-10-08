"""
WebSocket handlers for real-time stock price updates
"""

from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import threading
import websocket
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

# Global WebSocket connection
ws_connection = None
api_key = os.getenv("TWELVE_DATA_API_KEY")

def setup_websocket():
    """Setup WebSocket connection to Twelve Data API"""
    global ws_connection
    
    def on_open(ws):
        print("WebSocket opened")
    
    def on_message(ws, message):
        try:
            data = json.loads(message)
            # Emit price updates to all connected clients
            socketio.emit('price_update', data)
        except json.JSONDecodeError as e:
            print(f"Error parsing WebSocket message: {e}")
    
    def on_error(ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed")
    
    ws_connection = websocket.WebSocketApp(
        f"wss://ws.twelvedata.com/v1/quotes/price?apikey={api_key}",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    try:
        # Run WebSocket in a separate thread
        threading.Thread(target=ws_connection.run_forever, daemon=True).start()
    except Exception as e:
        print(f"Error starting WebSocket: {e}")

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to stock symbol updates"""
    global ws_connection
    
    if not ws_connection:
        setup_websocket()
        return
    
    symbol = data.get('symbol')
    if not symbol:
        emit('error', {'message': 'Symbol required'})
        return
    
    # Subscribe to symbol
    message = {
        "action": "subscribe",
        "params": {
            "symbols": symbol.upper(),
            "apikey": api_key
        }
    }
    
    try:
        ws_connection.send(json.dumps(message))
        join_room(f"symbol_{symbol.upper()}")
        emit('subscribed', {'symbol': symbol.upper()})
    except Exception as e:
        emit('error', {'message': f'Subscription failed: {str(e)}'})

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Unsubscribe from stock symbol updates"""
    global ws_connection
    
    if not ws_connection:
        return
    
    symbol = data.get('symbol')
    if not symbol:
        return
    
    # Unsubscribe from symbol
    message = {
        "action": "unsubscribe",
        "params": {
            "symbols": symbol.upper(),
            "apikey": api_key
        }
    }
    
    try:
        ws_connection.send(json.dumps(message))
        leave_room(f"symbol_{symbol.upper()}")
        emit('unsubscribed', {'symbol': symbol.upper()})
    except Exception as e:
        emit('error', {'message': f'Unsubscription failed: {str(e)}'})

@socketio.on('reset')
def handle_reset():
    """Reset WebSocket subscriptions"""
    global ws_connection
    
    if not ws_connection:
        return
    
    message = {
        "action": "reset",
        "params": {
            "apikey": api_key
        }
    }
    
    try:
        ws_connection.send(json.dumps(message))
        emit('reset_complete')
    except Exception as e:
        emit('error', {'message': f'Reset failed: {str(e)}'})

# Initialize WebSocket connection when module is imported
setup_websocket()
