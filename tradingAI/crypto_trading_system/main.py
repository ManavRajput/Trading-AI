import threading
from communication.message_queue import MessageQueue
from agents.agent1 import Agent1
from agents.agent2 import Agent2
from agents.agent3 import Agent3
from agents.agent4 import Agent4
from execution_system import ExecutionSystem # Import ExecutionSystem

def main():
    # Create message queue
    message_queue = MessageQueue("trading_queue")

    # Start agents and execution system in separate threads
    agents = [
        Agent1(message_queue, coin_list=["BTC", "ETH", "BNB", "XRP"]),
        Agent2(message_queue),
        Agent3(message_queue),
        Agent4(message_queue),
        ExecutionSystem() # Add ExecutionSystem
    ]

    threads = [threading.Thread(target=agent.run) for agent in agents]

    # Start all threads
    for thread in threads:
        thread.start()

    # Optional: Keep the main thread alive (for continuous operation)
    # import time
    # while True:
    #     time.sleep(1)

if __name__ == "__main__":
    main()