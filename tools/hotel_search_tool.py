# tools/hotel_search_tool.py
from langchain.tools import tool
import requests
from core.config import settings
from typing import List, Dict, Any


@tool("hotel_search")
def hotel_search(
    city_name: str, check_in_date: str, check_out_date: str, num_adults: int = 1
) -> List[Dict[str, Any]]:
    """
    Searches for hotels in a given city using a real-time Booking.com API.
    """
    url = "https://booking-com.p.rapidapi.com/v1/hotels/search-by-destination"
    querystring = {
        "dest_type": "city",
        "checkin_date": check_in_date,
        "checkout_date": check_out_date,
        "adults_number": str(num_adults),
        "order_by": "popularity",
        "units": "metric",
        "room_number": "1",
        "locale": "en-gb",
        "currency": "INR",
        "dest_name": city_name,
    }
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com",
    }
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        response.raise_for_status()
        data = response.json()

        if not data.get("result"):
            return [{"error": "No hotels found for the given location and dates."}]

        hotel_options = []
        for hotel in data["result"][:3]:
            hotel_options.append(
                {
                    "name": hotel.get("hotel_name", "N/A"),
                    "rating": hotel.get("class", 0.0),
                    "price_per_night": f"{hotel.get('min_total_price', 0)} {hotel.get('currency_code', '')}",
                    "review_score": hotel.get("review_score", 0.0),
                }
            )
        return hotel_options
    except requests.RequestException as e:
        return [{"error": f"API request failed: {e}"}]
    except Exception as e:
        return [{"error": f"An unexpected error occurred: {e}"}]
