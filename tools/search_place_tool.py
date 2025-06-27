from langchain.tools import tool
import requests
import os


@tool("search_place", return_direct=True)
def search_place(location: str, query: str = "tourist attractions") -> str:
    """Search for places of interest in a city using Google Places API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    url = (
        f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={query}+in+{location}&key={api_key}"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return f"No places found for {query} in {location}."
        places = [place["name"] for place in results[:5]]
        return f"Top places for {query} in {location}: {', '.join(places)}"
    except Exception as e:
        return f"Place search error: {e}"
