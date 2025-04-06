from binance import Client

# Replace with your actual API key and secret (if needed - public data doesn't require keys)
# api_key = "YOUR_API_KEY"
# api_secret = "YOUR_API_SECRET"

# client = Client(api_key, api_secret) # Use this if you need authenticated endpoints

client = Client() # For public endpoints

def get_binance_order_book(symbol="BTCUSDT", limit=10):  # limit is the depth of the order book (number of bids/asks)
    try:
        order_book = client.get_order_book(symbol=symbol, limit=limit)
        return order_book
    except Exception as e:
        print(f"Error fetching order book from Binance: {e}")
        return None

# Example usage:
order_book = get_binance_order_book()
if order_book:
    bids = order_book['bids']  # List of bids (price, quantity)
    asks = order_book['asks']  # List of asks (price, quantity)
    print("Bids:", bids)
    print("Asks:", asks)