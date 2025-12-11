"""
Enhanced prediction service combining ARIMA with news sentiment
"""
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
from backend.config import config
from backend.news_service import news_service
from backend.database import db

class PredictionService:
    def __init__(self):
        self.forecast_days = config.FORECAST_DAYS
        self.sentiment_weight = config.SENTIMENT_WEIGHT
    
    def predict_with_sentiment(self, symbol: str, prices: List[float], 
                               use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate prediction combining ARIMA forecast with news sentiment
        """
        # Check cache first
        if use_cache:
            cached = db.get_cached_prediction(symbol, max_age_seconds=3600)
            if cached:
                return cached['forecast_data']
        
        # Get ARIMA forecast (basic implementation)
        arima_forecast = self._arima_forecast(prices)
        
        # Get news sentiment
        news_items = news_service.fetch_stock_news(symbol)
        sentiment = news_service.get_overall_sentiment(news_items)
        
        # Adjust forecast based on sentiment
        adjusted_forecast = self._adjust_forecast_with_sentiment(
            arima_forecast, 
            sentiment['score'],
            prices[-1]
        )
        
        # Calculate confidence intervals
        confidence_intervals = self._calculate_confidence_intervals(
            adjusted_forecast['values'],
            prices,
            sentiment['confidence']
        )
        
        result = {
            'values': adjusted_forecast['values'],
            'confidenceIntervals': confidence_intervals,
            'sentiment': sentiment,
            'factors': {
                'arima_contribution': 1 - self.sentiment_weight,
                'sentiment_contribution': self.sentiment_weight,
                'base_volatility': adjusted_forecast['volatility'],
                'sentiment_adjustment': adjusted_forecast['sentiment_adjustment']
            },
            'news_count': len(news_items),
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache the prediction
        db.cache_prediction(symbol, result, sentiment['score'])
        
        return result
    
    def _arima_forecast(self, prices: List[float]) -> Dict[str, Any]:
        """
        Simple ARIMA-like forecast using autoregression
        """
        p = config.ARIMA_ORDER['p']
        d = config.ARIMA_ORDER['d']
        
        # Differencing
        diff_data = list(prices)
        for _ in range(d):
            diff_data = self._difference(diff_data)
        
        # Calculate AR coefficients
        coefficients = self._calculate_ar_coefficients(diff_data, p)
        
        # Generate forecast
        forecast_diff = []
        working_data = list(diff_data)
        
        for _ in range(self.forecast_days):
            next_value = sum(
                coefficients[j] * working_data[-(j+1)] 
                for j in range(min(p, len(working_data)))
            )
            forecast_diff.append(next_value)
            working_data.append(next_value)
        
        # Integrate back
        forecast = self._integrate(forecast_diff, prices[-1], d)
        
        # Calculate volatility
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        volatility = np.std(returns) * np.sqrt(252)  # Annualized
        
        return {
            'values': forecast,
            'volatility': volatility
        }
    
    def _adjust_forecast_with_sentiment(self, arima_forecast: Dict[str, Any], 
                                       sentiment_score: float, 
                                       current_price: float) -> Dict[str, Any]:
        """
        Adjust ARIMA forecast based on news sentiment
        """
        forecast_values = arima_forecast['values']
        
        # Calculate sentiment-based adjustment
        # Sentiment score ranges from -1 to 1
        # We'll adjust the trend based on sentiment
        sentiment_adjustment = sentiment_score * self.sentiment_weight
        
        adjusted_values = []
        for i, value in enumerate(forecast_values):
            # Progressive adjustment (more impact on later predictions)
            day_weight = (i + 1) / len(forecast_values)
            adjustment_factor = 1 + (sentiment_adjustment * day_weight * 0.1)  # Max 10% adjustment
            adjusted_value = value * adjustment_factor
            adjusted_values.append(adjusted_value)
        
        return {
            'values': adjusted_values,
            'volatility': arima_forecast['volatility'],
            'sentiment_adjustment': sentiment_adjustment
        }
    
    def _calculate_confidence_intervals(self, forecast: List[float], 
                                       historical_prices: List[float],
                                       sentiment_confidence: float) -> List[Dict[str, float]]:
        """
        Calculate confidence intervals for forecast
        """
        # Calculate standard error from historical data
        returns = [(historical_prices[i] - historical_prices[i-1]) / historical_prices[i-1] 
                   for i in range(1, len(historical_prices))]
        std_error = np.std(returns)
        
        # Adjust confidence based on sentiment confidence
        confidence_factor = 1.96 * (1 + (1 - sentiment_confidence) * 0.5)
        
        intervals = []
        for i, value in enumerate(forecast):
            # Widening interval over time
            margin = confidence_factor * std_error * value * np.sqrt(i + 1)
            intervals.append({
                'lower': max(0, value - margin),
                'upper': value + margin
            })
        
        return intervals
    
    def _difference(self, data: List[float]) -> List[float]:
        """Calculate first difference of series"""
        return [data[i] - data[i-1] for i in range(1, len(data))]
    
    def _integrate(self, diff_data: List[float], last_value: float, order: int) -> List[float]:
        """Integrate differenced series back to original scale"""
        result = []
        cumsum = last_value
        
        for value in diff_data:
            cumsum += value
            result.append(cumsum)
        
        return result
    
    def _calculate_ar_coefficients(self, data: List[float], p: int) -> List[float]:
        """Calculate autoregressive coefficients"""
        n = len(data)
        coefficients = []
        
        for lag in range(1, p + 1):
            if lag >= n:
                coefficients.append(0.0)
                continue
            
            # Simple autocorrelation-based coefficient
            numerator = sum(data[i] * data[i - lag] for i in range(lag, n))
            denominator = sum(data[i] ** 2 for i in range(n))
            
            if denominator > 0:
                coef = numerator / denominator
            else:
                coef = 0.0
            
            coefficients.append(coef)
        
        # Normalize coefficients
        total = sum(abs(c) for c in coefficients)
        if total > 0:
            coefficients = [c / total * 0.8 for c in coefficients]  # Damping factor
        
        return coefficients

# Create global prediction service instance
prediction_service = PredictionService()
