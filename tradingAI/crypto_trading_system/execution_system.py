import json

class ExecutionSystem:
    def __init__(self):
        self.balance = 10000  # Initial balance (example)
        self.holdings = {}    # Dictionary to store holdings (coin: quantity)

    def execute_trade(self, message):
        trading_signal = message.get('trading_signal')
        coin = message.get('coin')
        price = message.get('fundamental_data', {}).get('price_24h') # Get price for trade execution

        if not price:
            print("Price data not available. Cannot execute trade.")
            return

        if trading_signal == "BUY":
            if self.balance > 0:
                quantity = self.balance / price  # Buy as much as possible with current balance
                self.holdings[coin] = self.holdings.get(coin, 0) + quantity
                self.balance = 0  # Spend all available balance for now
                print(f"BUY {quantity:.8f} {coin} at ${price:.2f}")
                print(f"New Holdings: {self.holdings}")
                print(f"Remaining Balance: ${self.balance:.2f}")
            else:
                print("Insufficient balance to buy.")

        elif trading_signal == "SELL":
            if coin in self.holdings and self.holdings[coin] > 0:
                quantity = self.holdings[coin]
                self.balance += quantity * price
                del self.holdings[coin]
                print(f"SELL {quantity:.8f} {coin} at ${price:.2f}")
                print(f"New Holdings: {self.holdings}")
                print(f"Remaining Balance: ${self.balance:.2f}")
            else:
                print(f"No {coin} to sell.")
        elif trading_signal == "HOLD":
            print(f"HOLD {coin}")
        else:
            print(f"Unknown trading signal: {trading_signal}")

    def run(self):
        message_queue = MessageQueue("trading_queue")
        def callback(ch, method, properties, body):
            try:
                print(f"ExecutionSystem: Raw message received: {body}")  # Print the raw message
                message = json.loads(body)
                print(f"ExecutionSystem: Parsed message: {message}")  # Print the parsed message
                self.execute_trade(message)
                print("ExecutionSystem: Trade executed (or attempted).")
            except json.JSONDecodeError as e:
                print(f"ExecutionSystem: JSONDecodeError: {e}. Body: {body}")
            except Exception as e:
                print(f"ExecutionSystem: Exception in callback: {e}")

        print("ExecutionSystem: Starting to consume messages...")  # Check if start_consuming is called
        message_queue.start_consuming(callback)
        print("ExecutionSystem: Consuming messages finished...")
from crypto_trading_system.communication.message_queue import MessageQueue