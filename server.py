from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import yfinance as yf
from datetime import datetime, timedelta
import threading
import time

# Import backend services
from backend.config import config
from backend.database import db
from backend.news_service import news_service
from backend.market_service import market_service
from backend.prediction_service import prediction_service

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = config.SECRET_KEY
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state for real-time updates
active_connections = 0
market_data_cache = {}

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Original stock data endpoint - enhanced with caching"""
    try:
        # Check cache first
        cached = db.get_cached_stock_price(symbol, config.CACHE_TIMEOUT)
        if cached:
            return jsonify(cached['data'])
        
        # Download 1 year of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Fetch data using yfinance
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, interval='1d')
        
        if data.empty:
            return jsonify({'error': 'No data available for this symbol'}), 404
        
        # Get ticker info
        info = ticker.info
        
        # Prepare response
        response = {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'currency': info.get('currency', 'INR'),
            'dates': [date.strftime('%Y-%m-%d') for date in data.index],
            'prices': data['Close'].tolist(),
            'volumes': data['Volume'].tolist(),
            'currentPrice': float(data['Close'].iloc[-1]),
            'previousPrice': float(data['Close'].iloc[-2]) if len(data) > 1 else float(data['Close'].iloc[-1])
        }
        
        # Cache the data
        current_price = response['currentPrice']
        previous_price = response['previousPrice']
        change_percent = ((current_price - previous_price) / previous_price * 100) if previous_price else 0
        db.cache_stock_price(symbol, current_price, change_percent, 
                            int(data['Volume'].iloc[-1]), response)
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/overview')
def get_market_overview():
    """Get market overview with all tracked stocks"""
    try:
        overview = market_service.fetch_market_overview()
        return jsonify(overview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>/news')
def get_stock_news(symbol):
    """Get news for a specific stock"""
    try:
        news = news_service.fetch_stock_news(symbol)
        sentiment = news_service.get_overall_sentiment(news)
        
        return jsonify({
            'symbol': symbol,
            'news': news,
            'sentiment': sentiment
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/news')
def get_market_news():
    """Get general market news"""
    try:
        news = news_service.fetch_market_news()
        sentiment = news_service.get_overall_sentiment(news)
        
        return jsonify({
            'news': news,
            'sentiment': sentiment
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>/predict')
def get_stock_prediction(symbol):
    """Get AI-powered prediction with news sentiment"""
    try:
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, interval='1d')
        
        if data.empty:
            return jsonify({'error': 'No data available for this symbol'}), 404
        
        prices = data['Close'].tolist()
        
        # Get prediction with sentiment
        prediction = prediction_service.predict_with_sentiment(symbol, prices)
        
        return jsonify({
            'symbol': symbol,
            'prediction': prediction,
            'currentPrice': float(data['Close'].iloc[-1])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_stocks():
    """Search stocks by query"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        # Get market overview
        overview = market_service.fetch_market_overview()
        
        # Search in stocks
        results = market_service.search_stocks(query, overview['stocks'])
        
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/<symbol>')
def get_prediction(symbol):
    """Get prediction for Future Predictions tab (matches Vercel API)"""
    try:
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, interval='1d')
        
        if data.empty:
            return jsonify({'error': 'No data available for this symbol'}), 404
        
        prices = data['Close'].tolist()
        current_price = float(data['Close'].iloc[-1])
        
        # Get prediction with sentiment
        prediction = prediction_service.predict_with_sentiment(symbol, prices)
        
        return jsonify({
            'symbol': symbol,
            'currentPrice': current_price,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket events for real-time updates
@socketio.on('connect')
def handle_connect():
    global active_connections
    active_connections += 1
    print(f'Client connected. Active connections: {active_connections}')
    emit('connection_status', {'status': 'connected', 'message': 'Real-time updates enabled'})

@socketio.on('disconnect')
def handle_disconnect():
    global active_connections
    active_connections -= 1
    print(f'Client disconnected. Active connections: {active_connections}')

@socketio.on('subscribe_stock')
def handle_subscribe(data):
    """Subscribe to real-time updates for a stock"""
    symbol = data.get('symbol')
    print(f'Client subscribed to {symbol}')
    emit('subscribed', {'symbol': symbol})

@socketio.on('unsubscribe_stock')
def handle_unsubscribe(data):
    """Unsubscribe from stock updates"""
    symbol = data.get('symbol')
    print(f'Client unsubscribed from {symbol}')
    emit('unsubscribed', {'symbol': symbol})

def broadcast_market_updates():
    """Background task to broadcast market updates"""
    while True:
        time.sleep(config.REALTIME_UPDATE_INTERVAL)
        
        if active_connections > 0:
            try:
                # Fetch quick market update
                overview = market_service.fetch_market_overview(use_cache=False)
                
                # Broadcast to all connected clients
                socketio.emit('market_update', {
                    'statistics': overview['statistics'],
                    'topGainers': overview['topGainers'][:3],
                    'topLosers': overview['topLosers'][:3],
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f'Error broadcasting updates: {e}')

# Cleanup task
def cleanup_old_data():
    """Periodic cleanup of old cached data"""
    while True:
        time.sleep(86400)  # Run daily
        try:
            db.cleanup_old_data(days=7)
            print('Cleaned up old cached data')
        except Exception as e:
            print(f'Error cleaning up data: {e}')

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Enhanced Stock Analysis Dashboard Server...")
    print("=" * 60)
    print(f"Tracking {len(config.TRACKED_STOCKS)} stocks")
    print(f"News API: {'Configured' if config.NEWS_API_KEY else 'Using mock data'}")
    print(f"Database: {config.DATABASE_PATH}")
    print(f"Real-time updates every {config.REALTIME_UPDATE_INTERVAL}s")
    print("=" * 60)
    print("Server running at: http://localhost:5000")
    print("=" * 60)
    
    # Start background tasks
    threading.Thread(target=broadcast_market_updates, daemon=True).start()
    threading.Thread(target=cleanup_old_data, daemon=True).start()
    
    # Run server with SocketIO
    socketio.run(app, debug=True, port=5000, host='0.0.0.0', allow_unsafe_werkzeug=True)
