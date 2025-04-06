from crypto_trading_system.agents.agent import Agent
from crypto_trading_system.communication.message_queue import MessageQueue
import json
from crypto_trading_system.strategies.trading_strategy import make_trading_decision

class Agent4(Agent):
    def __init__(self, agent_id):
        super().__init__(agent_id)
        self.message_queue = MessageQueue("trading_queue")
        self.log("Agent4 specific initialization complete.")

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

    def run(self):
        self.log("Agent4 is running.")

        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                self.log(f"Received proposal: {message}")

                trading_decision = make_trading_decision(message)
                message['trading_signal'] = trading_decision
                self.log(f"Trading Decision: {trading_decision}")

                self.send_message(message, "Execution System") # Send to execution system

            except json.JSONDecodeError as e:
                self.log(f"Error decoding JSON: {e}. Body: {body}")
            except Exception as e:
                self.log(f"Error in callback: {e}")

        self.message_queue.start_consuming(callback)