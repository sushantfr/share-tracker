"""
Market overview service for fetching multiple stocks
"""
import yfinance as yf
from typing import List, Dict, Any
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.config import config
from backend.database import db

class MarketService:
    def __init__(self):
        self.tracked_stocks = config.TRACKED_STOCKS
    
    def fetch_stock_quick(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch quick stock data for a single symbol
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            previous_close = info.get('previousClose', current_price)
            
            # Calculate change
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
                'open': info.get('open', 0),
                'previousClose': previous_close,
                'currency': info.get('currency', 'INR'),
                'lastUpdate': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return {
                'symbol': symbol,
                'name': symbol.replace('.NS', ''),
                'price': 0,
                'change': 0,
                'changePercent': 0,
                'error': str(e)
            }
    
    def fetch_market_overview(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Fetch market overview with all tracked stocks
        """
        stocks = []
        
        # Use ThreadPoolExecutor for parallel fetching
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_symbol = {
                executor.submit(self.fetch_stock_quick, symbol): symbol 
                for symbol in self.tracked_stocks
            }
            
            for future in as_completed(future_to_symbol):
                try:
                    stock_data = future.result()
                    if not stock_data.get('error'):
                        stocks.append(stock_data)
                except Exception as e:
                    print(f"Error in future: {e}")
        
        # Sort by market cap (largest first)
        stocks.sort(key=lambda x: x.get('marketCap', 0), reverse=True)
        
        # Calculate market statistics
        total_stocks = len(stocks)
        gainers = [s for s in stocks if s.get('changePercent', 0) > 0]
        losers = [s for s in stocks if s.get('changePercent', 0) < 0]
        unchanged = total_stocks - len(gainers) - len(losers)
        
        # Get top gainers and losers
        top_gainers = sorted(stocks, key=lambda x: x.get('changePercent', 0), reverse=True)[:5]
        top_losers = sorted(stocks, key=lambda x: x.get('changePercent', 0))[:5]
        
        # Calculate average change
        avg_change = sum(s.get('changePercent', 0) for s in stocks) / total_stocks if total_stocks else 0
        
        return {
            'stocks': stocks,
            'statistics': {
                'total': total_stocks,
                'gainers': len(gainers),
                'losers': len(losers),
                'unchanged': unchanged,
                'avgChange': round(avg_change, 2)
            },
            'topGainers': top_gainers,
            'topLosers': top_losers,
            'lastUpdate': datetime.now().isoformat(),
            'categories': self._categorize_stocks(stocks)
        }
    
    def _categorize_stocks(self, stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Categorize stocks by sector
        """
        categories = {}
        
        for category_name, symbols in config.MARKET_CATEGORIES.items():
            category_stocks = [s for s in stocks if s['symbol'] in symbols]
            if category_stocks:
                avg_change = sum(s.get('changePercent', 0) for s in category_stocks) / len(category_stocks)
                categories[category_name] = {
                    'stocks': category_stocks,
                    'avgChange': round(avg_change, 2),
                    'count': len(category_stocks)
                }
        
        return categories
    
    def search_stocks(self, query: str, stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Search stocks by symbol or name
        """
        query = query.lower()
        return [
            s for s in stocks 
            if query in s.get('symbol', '').lower() or query in s.get('name', '').lower()
        ]

# Create global market service instance
market_service = MarketService()
