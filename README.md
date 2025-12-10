# Stock Analysis Dashboard

A professional stock price analysis dashboard with ARIMA forecasting and real-time data from Yahoo Finance.

![Dashboard Preview](https://via.placeholder.com/800x400/0a0e1a/3B82F6?text=Stock+Analysis+Dashboard)

## Features

- 📊 **Real-time stock data** from Yahoo Finance
- 📈 **ARIMA forecasting** (10-day ahead prediction)
- 💎 **Premium dark UI** with glassmorphism effects
- 📱 **Responsive design** for all devices
- ⚡ **Interactive charts** with Chart.js
- 🎯 **Key metrics**: Price, Volume, Volatility, 52W High/Low
- 🔮 **Forecast insights** with confidence intervals

## Quick Start

### Prerequisites

- Python 3.7+
- pip or conda

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd "c:\Users\91938\Desktop\Shares tracker"
   ```

2. **Install dependencies**:
   ```bash
   conda install -y flask flask-cors
   pip install yfinance
   ```

3. **Start the server**:
   ```bash
   python server.py
   ```

4. **Open your browser**:
   Navigate to `http://localhost:5000`

## Usage

### Analyzing Stocks

1. **Default Stock**: TATASTEEL.NS loads automatically
2. **Search**: Enter any NSE stock symbol (e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`)
3. **Quick Access**: Click popular stock chips for instant analysis
4. **View Forecast**: Scroll down to see 10-day price prediction with confidence intervals

### Supported Stock Symbols

Use NSE symbols with `.NS` suffix:
- `TATASTEEL.NS` - Tata Steel
- `RELIANCE.NS` - Reliance Industries
- `TCS.NS` - Tata Consultancy Services
- `INFY.NS` - Infosys
- `HDFCBANK.NS` - HDFC Bank
- And any other NSE-listed stock

## Project Structure

```
Shares tracker/
├── index.html      # Main HTML structure
├── styles.css      # Premium dark theme styling
├── app.js          # Frontend JavaScript with ARIMA
├── server.py       # Flask backend API
└── README.md       # This file
```

## Technical Details

### ARIMA Model
- **Order**: AR(5,1,0)
- **Forecast Horizon**: 10 trading days
- **Confidence Interval**: 95%

### Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js 4.4.0
- **Backend**: Flask (Python)
- **Data Source**: Yahoo Finance (via yfinance)
- **Fonts**: Inter, JetBrains Mono (Google Fonts)

### API Endpoints

- `GET /` - Serves the main dashboard
- `GET /api/stock/<symbol>` - Returns stock data in JSON format

## Features in Detail

### Stock Information Card
- Current price with real-time change
- 52-week high and low
- Average trading volume
- Data period (1 year)

### Interactive Chart
- Historical prices (blue line)
- Forecasted prices (orange dashed line)
- 95% confidence interval (shaded area)
- Hover tooltips with detailed information

### Forecast Insights
1. **Trend Analysis**: Bullish/Bearish/Neutral indicator
2. **Target Price**: 10-day ahead prediction
3. **Confidence Range**: ± range for uncertainty
4. **Volatility**: Annualized standard deviation

## Customization

### Changing Forecast Period

Edit `app.js`:
```javascript
const CONFIG = {
    FORECAST_DAYS: 10,  // Change this value
    // ...
};
```

### Changing ARIMA Parameters

Edit `app.js`:
```javascript
const CONFIG = {
    // ...
    ARIMA_ORDER: { p: 5, d: 1, q: 0 },  // Modify p, d, q
};
```

### Styling

Edit `styles.css` to customize:
- Colors (CSS variables at top of file)
- Fonts
- Spacing
- Border radius
- Animations

## Troubleshooting

### Server won't start
- Ensure Flask is installed: `pip install flask flask-cors`
- Check if port 5000 is available
- Try running with: `python server.py`

### No data loading
- Check internet connection (needs access to Yahoo Finance)
- Verify stock symbol is correct (use `.NS` for NSE stocks)
- Check browser console for errors

### Chart not displaying
- Ensure Chart.js CDN is accessible
- Check browser console for JavaScript errors
- Try refreshing the page

## Disclaimer

⚠️ **Important**: This application is for educational purposes only. Stock market investments are subject to market risks. Past performance is not indicative of future results. Please consult with a financial advisor before making investment decisions.

## License

This project is open source and available for educational purposes.

## Author

Created with ❤️ for stock market analysis and learning

---

**Happy Investing! 📈**
