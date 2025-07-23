from kafka import KafkaProducer
import json

def kafka_producer(topic_name, message):
    producer = KafkaProducer(
        bootstrap_servers=['rebel.grivolla.net:9092'],  # Replace with your Kafka broker(s)
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
    topic = 'asr'
    message = {'key1': 'value1', 'key2': 'value2'}
    kafka_producer(topic, message)