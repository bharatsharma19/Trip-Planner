from langchain.tools import tool
import requests
from core.config import settings


@tool("currency_converter")
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert currency using Exchange Rates API."""
    api_key = settings.EXCHANGE_RATES_API_KEY
    if not api_key:
        return "Error: EXCHANGE_RATES_API_KEY is not set."
    url = (
        f"https://v6.exchangerate-api.com/v6/{api_key}/pair/"
        f"{from_currency}/{to_currency}/{amount}"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("result") == "success":
            converted = data["conversion_result"]
            return f"{amount} {from_currency} is approximately {converted:.2f} {to_currency}"
        else:
            return (
                f"Currency conversion failed: {data.get('error-type', 'Unknown error')}"
            )
    except Exception as e:
        return f"Currency conversion error: {e}"
