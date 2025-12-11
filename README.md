# Real-Time Stock Tracker with AI Predictions

A professional real-time stock tracking platform with AI-powered predictions, news sentiment analysis, and market overview for 60+ NSE stocks.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Server
```bash
python server.py
```

### 3. Open Browser
Navigate to: **http://localhost:5000**

## ✨ Features

### 📊 Stock Analysis
- Real-time stock data from Yahoo Finance
- AI-powered 10-day price predictions
- News sentiment analysis integration
- Interactive price charts with confidence intervals
- Key metrics: 52W High/Low, Volume, Volatility

### 🌐 Market Overview
- View 60+ NSE stocks in real-time
- Market statistics (Gainers, Losers, Avg Change)
- Top gainers/losers cards
- Filter by sector (Banking, IT, Auto, Pharma, etc.)
- Search and sort functionality

### 📰 News & Sentiment
- Stock-specific news fetching
- Sentiment analysis (Positive/Negative/Neutral)
- Overall sentiment score with confidence
- News impact on price predictions

### ⚡ Real-Time Updates
- WebSocket connection for live data
- Market stats update every 30 seconds
- Connection status indicator

## 🎯 How to Use

### Analyze a Stock
1. Enter stock symbol (e.g., `TATASTEEL.NS`, `RELIANCE.NS`)
2. Click **Analyze** button
3. View AI predictions, news, and charts

### View Market Overview
1. Click **Market Overview** tab
2. Browse all tracked stocks
3. Filter by sector or search
4. Click any stock to analyze

## 🔧 Configuration

### Optional: Add News API Key
1. Sign up at https://newsapi.org (free tier)
2. Create `.env` file:
```env
NEWS_API_KEY=your_api_key_here
```
3. Restart server

Without API key, mock news data is used.

## 📁 Project Structure

```
Shares tracker/
├── backend/              # Backend services
│   ├── config.py         # Configuration & stock lists
│   ├── database.py       # SQLite caching
│   ├── news_service.py   # News & sentiment
│   ├── market_service.py # Market overview
│   └── prediction_service.py # AI predictions
├── server.py             # Flask server with WebSocket
├── index.html            # UI with tabs
├── app.js                # Main app logic
├── market.js             # Market overview
├── news.js               # News display
├── styles.css            # Styling
└── requirements.txt      # Dependencies
```

## 🛠️ Tech Stack

**Backend:**
- Flask + Flask-SocketIO (WebSocket)
- yfinance (Stock data)
- TextBlob (Sentiment analysis)
- SQLite (Caching)

**Frontend:**
- Vanilla JavaScript
- Chart.js (Charts)
- Socket.IO (Real-time)
- Premium dark theme UI

## 📈 Tracked Stocks

- **Nifty 50**: All top 50 NSE stocks
- **Popular**: Additional high-volume stocks
- **Total**: 60 stocks

Edit `backend/config.py` to add more stocks.

## 🎨 Features in Detail

### AI Predictions
- Combines ARIMA forecasting (70%) + News sentiment (30%)
- 10-day ahead predictions
- 95% confidence intervals
- Sentiment-adjusted forecasts

### Market Overview
- Parallel fetching for fast loading
- Real-time price updates
- Sector categorization
- Sortable by price, change%, volume

### News Integration
- Recent news for each stock
- Sentiment scoring (-1 to +1)
- Confidence percentage
- Color-coded badges

## 🚀 Deployment

Ready to deploy to:
- **Vercel** (Recommended for serverless)
- **Render/Railway** (Free tier available)
- **Heroku** (Paid)

See `VERCEL_DEPLOY.md` for deployment instructions.

## ⚠️ Disclaimer

This application is for **educational purposes only**. Stock market investments are subject to market risks. Past performance is not indicative of future results. Please consult with a financial advisor before making investment decisions.

## 📝 License

Open source for educational purposes.

---

**Happy Investing! 📈**

For detailed documentation, see [walkthrough.md](file:///.gemini/antigravity/brain/1b04c885-4e04-4ee0-a487-0aca58bc64b1/walkthrough.md)
