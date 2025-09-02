from kafka import KafkaConsumer
import json
import os
from app import config

KAFKA_BROKERS = [f"{config.settings.KAFKA_SERVER}:{config.settings.KAFKA_PORT}"]
KAFKA_TOPIC = config.settings.KAFKA_TOPIC

def clear_screen():
    """Clears the console screen."""
    os.system("cls" if os.name == "nt" else "clear")

def kafka_consumer(topic_name, group_id):
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=KAFKA_BROKERS, 
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    try:
        for message in consumer:
            clear_screen()
            for msg in message.value:
                print(json.dumps(msg, indent=2, default=str))
        n_last_messages = 3 
        last_messages = [None]*n_last_messages
    except Exception as e:
        print(f"Error consuming message: {e}")
    finally:
        consumer.close()

if __name__ == '__main__':
    topic = KAFKA_TOPIC
    group_id = 'session-00001'
    kafka_consumer(topic, group_id)