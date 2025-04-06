import pika
import json

class MessageQueue:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost')) # Connect to local rabbitmq server
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name) # Ensure queue exists

    def send_message(self, message):
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(message))
        print(f" [x] Sent {message}")

    def receive_message(self):
        method_frame, properties, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True) # auto_ack = acknowledge automatically after reading the message.
        if body:
            message = json.loads(body)
            print(f" [x] Received {message}")
            return message
        else:
            return None # return None if there is no message in the queue.

    def close(self):
        self.connection.close()

    def start_consuming(self, callback):  # added callback function
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()