from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import yfinance as yf
from datetime import datetime, timedelta
import json
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Enable CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Extract symbol from path: /api/predict/SYMBOL
            path_parts = parsed_path.path.split('/')
            symbol = None
            
            # Try to get symbol from path
            for i, part in enumerate(path_parts):
                if part == 'predict' and i + 1 < len(path_parts):
                    symbol = path_parts[i + 1]
                    break
            
            if symbol:
                response = self.get_prediction(symbol)
            else:
                response = {'error': 'Symbol not provided'}
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def get_prediction(self, symbol):
        """Get AI prediction for stock"""
        try:
            # Fetch historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if data.empty:
                return {'error': 'No data available'}
            
            prices = data['Close'].tolist()
            current_price = float(data['Close'].iloc[-1])
            
            # Simple ARIMA-like forecast
            forecast = self.simple_forecast(prices, days=10)
            
            # Calculate confidence intervals
            std_dev = np.std(prices[-30:])  # Last 30 days volatility
            confidence_intervals = []
            
            for i, value in enumerate(forecast):
                margin = 1.96 * std_dev * np.sqrt(i + 1)
                confidence_intervals.append({
                    'lower': max(0, value - margin),
                    'upper': value + margin
                })
            
            return {
                'symbol': symbol,
                'currentPrice': current_price,
                'prediction': {
                    'values': forecast,
                    'confidenceIntervals': confidence_intervals,
                    'sentiment': {
                        'score': 0.0,
                        'label': 'Neutral',
                        'confidence': 0.5,
                        'article_count': 0
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def simple_forecast(self, prices, days=10):
        """Simple moving average based forecast"""
        # Use last 30 days for trend
        recent = prices[-30:]
        
        # Calculate trend
        x = np.arange(len(recent))
        coeffs = np.polyfit(x, recent, 1)
        trend = coeffs[0]
        
        # Generate forecast
        last_price = prices[-1]
        forecast = []
        
        for i in range(1, days + 1):
            # Simple linear projection with dampening
            predicted = last_price + (trend * i * 0.8)  # 0.8 dampening factor
            forecast.append(float(predicted))
        
        return forecast
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
