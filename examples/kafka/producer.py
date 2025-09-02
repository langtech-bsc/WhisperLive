from kafka import KafkaProducer
import json
from app import config

KAFKA_BROKERS = [f"{config.settings.KAFKA_SERVER}:{config.settings.KAFKA_PORT}"]
KAFKA_TOPIC = config.settings.KAFKA_TOPIC

def kafka_producer(topic_name, message):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKERS, # ['rebel.grivolla.net:9092'],  # Replace with your Kafka broker(s)
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    try:
        producer.send(topic_name, message)
        producer.flush()  # Ensure all messages are sent
        print(f"Message sent to topic '{topic_name}': {message}")
    except Exception as e:
        print(f"Error producing message: {e}")
    finally:
        producer.close()

if __name__ == '__main__':
    topic = KAFKA_TOPIC
    message = {'key1': 'value1', 'key2': 'value2'}
    kafka_producer(topic, message)