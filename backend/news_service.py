"""
News fetching and sentiment analysis service
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from textblob import TextBlob
from backend.config import config
from backend.database import db

class NewsService:
    def __init__(self):
        self.api_key = config.NEWS_API_KEY
        self.base_url = 'https://newsapi.org/v2'
    
    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text using TextBlob
        Returns: score between -1 (negative) and 1 (positive)
        """
        if not text:
            return 0.0
        
        try:
            blob = TextBlob(text)
            # TextBlob polarity is between -1 and 1
            return blob.sentiment.polarity
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return 0.0
    
    def fetch_stock_news(self, symbol: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch news for a specific stock
        """
        # Check cache first
        if use_cache:
            cached_news = db.get_cached_news(symbol, config.NEWS_CACHE_TIMEOUT)
            if cached_news:
                return cached_news
        
        # Extract company name from symbol (remove .NS suffix)
        company_name = symbol.replace('.NS', '').replace('.BO', '')
        
        # Map common symbols to company names
        company_map = {
            'TATASTEEL': 'Tata Steel',
            'RELIANCE': 'Reliance Industries',
            'TCS': 'Tata Consultancy Services',
            'INFY': 'Infosys',
            'HDFCBANK': 'HDFC Bank',
            'ICICIBANK': 'ICICI Bank',
            'SBIN': 'State Bank of India',
            'WIPRO': 'Wipro',
            'MARUTI': 'Maruti Suzuki',
            'ITC': 'ITC Limited'
        }
        
        search_query = company_map.get(company_name, company_name)
        
        try:
            news = self._fetch_news_from_api(search_query)
            
            # Add sentiment scores
            for article in news:
                text = f"{article.get('title', '')} {article.get('description', '')}"
                article['sentiment_score'] = self.analyze_sentiment(text)
            
            # Cache the news
            if news:
                db.cache_news(symbol, news)
            
            return news
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []
    
    def fetch_market_news(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch general market news
        """
        # Check cache first
        if use_cache:
            cached_news = db.get_cached_news(None, config.NEWS_CACHE_TIMEOUT)
            if cached_news:
                return cached_news
        
        try:
            news = self._fetch_news_from_api('stock market India OR NSE OR BSE OR Nifty OR Sensex')
            
            # Add sentiment scores
            for article in news:
                text = f"{article.get('title', '')} {article.get('description', '')}"
                article['sentiment_score'] = self.analyze_sentiment(text)
            
            # Cache the news
            if news:
                db.cache_news(None, news)
            
            return news
        except Exception as e:
            print(f"Error fetching market news: {e}")
            return []
    
    def _fetch_news_from_api(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch news from NewsAPI
        """
        if not self.api_key:
            # Return mock data if no API key
            return self._get_mock_news(query)
        
        # Calculate date range (last 7 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=7)
        
        params = {
            'q': query,
            'apiKey': self.api_key,
            'language': config.NEWS_LANGUAGE,
            'sortBy': 'publishedAt',
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'pageSize': config.MAX_NEWS_ITEMS
        }
        
        try:
            response = requests.get(f'{self.base_url}/everything', params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                return [
                    {
                        'title': article.get('title'),
                        'description': article.get('description'),
                        'url': article.get('url'),
                        'source': article.get('source', {}).get('name'),
                        'publishedAt': article.get('publishedAt'),
                        'urlToImage': article.get('urlToImage')
                    }
                    for article in articles
                ]
            return []
        except requests.exceptions.RequestException as e:
            print(f"NewsAPI request error: {e}")
            return self._get_mock_news(query)
    
    def _get_mock_news(self, query: str) -> List[Dict[str, Any]]:
        """
        Return mock news data when API is not available
        """
        return [
            {
                'title': f'{query} shows strong market performance',
                'description': 'Market analysts predict positive trends based on recent economic indicators.',
                'url': '#',
                'source': 'Mock News',
                'publishedAt': datetime.now().isoformat(),
                'urlToImage': None,
                'sentiment_score': 0.5
            },
            {
                'title': f'Investors cautious about {query} amid global uncertainty',
                'description': 'Global economic conditions continue to impact investor sentiment.',
                'url': '#',
                'source': 'Mock News',
                'publishedAt': (datetime.now() - timedelta(hours=6)).isoformat(),
                'urlToImage': None,
                'sentiment_score': -0.2
            }
        ]
    
    def get_overall_sentiment(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall sentiment from news items
        """
        if not news_items:
            return {
                'score': 0.0,
                'label': 'Neutral',
                'confidence': 0.0
            }
        
        scores = [item.get('sentiment_score', 0.0) for item in news_items]
        avg_score = sum(scores) / len(scores)
        
        # Determine label
        if avg_score > 0.2:
            label = 'Positive'
        elif avg_score < -0.2:
            label = 'Negative'
        else:
            label = 'Neutral'
        
        # Calculate confidence (based on consistency of scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        confidence = max(0, 1 - variance)
        
        return {
            'score': avg_score,
            'label': label,
            'confidence': confidence,
            'article_count': len(news_items)
        }

# Create global news service instance
news_service = NewsService()
