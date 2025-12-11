"""
Database layer for caching stock data and news
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from backend.config import config

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Stock prices cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                change_percent REAL,
                volume INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                data JSON
            )
        ''')
        
        # News cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                title TEXT NOT NULL,
                description TEXT,
                url TEXT,
                source TEXT,
                published_at DATETIME,
                sentiment_score REAL,
                cached_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Predictions cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                forecast_data JSON NOT NULL,
                sentiment_score REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_symbol ON stock_prices(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_symbol ON news_cache(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pred_symbol ON predictions(symbol)')
        
        conn.commit()
        conn.close()
    
    def cache_stock_price(self, symbol: str, price: float, change_percent: float, 
                         volume: int, data: Dict[str, Any]):
        """Cache stock price data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO stock_prices (symbol, price, change_percent, volume, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (symbol, price, change_percent, volume, json.dumps(data)))
        
        conn.commit()
        conn.close()
    
    def get_cached_stock_price(self, symbol: str, max_age_seconds: int = 300) -> Optional[Dict[str, Any]]:
        """Get cached stock price if not expired"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)
        
        cursor.execute('''
            SELECT * FROM stock_prices 
            WHERE symbol = ? AND timestamp > ?
            ORDER BY timestamp DESC LIMIT 1
        ''', (symbol, cutoff_time))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'symbol': row['symbol'],
                'price': row['price'],
                'change_percent': row['change_percent'],
                'volume': row['volume'],
                'data': json.loads(row['data']),
                'timestamp': row['timestamp']
            }
        return None
    
    def cache_news(self, symbol: Optional[str], articles: List[Dict[str, Any]]):
        """Cache news articles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for article in articles:
            cursor.execute('''
                INSERT INTO news_cache 
                (symbol, title, description, url, source, published_at, sentiment_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                article.get('title'),
                article.get('description'),
                article.get('url'),
                article.get('source'),
                article.get('publishedAt'),
                article.get('sentiment_score', 0.0)
            ))
        
        conn.commit()
        conn.close()
    
    def get_cached_news(self, symbol: Optional[str] = None, 
                       max_age_seconds: int = 1800) -> List[Dict[str, Any]]:
        """Get cached news articles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)
        
        if symbol:
            cursor.execute('''
                SELECT * FROM news_cache 
                WHERE symbol = ? AND cached_at > ?
                ORDER BY published_at DESC
            ''', (symbol, cutoff_time))
        else:
            cursor.execute('''
                SELECT * FROM news_cache 
                WHERE cached_at > ?
                ORDER BY published_at DESC
            ''', (cutoff_time,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def cache_prediction(self, symbol: str, forecast_data: Dict[str, Any], sentiment_score: float):
        """Cache prediction data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions (symbol, forecast_data, sentiment_score)
            VALUES (?, ?, ?)
        ''', (symbol, json.dumps(forecast_data), sentiment_score))
        
        conn.commit()
        conn.close()
    
    def get_cached_prediction(self, symbol: str, max_age_seconds: int = 3600) -> Optional[Dict[str, Any]]:
        """Get cached prediction if not expired"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)
        
        cursor.execute('''
            SELECT * FROM predictions 
            WHERE symbol = ? AND created_at > ?
            ORDER BY created_at DESC LIMIT 1
        ''', (symbol, cutoff_time))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'symbol': row['symbol'],
                'forecast_data': json.loads(row['forecast_data']),
                'sentiment_score': row['sentiment_score'],
                'created_at': row['created_at']
            }
        return None
    
    def cleanup_old_data(self, days: int = 7):
        """Clean up old cached data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(days=days)
        
        cursor.execute('DELETE FROM stock_prices WHERE timestamp < ?', (cutoff_time,))
        cursor.execute('DELETE FROM news_cache WHERE cached_at < ?', (cutoff_time,))
        cursor.execute('DELETE FROM predictions WHERE created_at < ?', (cutoff_time,))
        
        conn.commit()
        conn.close()

# Create global database instance
db = Database()
