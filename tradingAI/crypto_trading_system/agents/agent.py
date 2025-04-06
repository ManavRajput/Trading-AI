from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.log(f"Agent {self.agent_id} initialized.")

    @abstractmethod
    def send_message(self, message, recipient):
        pass

    @abstractmethod
    def receive_message(self):
        pass

    def log(self, message):
        print(f"Agent {self.agent_id}: {message}")

    @abstractmethod
    def run(self):
        pass