import requests

def get_market_cap(coin, api_key):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parameters = {'symbol': coin}
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': api_key}
    try:
        session = requests.Session()
        session.headers.update(headers)
        response = session.get(url, params=parameters)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data.get('status', {}).get('error_code') == 0:
            quote = data['data'].get(coin, {}).get('quote', {}).get('USD', {})
            market_cap = quote.get('market_cap')
            return float(market_cap) if market_cap is not None else None
        else:
            error_message = data.get('status', {}).get('error_message', "Unknown error")
            print(f"Error getting market cap for {coin}: {error_message}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request Error getting market cap for {coin}: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Error parsing market cap JSON for {coin}: {e}. Response: {response.text if 'response' in locals() else 'No Response'}")
        return None
    except Exception as e:
        print(f"General Error getting market cap for {coin}: {e}")
        return None

def get_volume_24h(coin, api_key):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parameters = {'symbol': coin}
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': api_key}
    try:
        session = requests.Session()
        session.headers.update(headers)
        response = session.get(url, params=parameters)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()

        if data.get('status', {}).get('error_code') == 0:
            quote = data['data'].get(coin, {}).get('quote', {}).get('USD', {})
            volume_24h = quote.get('volume_24h')
            return float(volume_24h) if volume_24h is not None else None
        else:
            error_message = data.get('status', {}).get('error_message', "Unknown error")
            print(f"Error getting 24h volume for {coin}: {error_message}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request Error getting 24h volume for {coin}: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Error parsing 24h volume JSON for {coin}: {e}. Response: {response.text if 'response' in locals() else 'No Response'}")
        return None
    except Exception as e:
        print(f"General Error getting 24h volume for {coin}: {e}")
        return None