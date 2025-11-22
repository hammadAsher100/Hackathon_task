import requests
import os
import streamlit as st
import random
from datetime import datetime, timedelta

class AlphaVantageClient:
    def __init__(self):
        # Try to get API key from Streamlit secrets first, then environment
        try:
            self.api_key = st.secrets["ALPHAVANTAGE_API_KEY"]
        except:
            self.api_key = os.getenv('ALPHAVANTAGE_API_KEY')
        
        # If no API key found, show demo mode message
        self.demo_mode = not self.api_key

    def fetch_daily(self, symbol):
        if self.demo_mode:
            return self._get_demo_stock_data(symbol, "Daily")
        
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={self.api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if "Error Message" in data:
                    raise ValueError(f"Invalid symbol: {symbol}")
                return data
            else:
                raise RuntimeError(f"API error: {response.status_code}")
        except Exception as e:
            st.warning(f"Using demo data due to API error: {e}")
            return self._get_demo_stock_data(symbol, "Daily")

    def fetch_intraday(self, symbol, interval="60min"):
        if self.demo_mode:
            return self._get_demo_stock_data(symbol, "Intraday")
        
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={self.api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if "Error Message" in data:
                    raise ValueError(f"Invalid symbol: {symbol}")
                return data
            else:
                raise RuntimeError(f"API error: {response.status_code}")
        except Exception as e:
            st.warning(f"Using demo data due to API error: {e}")
            return self._get_demo_stock_data(symbol, "Intraday")

    def _get_demo_stock_data(self, symbol, interval_type):
        """Return realistic demo stock data for presentation"""
        import random
        from datetime import datetime, timedelta
        
        # Base prices for popular symbols
        base_prices = {
            "AAPL": 180, "MSFT": 330, "GOOGL": 135, "TSLA": 240, 
            "AMZN": 150, "META": 320, "NVDA": 450, "IBM": 160
        }
        
        base_price = base_prices.get(symbol, 100)  # Default to $100 for unknown symbols
        time_series = {}
        
        if interval_type == "Daily":
            # Generate 30 days of data
            for i in range(30):
                date = datetime.now() - timedelta(days=30-i)
                date_str = date.strftime("%Y-%m-%d")
                
                # Simulate realistic price movements
                open_price = base_price * (1 + random.uniform(-0.02, 0.02))
                close_price = open_price * (1 + random.uniform(-0.03, 0.03))
                high_price = max(open_price, close_price) * (1 + random.uniform(0.01, 0.03))
                low_price = min(open_price, close_price) * (1 - random.uniform(0.01, 0.03))
                volume = random.randint(1000000, 50000000)
                
                time_series[date_str] = {
                    "1. open": f"{open_price:.4f}",
                    "2. high": f"{high_price:.4f}",
                    "3. low": f"{low_price:.4f}",
                    "4. close": f"{close_price:.4f}",
                    "5. volume": f"{volume}"
                }
        else:
            # Generate intraday data (last 24 hours)
            for i in range(24):
                date = datetime.now() - timedelta(hours=24-i)
                date_str = date.strftime("%Y-%m-%d %H:%M:%S")
                
                open_price = base_price * (1 + random.uniform(-0.01, 0.01))
                close_price = open_price * (1 + random.uniform(-0.02, 0.02))
                high_price = max(open_price, close_price) * (1 + random.uniform(0.005, 0.015))
                low_price = min(open_price, close_price) * (1 - random.uniform(0.005, 0.015))
                volume = random.randint(100000, 5000000)
                
                time_series[date_str] = {
                    "1. open": f"{open_price:.4f}",
                    "2. high": f"{high_price:.4f}",
                    "3. low": f"{low_price:.4f}",
                    "4. close": f"{close_price:.4f}",
                    "5. volume": f"{volume}"
                }
        
        return {
            "Meta Data": {
                "1. Information": f"{interval_type} Prices (open, high, low, close) and Volumes",
                "2. Symbol": symbol,
                "3. Last Refreshed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "4. Output Size": "Compact",
                "5. Time Zone": "US/Eastern"
            },
            f"Time Series ({'Daily' if interval_type == 'Daily' else '60min'})": time_series
        }