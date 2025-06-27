from langchain.tools import tool
import requests
import os


@tool("weather_info", return_direct=True)
def weather_info(location: str) -> str:
    """Get weather information for a given city."""
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if "current" in data:
            weather = data["current"]
            return (
                f"Weather in {location}: {weather['temp_c']}°C, "
                f"{weather['condition']['text']}, Humidity: {weather['humidity']}%"
            )
        else:
            return f"Could not fetch weather for {location}."
    except Exception as e:
        return f"Weather API error: {e}"
