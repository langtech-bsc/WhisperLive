import requests
import os
import json 
import datetime
from kafka import KafkaProducer
from app import config

# IP = "localhost" # "84.88.51.151" # "localhost"
# PORT = "8050" # 8000
FASTAPI_SERVER = config.settings.FASTAPI_SERVER
FASTAPI_PORT = config.settings.FASTAPI_PORT
KAFKA_BROKERS = [f"{config.settings.KAFKA_SERVER}:{config.settings.KAFKA_PORT}"]
KAFKA_TOPIC = config.settings.KAFKA_TOPIC
DO_PRINT_KAFKA_MESSAGES = config.settings.DO_PRINT_KAFKA_MESSAGES
DO_SEND_KAFKA_MESSAGES = config.settings.DO_SEND_KAFKA_MESSAGES

url = f"http://{FASTAPI_SERVER}:{FASTAPI_PORT}/transcribe"
example_file_path = "/home/marti/projects/langtech-bsc/WhisperLive/data/1cd8983e-f38b-4df6-9510-7b973e006a17_only_conversation.wav"

def clear_screen():
    """Clears the console screen."""
    os.system("cls" if os.name == "nt" else "clear")

def get_current_time():
    """Get the current time formatted as yy-mm-dd HH:MM:SS.sss."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def kafka_producer(topic_name, message):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKERS, # ['rebel.grivolla.net:9092'],  # Replace with your Kafka broker(s)
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    try:
        producer.send(topic_name, message)
        producer.flush()  # Ensure all messages are sent
        if DO_PRINT_KAFKA_MESSAGES:
            print(f"Message sent to topic '{topic_name}': {message}")
    except Exception as e:
        print(f"Error producing message: {e}")
    finally:
        producer.close()

def update_content(line, last_line_dict):
    """Check if the content has changed before printing."""
    if len(line) > len(last_line_dict) and len(last_line_dict) > 0:
        return True
    return False

def health_check():
    """Check the health of the API."""
    response = requests.get(f"http://{FASTAPI_SERVER}:{FASTAPI_PORT}/health")
    if response.status_code == 200:
        msg = "API is healthy:", response.json()
    else:
        msg = "API health check failed:", response.status_code
    return msg

def process_file(file_path: str = ""):

    health_msg = health_check()
    last_line_dict = []
    do_update = False
    do_print_screen = DO_PRINT_KAFKA_MESSAGES
    do_send_kafka = DO_SEND_KAFKA_MESSAGES
    with open(file_path, "rb") as audio_file:
        files = {"file": audio_file}
        with requests.post(url, stream=True, files=files) as response:
            for line in response.iter_lines():
                if line: 
                    line_dict = json.loads(line.decode("utf-8"))
                    do_update = update_content(line_dict, last_line_dict)
                    if do_update:
                        if do_print_screen:
                            clear_screen()
                            print(health_msg)
                            print(json.dumps(last_line_dict, indent=4))
                            print(f"Update time (loop, {do_update}): {get_current_time()}")
                        if do_send_kafka:
                            kafka_producer(KAFKA_TOPIC, message = last_line_dict)
                    last_line_dict = line_dict

    if not do_update:
        if do_print_screen:
            clear_screen()
            print(health_msg)
            print(json.dumps(last_line_dict, indent=4))
            print(f"Update time (last, {do_update}): {get_current_time()}")
        if do_send_kafka:
            kafka_producer(KAFKA_TOPIC, message = last_line_dict)

    msg = [{"END": "End of transcription stream."}]
    if do_print_screen:
        clear_screen()
        print(health_msg)
        print(msg)
    if do_send_kafka:
        kafka_producer(KAFKA_TOPIC, message = msg)

if __name__ == "__main__":
    process_file(file_path = example_file_path)
