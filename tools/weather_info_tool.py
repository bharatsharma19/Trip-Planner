from langchain.tools import tool
import requests
from core.config import settings


@tool("weather_info")
def weather_info(location: str) -> str:
    """Get current weather information for a given city."""
    api_key = settings.WEATHER_API_KEY
    if not api_key:
        return "Error: WEATHER_API_KEY is not set."
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "current" in data:
            weather = data["current"]
            return (
                f"The current weather in {location} is {weather['temp_c']}°C "
                f"and feels like {weather['feelslike_c']}°C. "
                f"The condition is {weather['condition']['text']} with {weather['humidity']}% humidity."
            )
        else:
            return f"Could not fetch weather for {location}. The API might not recognize the location or there might be an issue."
    except Exception as e:
        return f"Weather API error: {e}"
