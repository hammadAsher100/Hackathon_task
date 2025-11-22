import requests
import os
import streamlit as st

class OpenWeatherClient:
    def __init__(self):
        # Try to get API key from Streamlit secrets first, then environment
        try:
            self.api_key = st.secrets["OPENWEATHER_API_KEY"]
        except:
            self.api_key = os.getenv('OPENWEATHER_API_KEY')
        
        # If no API key found, show demo mode message
        self.demo_mode = not self.api_key

    def fetch_current_weather(self, city):
        if self.demo_mode:
            # Return demo data when no API key is available
            return self._get_demo_weather_data(city)
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise ValueError(f"City '{city}' not found")
            else:
                raise RuntimeError(f"API error: {response.status_code}")
        except Exception as e:
            st.warning(f"Using demo data due to API error: {e}")
            return self._get_demo_weather_data(city)

    def _get_demo_weather_data(self, city):
        """Return realistic demo data for presentation"""
        import random
        from datetime import datetime
        
        demo_data = {
            "London": {
                "name": "London",
                "sys": {"country": "GB"},
                "weather": [{"description": "light rain"}],
                "main": {
                    "temp": 280 + random.uniform(0, 5),  # 7-12°C in Kelvin
                    "feels_like": 280 + random.uniform(0, 5),
                    "temp_min": 280 + random.uniform(0, 3),
                    "temp_max": 280 + random.uniform(2, 5),
                    "pressure": 1010 + random.randint(-10, 10),
                    "humidity": 70 + random.randint(-20, 20)
                },
                "wind": {"speed": round(random.uniform(2, 6), 2)},
                "dt": int(datetime.now().timestamp())
            },
            "New York": {
                "name": "New York",
                "sys": {"country": "US"},
                "weather": [{"description": "clear sky"}],
                "main": {
                    "temp": 285 + random.uniform(0, 5),  # 12-17°C
                    "feels_like": 285 + random.uniform(0, 5),
                    "temp_min": 285 + random.uniform(0, 3),
                    "temp_max": 285 + random.uniform(2, 5),
                    "pressure": 1015 + random.randint(-10, 10),
                    "humidity": 60 + random.randint(-20, 20)
                },
                "wind": {"speed": round(random.uniform(3, 8), 2)},
                "dt": int(datetime.now().timestamp())
            },
            "Tokyo": {
                "name": "Tokyo",
                "sys": {"country": "JP"},
                "weather": [{"description": "few clouds"}],
                "main": {
                    "temp": 290 + random.uniform(0, 5),  # 17-22°C
                    "feels_like": 290 + random.uniform(0, 5),
                    "temp_min": 290 + random.uniform(0, 3),
                    "temp_max": 290 + random.uniform(2, 5),
                    "pressure": 1012 + random.randint(-10, 10),
                    "humidity": 65 + random.randint(-20, 20)
                },
                "wind": {"speed": round(random.uniform(1, 4), 2)},
                "dt": int(datetime.now().timestamp())
            }
        }
        
        return demo_data.get(city, demo_data["London"])  # Default to London if city not in demo data