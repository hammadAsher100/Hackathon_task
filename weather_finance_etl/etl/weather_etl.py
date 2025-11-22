import pandas as pd
from datetime import datetime

def transform_weather(raw):
    if raw is None:
        return None

    df = pd.DataFrame([{
        "city": raw.get("name"),
        "country": raw["sys"].get("country"),
        "description": raw["weather"][0].get("description"),
        "temp": raw["main"].get("temp"),
        "humidity": raw["main"].get("humidity"),
        "wind": raw["wind"].get("speed"),
        "timestamp": datetime.utcfromtimestamp(raw["dt"])
    }])

    return df
