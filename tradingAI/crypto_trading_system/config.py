import os

COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not COINMARKETCAP_API_KEY or not NEWS_API_KEY:
    raise ValueError("API keys not set in environment variables.")
