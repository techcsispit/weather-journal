"""Weather data fetching module via OpenWeatherMap API."""

import os
import requests
import time

API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

_cache = {}



def get_current(city, api_key=None):
    """Fetches current weather for a city from OpenWeatherMap.
    
    Returns a dictionary with temperature, humidity, and condition description.
    """
    city_lower = city.lower()
    if city_lower in _cache:
        cached_time, cached_data = _cache[city_lower]
        if time.time() - cached_time < 600:
            return cached_data

    key = api_key or os.environ.get("OWM_API_KEY")
    if not key:
        raise ValueError("Missing API key. Please set OWM_API_KEY environment variable or pass --key.")

    params = {
        "q": city,
        "appid": key,
        "units": "metric"
    }

    for attempt in range(3):
        try:
            resp = requests.get(API_BASE_URL, params=params, timeout=10)
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise ValueError(f"Network error: {e}")
            time.sleep(2 ** attempt)

    data = resp.json()

    if resp.status_code == 401:
        raise ValueError("Invalid API key.")
    elif resp.status_code == 404:
        raise ValueError(f"City '{city}' not found.")
    elif resp.status_code != 200:
        raise ValueError(f"API Error: {data.get('message', 'Unknown error')}")

    result = {
        "city": data["name"],
        "temp": round(data["main"]["temp"], 1),
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"]
    }
    
    _cache[city_lower] = (time.time(), result)
    return result
