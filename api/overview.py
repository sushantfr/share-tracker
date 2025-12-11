from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import yfinance as yf
from datetime import datetime, timedelta
import json
import sys
from concurrent.futures import ThreadPoolExecutor

# Stock lists
NIFTY_50 = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
    'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
    'TITAN.NS', 'BAJFINANCE.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS', 'WIPRO.NS',
    'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'M&M.NS', 'TATAMOTORS.NS',
    'TATASTEEL.NS', 'TECHM.NS', 'HCLTECH.NS', 'INDUSINDBK.NS', 'ADANIPORTS.NS'
]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Enable CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            response = self.get_market_overview()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def get_market_overview(self):
        """Get today's prices for all stocks"""
        stocks = []
        
        def fetch_stock(symbol):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                previous_close = info.get('previousClose', current_price)
                
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close else 0
                
                return {
                    'symbol': symbol,
                    'name': info.get('longName', symbol.replace('.NS', '')),
                    'price': round(current_price, 2),
                    'change': round(change, 2),
                    'changePercent': round(change_percent, 2),
                    'volume': info.get('volume', 0),
                    'marketCap': info.get('marketCap', 0),
                    'high': info.get('dayHigh', 0),
                    'low': info.get('dayLow', 0),
                    'currency': info.get('currency', 'INR')
                }
            except:
                return None
        
        # Fetch stocks in parallel (limit to 10 concurrent to avoid rate limiting)
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(fetch_stock, NIFTY_50[:30]))  # Limit to 30 for speed
        
        stocks = [s for s in results if s is not None]
        stocks.sort(key=lambda x: x.get('marketCap', 0), reverse=True)
        
        # Calculate statistics
        total_stocks = len(stocks)
        gainers = [s for s in stocks if s.get('changePercent', 0) > 0]
        losers = [s for s in stocks if s.get('changePercent', 0) < 0]
        avg_change = sum(s.get('changePercent', 0) for s in stocks) / total_stocks if total_stocks else 0
        
        top_gainers = sorted(stocks, key=lambda x: x.get('changePercent', 0), reverse=True)[:5]
        top_losers = sorted(stocks, key=lambda x: x.get('changePercent', 0))[:5]
        
        return {
            'stocks': stocks,
            'statistics': {
                'total': total_stocks,
                'gainers': len(gainers),
                'losers': len(losers),
                'avgChange': round(avg_change, 2)
            },
            'topGainers': top_gainers,
            'topLosers': top_losers,
            'lastUpdate': datetime.now().isoformat()
        }
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
