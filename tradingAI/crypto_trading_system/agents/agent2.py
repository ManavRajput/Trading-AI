from crypto_trading_system.agents.agent import Agent
from crypto_trading_system.communication.message_queue import MessageQueue
from crypto_trading_system.analysis.psychology_analysis import identify_human_psychology
from crypto_trading_system.analysis.sentiment_analysis import analyze_sentiment
from crypto_trading_system.config import COINMARKETCAP_API_KEY
import requests
import datetime
import json
import numpy as np

class Agent2(Agent):
    def __init__(self, agent_id):
        super().__init__(agent_id)
        self.message_queue = MessageQueue("trading_queue")
        self.coinmarketcap_api_key = COINMARKETCAP_API_KEY
        self.previous_price = {}
        self.historical_market_data = []
        self.log("Agent2 specific initialization complete.")

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

    def assess_psychology(self, sentiment_scores):
        compound_score = sentiment_scores.get('compound', 0)  # Handle missing 'compound'
        psychological_assessment = ""

        if compound_score > 0.5:
            psychological_assessment = "High Optimism: Potential overbought condition."
        elif compound_score < -0.5:
            psychological_assessment = "High Pessimism: Potential oversold condition."
        else:
            psychological_assessment = "Neutral Sentiment."

        return psychological_assessment

    def get_market_data(self, coin):
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        parameters = {'symbol': coin}
        headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': self.coinmarketcap_api_key}

        try:
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, params=parameters)
            data = response.json()

            if data.get('status', {}).get('error_code') == 0:  # Safer data access
                quote = data['data'].get(coin, {}).get('quote', {}).get('USD', {})
                price = quote.get('price')
                volume_24h = quote.get('volume_24h')
                if price is not None and volume_24h is not None:
                    market_data = {"coin": coin, "price": price, "volume_24h": volume_24h, "timestamp": datetime.datetime.now().isoformat()}
                    self.historical_market_data.append(market_data)
                    return float(price), float(volume_24h)
                else:
                    self.log(f"Price or volume data missing for {coin}")
                    return None, None
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

    def calculate_volatility(self, coin, period=14):
        prices = [data["price"] for data in self.historical_market_data[-period:] if data["coin"] == coin]
        if len(prices) < 2:  # Volatility needs at least 2 data points
            return 0

        price_changes = np.diff(prices) / prices[:-1]
        volatility = np.std(price_changes)
        return volatility

    def run(self):
        self.log("Agent2 is running.")

        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                self.log(f"Received proposal: {message}")

                market_data_for_psychology = {}

                if 'rationale' in message and message['rationale']:
                    news_section = message['rationale'].split("Recent News:\n")
                    if len(news_section) > 1:
                        news_text = news_section[1]
                        sentiment_scores = analyze_sentiment(news_text)
                        message['sentiment'] = sentiment_scores

                        market_data_for_psychology["negative_news"] = sentiment_scores.get('compound', 0) < -0.2
                        market_data_for_psychology["positive_news"] = sentiment_scores.get('compound', 0) > 0.2

                        assessment = self.assess_psychology(sentiment_scores)
                        message['psychological_assessment'] = assessment
                        self.log(f"Psychological Assessment: {assessment}")
                    else:
                        self.log("No news found in rationale.")

                if 'coin' in message:
                    coin = message['coin']
                    price, volume = self.get_market_data(coin)
                    if price is not None and volume is not None:
                        market_data_for_psychology["price_falling_rapidly"] = price < self.previous_price.get(coin, float('inf')) if coin in self.previous_price else False
                        market_data_for_psychology["price_rising_rapidly"] = price > self.previous_price.get(coin, float('-inf')) if coin in self.previous_price else False
                        market_data_for_psychology["volume_low"] = volume < 1000000
                        market_data_for_psychology["volume_high"] = volume > 10000000

                        volatility = self.calculate_volatility(coin)
                        market_data_for_psychology["high_risk_tolerance"] = volatility > 0.01

                        self.previous_price[coin] = price  # Update previous price
                    else:
                        self.log(f"Could not fetch price/volume for {coin}")


                # Placeholder for other psychological factors
                market_data_for_psychology["frequent_trading"] = False
                market_data_for_psychology["quick_to_sell"] = False
                market_data_for_psychology["reluctant_to_buy"] = False
                market_data_for_psychology["following_trends"] = False
                market_data_for_psychology["copying_others"] = False

                human_psychology = identify_human_psychology(market_data_for_psychology)
                message['human_psychology'] = human_psychology
                self.log(f"Human Psychology: {human_psychology}")

                self.send_message(message, "Other Agents")

            except json.JSONDecodeError as e:
                self.log(f"Error decoding JSON: {e}. Body: {body}")
            except Exception as e:
                self.log(f"Error in callback: {e}")

        self.message_queue.start_consuming(callback)