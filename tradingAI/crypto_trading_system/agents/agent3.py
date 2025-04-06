from crypto_trading_system.agents.agent import Agent
from crypto_trading_system.communication.message_queue import MessageQueue
import json
import requests
import datetime
from crypto_trading_system.config import COINMARKETCAP_API_KEY
from crypto_trading_system.strategies.technical_indicators import calculate_sma, calculate_ema, calculate_rsi
from crypto_trading_system.strategies.fundamental_analysis import get_market_cap, get_volume_24h

class Agent3(Agent):
    def __init__(self, agent_id):
        super().__init__(agent_id)
        self.message_queue = MessageQueue("trading_queue")
        self.coinmarketcap_api_key = COINMARKETCAP_API_KEY
        self.historical_market_data = []
        self.log("Agent3 specific initialization complete.")

    def send_message(self, message, recipient):
        self.message_queue.send_message(message)
        self.log(f"Sent message to {recipient}: {message}")
        return f"Message sent by {self.agent_id}"

    def receive_message(self):
        message = self.message_queue.receive_message()
        if message:
            self.log(f"Received message: {message}")
            return message
        else:
            self.log("No message received.")
            return None

    def get_market_data(self, coin):
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        parameters = {'symbol': coin}
        headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': self.coinmarketcap_api_key}

        try:
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, params=parameters)
            data = response.json()

            if data.get('status', {}).get('error_code') == 0:
                quote = data['data'].get(coin, {}).get('quote', {}).get('USD', {})
                price = quote.get('price')
                volume_24h = quote.get('volume_24h')
                market_data = {"coin": coin, "price": price, "volume_24h": volume_24h, "timestamp": datetime.datetime.now().isoformat()}
                self.historical_market_data.append(market_data)
                return float(price), float(volume_24h)
            else:
                error_message = data.get('status', {}).get('error_message', "Unknown error")
                self.log(f"Error getting market data for {coin}: {error_message}")
                return None, None
        except requests.exceptions.RequestException as e:
            self.log(f"Request Error getting market data for {coin}: {e}")
            return None, None
        except Exception as e:
            self.log(f"General Error getting market data for {coin}: {e}")
            return None, None

    def run(self):
        self.log("Agent3 is running.")

        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                self.log(f"Received proposal: {message}")

                if 'coin' in message:
                    coin = message['coin']
                    price, volume = self.get_market_data(coin)

                    if price and volume:
                        prices = [data["price"] for data in self.historical_market_data if data["coin"] == coin]
                        sma_20 = calculate_sma(prices, 20)
                        ema_12 = calculate_ema(prices, 12)
                        rsi_14 = calculate_rsi(prices, 14)
                        market_cap = get_market_cap(coin, self.coinmarketcap_api_key)

                        message['technical_indicators'] = {
                            'sma_20': sma_20,
                            'ema_12': ema_12,
                            'rsi_14': rsi_14
                        }
                        message['fundamental_data'] = {
                            'market_cap': market_cap,
                            'volume_24h': volume,
                            'price': price
                        }
                        self.log(f"Technical Indicators: {message['technical_indicators']}")
                        self.log(f"Fundamental Data: {message['fundamental_data']}")
                    else:
                        self.log(f"Could not fetch price/volume for {coin}")
                else:
                    self.log("No coin found in message.")

                self.send_message(message, "Other Agents")

            except json.JSONDecodeError as e:
                self.log(f"Error decoding JSON: {e}. Body: {body}")
            except Exception as e:
                self.log(f"Error in callback: {e}")

        self.message_queue.start_consuming(callback)