"""
Configuration settings for the stock tracker backend
"""
import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    
    # API Keys
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')  # Get from https://newsapi.org
    
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'stock_data.db')
    
    # Cache settings
    CACHE_TIMEOUT = 300  # 5 minutes for stock prices
    NEWS_CACHE_TIMEOUT = 1800  # 30 minutes for news
    MARKET_OVERVIEW_CACHE_TIMEOUT = 60  # 1 minute for market overview
    
    # Update intervals
    REALTIME_UPDATE_INTERVAL = 30  # seconds
    
    # Stock lists - Top Indian stocks
    NIFTY_50 = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
        'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
        'TITAN.NS', 'BAJFINANCE.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS', 'WIPRO.NS',
        'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'M&M.NS', 'TATAMOTORS.NS',
        'TATASTEEL.NS', 'TECHM.NS', 'HCLTECH.NS', 'INDUSINDBK.NS', 'ADANIPORTS.NS',
        'BAJAJFINSV.NS', 'COALINDIA.NS', 'DRREDDY.NS', 'GRASIM.NS', 'HEROMOTOCO.NS',
        'HINDALCO.NS', 'JSWSTEEL.NS', 'DIVISLAB.NS', 'BRITANNIA.NS', 'EICHERMOT.NS',
        'CIPLA.NS', 'SHREECEM.NS', 'UPL.NS', 'APOLLOHOSP.NS', 'TATACONSUM.NS',
        'BAJAJ-AUTO.NS', 'SBILIFE.NS', 'BPCL.NS', 'ADANIENT.NS', 'HDFCLIFE.NS'
    ]
    
    # Additional popular stocks
    POPULAR_STOCKS = [
        'YESBANK.NS', 'VEDL.NS', 'SAIL.NS', 'BANKNIFTY.NS', 'NIFTY.NS',
        'IDEA.NS', 'PNB.NS', 'RPOWER.NS', 'SUZLON.NS', 'ZEEL.NS'
    ]
    
    # Combine all tracked stocks
    TRACKED_STOCKS = list(set(NIFTY_50 + POPULAR_STOCKS))
    
    # News settings
    NEWS_SOURCES = 'bloomberg,reuters,the-wall-street-journal,financial-times'
    NEWS_LANGUAGE = 'en'
    MAX_NEWS_ITEMS = 10
    
    # Prediction settings
    FORECAST_DAYS = 10
    ARIMA_ORDER = {'p': 5, 'd': 1, 'q': 0}
    SENTIMENT_WEIGHT = 0.3  # Weight of news sentiment in prediction (0-1)
    
    # Market categories
    MARKET_CATEGORIES = {
        'banking': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'INDUSINDBK.NS'],
        'it': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
        'auto': ['MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS'],
        'pharma': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'APOLLOHOSP.NS'],
        'energy': ['RELIANCE.NS', 'ONGC.NS', 'BPCL.NS', 'NTPC.NS', 'POWERGRID.NS', 'COALINDIA.NS'],
        'metals': ['TATASTEEL.NS', 'HINDALCO.NS', 'JSWSTEEL.NS', 'VEDL.NS', 'SAIL.NS'],
        'fmcg': ['HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'TATACONSUM.NS']
    }

# Create config instance
config = Config()
