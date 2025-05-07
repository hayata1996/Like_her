import yfinance as yf
from datetime import datetime
import sys
import os


# Base directory for data storage
DATA_DIR = os.environ.get("DATA_DIR", "/data")
MODEL_PATH = os.environ.get("MODEL_PATH", "/data/models")

# AI Platform configuration
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION", "us-central1")
AGENT_ID = os.environ.get("AGENT_ID")

def main():
    symbol = "AAPL"
    period = "1mo"  # You can change this to "1d", "5d", "1y", etc.
    print(f"Testing yfinance with symbol: {symbol}")
    try:
        # Use yfinance to get real stock data
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        # Reset index to make Date a column
        hist.reset_index(inplace=True)
        
        # Convert datetime to string for JSON serialization
        hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
        
        # Add moving averages
        hist['MA5'] = hist['Close'].rolling(window=5).mean()
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        
        # Get company name
        info = stock.info
        company_name = info.get('shortName', symbol)
        
        # Convert to dict for JSON response
        data = {
            "dates": hist['Date'].tolist(),
            "open": hist['Open'].tolist(),
            "high": hist['High'].tolist(),
            "low": hist['Low'].tolist(),
            "close": hist['Close'].tolist(),
            "volume": hist['Volume'].tolist(),
            "ma5": hist['MA5'].tolist(),
            "ma20": hist['MA20'].tolist(),
            "symbol": symbol,
            "name": company_name
        }

        
        print(data)
    except Exception as e:
        print(f"❌ Error fetching data from yfinance: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()