from kafka import KafkaConsumer
import json
import os

def clear_screen():
    """Clears the console screen."""
    os.system("cls" if os.name == "nt" else "clear")

def kafka_consumer(topic_name, group_id):
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=['rebel.grivolla.net:9092'],  # Replace with your Kafka broker(s)
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
        # for message in consumer:
            #print(f"Received message from topic '{topic_name}': {message.value[-3:]}")
            # for id, msg in enumerate(message.value[-1*n_last_messages:]):
            #     same = "same" if last_messages[id] == msg else "different"
            #     print(f"{id+1}\t{same}\t{msg}")
            #     last_messages.append(msg)
            # last_messages = last_messages[-1*n_last_messages:]
    except Exception as e:
        print(f"Error consuming message: {e}")
    finally:
        consumer.close()

if __name__ == '__main__':
    topic = 'asr'
    group_id = 'session-00001'
    kafka_consumer(topic, group_id)