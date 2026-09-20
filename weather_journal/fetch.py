"""Weather data fetching module via OpenWeatherMap API."""

import os
import requests

API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_current(city, api_key=None):
    """Fetches current weather for a city from OpenWeatherMap.
    
    Returns a dictionary with temperature, humidity, and condition description.
    """
    key = api_key or os.environ.get("OWM_API_KEY")
    if not key:
        raise ValueError("Missing API key. Please set OWM_API_KEY environment variable or pass --key.")

    # BUG: Missing '&units=metric', causing API to return temperatures in Kelvin
    params = {
        "q": city,
        "appid": key
    }

    resp = requests.get(API_BASE_URL, params=params, timeout=10)
    data = resp.json()

    # BUG: Directly accesses 'main' without verifying if API returned a 404 or error response
    return {
        "city": data["name"],
        "temp": round(data["main"]["temp"], 1),
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"]
    }
