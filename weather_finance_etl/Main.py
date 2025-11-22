import requests
import csv
import time
from datetime import datetime, timedelta
import pandas as pd
from api_client.openweathermap_client import OpenWeatherClient
from api_client.alphavantage_client import AlphaVantageClient
from dotenv import load_dotenv
import os

load_dotenv()
OWM = OpenWeatherClient()
AV = None
try:
    AV = AlphaVantageClient()
except Exception:
    pass

def kelvin_to_fahrenheit(temp_c):
    if temp_c is None:
        return None
    return (temp_c * 9.0 / 5.0) + 32.0

def write_weather_csv(cities, out_path="WeatherData_combined.csv"):
    all_data = []
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "City","Country","Description","Temp_C","Temp_F","FeelsLike_C","FeelsLike_F",
            "MinTemp_C","MinTemp_F","MaxTemp_C","MaxTemp_F","Pressure","Humidity",
            "WindSpeed","Time_of_Record","Sunrise","Sunset","fetched_at_utc"
        ])

        for city in cities:
            print(f"Fetching weather for: {city}")
            try:
                raw = OWM.fetch_current_weather(city)
                if raw is None:
                    print(f"No data returned for {city}. Skipping.")
                    continue
            except ValueError as e:
                print(f"Skipping {city}: {e}")
                continue
            except RuntimeError as e:
                print(f"API error for {city}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error for {city}: {e}")
                continue

            try:
                df = pd.DataFrame([{
                    "City": raw.get("name"),
                    "Country": raw.get("sys", {}).get("country"),
                    "Description": raw.get("weather", [{}])[0].get("description"),
                    "Temp_C": raw.get("main", {}).get("temp"),
                    "Temp_F": kelvin_to_fahrenheit(raw.get("main", {}).get("temp")),
                    "FeelsLike_C": raw.get("main", {}).get("feels_like"),
                    "FeelsLike_F": kelvin_to_fahrenheit(raw.get("main", {}).get("feels_like")),
                    "MinTemp_C": raw.get("main", {}).get("temp_min"),
                    "MinTemp_F": kelvin_to_fahrenheit(raw.get("main", {}).get("temp_min")),
                    "MaxTemp_C": raw.get("main", {}).get("temp_max"),
                    "MaxTemp_F": kelvin_to_fahrenheit(raw.get("main", {}).get("temp_max")),
                    "Pressure": raw.get("main", {}).get("pressure"),
                    "Humidity": raw.get("main", {}).get("humidity"),
                    "WindSpeed": raw.get("wind", {}).get("speed"),
                    "Time_of_Record": datetime.utcfromtimestamp(raw.get("dt")),
                    "Sunrise": datetime.utcfromtimestamp(raw.get("sys", {}).get("sunrise")),
                    "Sunset": datetime.utcfromtimestamp(raw.get("sys", {}).get("sunset")),
                    "fetched_at_utc": datetime.utcnow()
                }])
                
                if not df.empty:
                    row = df.iloc[0].tolist()
                    writer.writerow(row)
                    all_data.append(row)
                    print(f"Successfully fetched data for {city}")
                else:
                    print(f"Empty DataFrame for {city}")
                    
            except Exception as e:
                print(f"Error processing data for {city}: {e}")
                continue
                
            time.sleep(1)

    print("Total weather records written:", len(all_data))
    return out_path

def write_finance_csv(symbols, interval="Daily", outputsize="compact", out_path="FinanceData_combined.csv", start_date=None, end_date=None):
    if AV is None:
        raise RuntimeError("Alpha Vantage client not configured. Set ALPHAVANTAGE_API_KEY in .env.")
    all_data = []
    
    if start_date:
        try:
            start_date = pd.to_datetime(start_date)
            print(f"Filtering from: {start_date}")
        except Exception as e:
            print(f"Invalid start date '{start_date}': {e}")
            start_date = None
    
    if end_date:
        try:
            end_date = pd.to_datetime(end_date)
            print(f"Filtering until: {end_date}")
        except Exception as e:
            print(f"Invalid end date '{end_date}': {e}")
            end_date = None
    
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Symbol","Datetime","Open","High","Low","Close","Volume","fetched_at_utc"])

        for symbol in symbols:
            print(f"\nFetching timeseries for: {symbol}")
            try:
                if interval.lower() == "intraday":
                    print("Fetching INTRADAY data (60min intervals)...")
                    raw = AV.fetch_intraday(symbol, interval="60min", outputsize=outputsize)
                else:
                    print("Fetching DAILY data...")
                    raw = AV.fetch_daily(symbol, outputsize=outputsize)
                
                print(f"API response keys: {list(raw.keys())}")
                if "Error Message" in raw:
                    print(f"API Error: {raw['Error Message']}")
                    continue
                if "Note" in raw:
                    print(f"API Note: {raw['Note']}")
                
            except ValueError as e:
                print(f"Skipping {symbol}: {e}")
                continue
            except RuntimeError as e:
                print(f"API error for {symbol}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error for {symbol}: {e}")
                continue

            ts_key = None
            for k in raw.keys():
                if "Time Series" in k:
                    ts_key = k
                    break
            
            if ts_key is None:
                print(f"No time series data found for {symbol}! Available keys: {list(raw.keys())}")
                continue
            
            ts = raw[ts_key]
            print(f"Found {len(ts)} total records in time series")
            sample_dates = list(ts.keys())[:3]
            print(f"Sample timestamps: {sample_dates}")
            
            records_processed = 0
            records_written = 0
            records_filtered = 0
            
            for dt_str, metrics in ts.items():
                records_processed += 1
                try:
                    dt = pd.to_datetime(dt_str)
                    if records_processed <= 3:
                        print(f"Processing: {dt_str} -> {dt}")
                    
                    skip_reason = None
                    if start_date and dt < start_date:
                        skip_reason = f"before start_date ({start_date.date()})"
                    elif end_date and dt > end_date:
                        skip_reason = f"after end_date ({end_date.date()})"
                    
                    if skip_reason:
                        records_filtered += 1
                        if records_processed <= 3:
                            print(f"Skipped: {skip_reason}")
                        continue
                    
                    vals = list(metrics.values())
                    if len(vals) >= 5:
                        open_p = float(vals[0])
                        high_p = float(vals[1])
                        low_p = float(vals[2])
                        close_p = float(vals[3])
                        volume = int(float(vals[4]))
                        row = [symbol, dt, open_p, high_p, low_p, close_p, volume, datetime.utcnow()]
                        writer.writerow(row)
                        all_data.append(row)
                        records_written += 1
                        if records_written <= 3:
                            print(f"Written: {dt.date()} O:{open_p:.2f} H:{high_p:.2f} L:{low_p:.2f} C:{close_p:.2f}")
                    else:
                        print(f"Insufficient data fields: {vals}")
                        
                except Exception as e:
                    print(f"Error processing record {dt_str} for {symbol}: {e}")
                    continue
            
            print(f"Summary for {symbol}: {records_processed} processed, {records_filtered} filtered, {records_written} written")
            
            if records_written == 0 and records_processed > 0:
                print("All records were filtered out. Try adjusting date range.")
                print(f"Data range available: {list(ts.keys())[0]} to {list(ts.keys())[-1]}")
            
            time.sleep(12)

    print(f"Total finance records written: {len(all_data)}")
    if len(all_data) == 0:
        print("No data written. Possible issues:")
        print("  - API rate limits reached")
        print("  - Invalid symbol")
        print("  - Date range doesn't match available data")
        print("  - API key issues")
    
    return out_path

if __name__ == "__main__":
    mode = input("Export (weather/finance/both)?: ").strip().lower()
    
    if mode == "weather":
        cities_raw = input("Enter cities separated by comma (example: Portland,London,Karachi): ")
        cities = [c.strip() for c in cities_raw.split(",") if c.strip()]
        if cities:
            out = write_weather_csv(cities)
            print("Saved:", out)
        else:
            print("No valid cities provided.")
            
    elif mode == "finance":
        syms_raw = input("Enter symbols separated by comma (example: AAPL,MSFT): ")
        syms = [s.strip().upper() for s in syms_raw.split(",") if s.strip()]
        if syms:
            interval = input("Interval (Daily/Intraday) [Daily]: ") or "Daily"
            start_date = input("Start date (YYYY-MM-DD) or blank: ") or None
            end_date = input("End date (YYYY-MM-DD) or blank: ") or None
            out = write_finance_csv(syms, interval=interval, start_date=start_date, end_date=end_date)
            print("Saved:", out)
        else:
            print("No valid symbols provided.")
            
    elif mode == "both":
        cities_raw = input("Cities (comma separated): ")
        cities = [c.strip() for c in cities_raw.split(",") if c.strip()]
        syms_raw = input("Symbols (comma separated): ")
        syms = [s.strip().upper() for s in syms_raw.split(",") if s.strip()]
        
        if cities:
            write_weather_csv(cities, out_path="WeatherData_combined.csv")
        else:
            print("No valid cities provided for weather data.")
            
        if syms:
            write_finance_csv(syms, out_path="FinanceData_combined.csv")
        else:
            print("No valid symbols provided for finance data.")
            
        print("Saved both CSVs.")
        
    else:
        print("Invalid mode selected. Please choose 'weather', 'finance', or 'both'.")
