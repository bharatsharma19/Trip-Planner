from langchain.tools import tool
import requests
import os


@tool("currency_converter", return_direct=True)
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert currency using Exchange Rates API."""
    api_key = os.getenv("EXCHANGE_RATES_API_KEY")
    url = (
        f"https://v6.exchangerate-api.com/v6/{api_key}/pair/"
        f"{from_currency}/{to_currency}/{amount}"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("result") == "success":
            converted = data["conversion_result"]
            return f"{amount} {from_currency} = {converted} {to_currency}"
        else:
            return (
                f"Currency conversion failed: {data.get('error-type', 'Unknown error')}"
            )
    except Exception as e:
        return f"Currency conversion error: {e}"
