from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    try:
        # Download 1 year of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Fetch data using yfinance
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, interval='1d')
        
        if data.empty:
            return jsonify({'error': 'No data available for this symbol'}), 404
        
        # Get ticker info
        info = ticker.info
        
        # Prepare response
        response = {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'currency': info.get('currency', 'INR'),
            'dates': [date.strftime('%Y-%m-%d') for date in data.index],
            'prices': data['Close'].tolist(),
            'volumes': data['Volume'].tolist(),
            'currentPrice': float(data['Close'].iloc[-1]),
            'previousPrice': float(data['Close'].iloc[-2]) if len(data) > 1 else float(data['Close'].iloc[-1])
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Stock Analysis Dashboard Server...")
    print("Open your browser and navigate to: http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
