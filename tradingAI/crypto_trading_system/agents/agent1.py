import random
import datetime
import time
import requests
import numpy as np
from .agent import Agent
from crypto_trading_system.config import COINMARKETCAP_API_KEY
from crypto_trading_system.communication.message_queue import MessageQueue
import json
from crypto_trading_system.data.data_handler import save_market_data_csv, load_market_data_csv


class Agent1(Agent):
    def __init__(self, agent_id, coin_list):
        super().__init__(agent_id)
        self.coin_list = coin_list
        self.coinmarketcap_api_key = COINMARKETCAP_API_KEY
        self.message_queue = MessageQueue("trading_queue")
        self.log("Agent1 specific initialization complete.")

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

    def get_top_coins(self, limit=10):
        """Fetch top coins by market cap from CoinMarketCap."""
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        parameters = {
            'limit': limit,
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.coinmarketcap_api_key
        }

        try:
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, params=parameters)
            data = response.json()

            if data['status']['error_code'] == 0:
                return data['data']
            else:
                self.log(f"Error getting top coins: {data['status']['error_message']}")
                return []
        except Exception as e:
            self.log(f"Error fetching top coins: {e}")
            return []

    def analyze_coin(self, coin_symbol):
        """Analyze a specific coin using CoinMarketCap data."""
        url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
        parameters = {'symbol': coin_symbol}
        headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': self.coinmarketcap_api_key}

        try:
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, params=parameters)
            data = response.json()

            if data['status']['error_code'] == 0:
                coin_data = data['data'][coin_symbol][0]
                return {
                    'id': coin_data['id'],
                    'name': coin_data['name'],
                    'symbol': coin_data['symbol'],
                    'price': coin_data['quote']['USD']['price'],
                    'market_cap': coin_data['quote']['USD']['market_cap'],
                    'volume_24h': coin_data['quote']['USD']['volume_24h'],
                    'percent_change_24h': coin_data['quote']['USD']['percent_change_24h'],
                    'timestamp': datetime.datetime.now().isoformat()
                }
            else:
                self.log(f"Error analyzing coin {coin_symbol}: {data['status']['error_message']}")
                return None
        except Exception as e:
            self.log(f"Error analyzing coin {coin_symbol}: {e}")
            return None

    def calculate_volatility(self, prices):
        """Calculate historical volatility."""
        try:
            if len(prices) < 2:
                return 0
            returns = np.diff(prices) / prices[:-1]
            return np.std(returns)
        except Exception as e:
            self.log(f"Error calculating volatility: {e}")
            return 0

    def fetch_on_chain_metrics(self, coin_symbol):
        """Fetch on-chain metrics (mock function)."""
        # Mock data since CoinMarketCap doesn't provide on-chain metrics
        return {
            "active_addresses": np.random.randint(1000, 10000),
            "transaction_volume": np.random.randint(100000, 1000000),
            "network_growth": np.random.uniform(0.1, 1.0)
        }

    def get_market_data(self, coin):
        """Get comprehensive market data for a coin."""
        coin_data = self.analyze_coin(coin)
        if coin_data:
            # Add on-chain metrics
            on_chain_data = self.fetch_on_chain_metrics(coin)
            coin_data.update(on_chain_data)

            # Save to CSV
            save_market_data_csv([coin_data])
            return coin_data
        return None

    def calculate_score(self, market_data):
        try:
            # Normalize values
            normalized_market_cap = market_data['market_cap'] / 1e12  # Normalize to trillions
            normalized_volume = market_data['volume_24h'] / 1e9  # Normalize to billions
            price_change = market_data['percent_change_24h']

            # Include on-chain metrics in scoring
            normalized_tx_volume = market_data['transaction_volume'] / 1e6  # Normalize to millions
            network_growth = market_data['network_growth']

            score = (normalized_market_cap * 0.3) + \
                    (normalized_volume * 0.2) + \
                    (price_change * 0.2) + \
                    (normalized_tx_volume * 0.15) + \
                    (network_growth * 0.15)

            return score
        except Exception as e:
            self.log(f"Error calculating score: {e}")
            return -1

    def generate_rationale(self, coin, market_data):
        rationale = f"Analysis for {coin}:\n"

        if market_data:
            rationale += f"Current Price: ${market_data['price']:,.2f}\n"
            rationale += f"Market Cap: ${market_data['market_cap']:,.2f}\n"
            rationale += f"24h Volume: ${market_data['volume_24h']:,.2f}\n"
            rationale += f"24h Price Change: {market_data['percent_change_24h']:.2f}%\n"

            # Add on-chain metrics to rationale
            rationale += f"Active Addresses: {market_data['active_addresses']:,}\n"
            rationale += f"Transaction Volume: ${market_data['transaction_volume']:,.2f}\n"
            rationale += f"Network Growth: {market_data['network_growth']:.2f}\n"

            score = self.calculate_score(market_data)
            rationale += f"Overall Score: {score:.2f}\n"
        else:
            rationale += "No market data available for analysis.\n"

        return rationale

    def run(self):
        self.log("Agent1 is running.")
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.log(f"Current Time = {current_time}")

        # Get top coins and select one for analysis
        top_coins = self.get_top_coins(limit=5)
        if top_coins:
            chosen_coin = random.choice(top_coins)['symbol']
            market_data = self.get_market_data(chosen_coin)
            rationale = self.generate_rationale(chosen_coin, market_data)

            proposal = {
                "coin": chosen_coin,
                "market_data": market_data,
                "rationale": rationale,
                "timestamp": current_time
            }

            message_sent = self.send_message(proposal, "Other Agents")
            self.log(message_sent)
        else:
            self.log("No coins available for analysis")

        def handle_message(ch, method, properties, body):
            try:
                message = json.loads(body)
                self.log(f"Received message: {message}")
            except json.JSONDecodeError:
                self.log("Failed to decode message body.")
            except Exception as e:
                self.log(f"Unexpected error in handling message: {str(e)}")

        self.message_queue.start_consuming(handle_message)