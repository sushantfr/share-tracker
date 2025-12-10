from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import yfinance as yf
from datetime import datetime, timedelta
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.split('/')
        
        # Check if this is a stock request
        if len(path_parts) >= 3 and path_parts[1] == 'api' and path_parts[2] == 'stock':
            if len(path_parts) >= 4:
                symbol = path_parts[3]
                self.get_stock_data(symbol)
            else:
                self.send_error_response('Symbol not provided', 400)
        else:
            self.send_error_response('Invalid endpoint', 404)
    
    def get_stock_data(self, symbol):
        try:
            # Download 1 year of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if data.empty:
                self.send_error_response('No data available for this symbol', 404)
                return
            
            # Get ticker info
            try:
                info = ticker.info
                name = info.get('longName', symbol)
                currency = info.get('currency', 'INR')
            except:
                name = symbol
                currency = 'INR'
            
            # Prepare response
            response = {
                'symbol': symbol,
                'name': name,
                'currency': currency,
                'dates': [date.strftime('%Y-%m-%d') for date in data.index],
                'prices': data['Close'].tolist(),
                'volumes': data['Volume'].tolist(),
                'currentPrice': float(data['Close'].iloc[-1]),
                'previousPrice': float(data['Close'].iloc[-2]) if len(data) > 1 else float(data['Close'].iloc[-1])
            }
            
            self.send_json_response(response)
        
        except Exception as e:
            self.send_error_response(str(e), 500)
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, message, code):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
