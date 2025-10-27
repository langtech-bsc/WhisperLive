import requests
import os
import json 
import datetime
from kafka import KafkaProducer
from app import config
import argparse
import uuid
import time

def generate_input_id():
    """Generate a unique input ID."""
    return str(uuid.uuid4())

# IP = "localhost" # "84.88.51.151" # "localhost"
# PORT = "8050" # 8000
FASTAPI_SERVER = config.settings.FASTAPI_SERVER
FASTAPI_PORT = config.settings.FASTAPI_PORT
KAFKA_BROKERS = [f"{config.settings.KAFKA_SERVER}:{config.settings.KAFKA_PORT}"]
KAFKA_TOPIC = config.settings.KAFKA_TOPIC
DO_PRINT_KAFKA_MESSAGES = config.settings.DO_PRINT_KAFKA_MESSAGES
DO_SEND_KAFKA_MESSAGES = config.settings.DO_SEND_KAFKA_MESSAGES
DO_ALWAYS_SEND_ASR_KAFKA_MESSAGES = config.settings.DO_ALWAYS_SEND_ASR_KAFKA_MESSAGES
DO_SEND_ASR_KAFKA_MESSAGES_BY_TIME_DIFFERENCE = float(config.settings.DO_SEND_ASR_KAFKA_MESSAGES_BY_TIME_DIFFERENCE)
SESSION_ID = generate_input_id()
DATA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))

if "http" not in FASTAPI_SERVER:
    FASTAPI_SERVER = f"http://{FASTAPI_SERVER}:{FASTAPI_PORT}"

url_transcribe_file = f"{FASTAPI_SERVER}/transcribe_file"
url_simulate_trancription = f"{FASTAPI_SERVER}/simulate_trancription"
example_file_path = os.path.join(DATA_FOLDER, "1cd8983e-f38b-4df6-9510-7b973e006a17_only_conversation.wav")
example_jsonl = os.path.join(DATA_FOLDER, "conversation_example.jsonl")
example_jsonl2 = os.path.join(DATA_FOLDER, "conversation_example2.jsonl")
example_jsonl3 = os.path.join(DATA_FOLDER, "conversation_example3.jsonl")

def clear_screen():
    """Clears the console screen."""
    # print("#" * 25)
    os.system("cls" if os.name == "nt" else "clear")

def get_current_time():
    """Get the current time formatted as yy-mm-dd HH:MM:SS.sss."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def kafka_producer(topic_name, message, session_id="test_marti"):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKERS, # ['rebel.grivolla.net:9092'],  # Replace with your Kafka broker(s)
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    try:
        kafka_message = {"content": message, 
                         "session_id": session_id,
                         "input_id": generate_input_id()}
        producer.send(topic_name, kafka_message)
        producer.flush()  # Ensure all messages are sent
        if DO_PRINT_KAFKA_MESSAGES:
            print(f"Message sent to topic '{topic_name}': {kafka_message}")
    except Exception as e:
        print(f"Error producing kafka_message: {e}")
    finally:
        producer.close()

def update_content(line, last_line_dict, last_timestamp):
    """Check if the content has changed before printing."""

    print(f"update_content: len line = {len(line)} vs len last_line_dict {len(last_line_dict)}")

    time_difference = get_current_timestamp() - last_timestamp

    if DO_ALWAYS_SEND_ASR_KAFKA_MESSAGES:
        print(f"update_content (always) --> True")
        return True
    elif len(line) > len(last_line_dict) and len(last_line_dict) > 0:
        print(f"update_content (logic) --> True")
        return True
    elif DO_SEND_ASR_KAFKA_MESSAGES_BY_TIME_DIFFERENCE and time_difference and time_difference > DO_SEND_ASR_KAFKA_MESSAGES_BY_TIME_DIFFERENCE:
        if line != last_line_dict:
            print(f"update_content (time) --> True (time_difference: {time_difference})")
            if line: print(f"line[-1]: {line[-1]}")
            if last_line_dict: print(f"last_line_dict[-1]: {last_line_dict[-1]}")
            return True
        else:
            print(f"update_content (time) --> False (time_difference: {time_difference}) but same content as last message")
            if line: print(f"line[-1]: {line[-1]}")
            if last_line_dict: print(f"last_line_dict[-1]: {last_line_dict[-1]}")
            return False
    print(f"update_content (logic) --> False")
    return False

def health_check():
    """Check the health of the API."""
    response = requests.get(f"{FASTAPI_SERVER}/health")
    if response.status_code == 200:
        msg = "API is healthy:", response.json()
    else:
        msg = "API health check failed:", response.status_code
    return msg

def get_current_timestamp():

    return time.time()

def process_file(file_path: str = ""):

    # Determine endpoint and request parameters
    if file_path.lower().endswith('.wav'):
        url = url_transcribe_file
    elif file_path.lower().endswith('.jsonl'):
        url = url_simulate_trancription
    else:
        print("Unsupported file type.")
        return

    health_msg = health_check()
    print(health_msg)
    last_line_dict = []
    last_timestamp = get_current_timestamp()
    do_update = False
    do_print_screen = DO_PRINT_KAFKA_MESSAGES
    do_send_kafka = DO_SEND_KAFKA_MESSAGES
    
    request_args = {"files": {"file": open(file_path, "rb")}}
    request_kwargs = {"stream": True}

    print(f"URL: {url}")

    # Unified streaming processing
    with requests.post(url, **request_args, **request_kwargs) as response:
        for line in response.iter_lines():
            if line:
                line_dict = json.loads(line.decode("utf-8"))
                do_update = update_content(line_dict, last_line_dict, last_timestamp)
                if do_update:
                    last_timestamp = get_current_timestamp()
                    if do_print_screen:
                        clear_screen()
                        print(health_msg)
                        print(json.dumps(last_line_dict, indent=4))
                        print(f"Update time (loop, {do_update}): {get_current_time()}")
                    if do_send_kafka:
                        kafka_producer(KAFKA_TOPIC, message=last_line_dict, session_id=SESSION_ID)
                last_line_dict = line_dict
            else:
                print("\n***Received empty line (flush)***\n")

    if last_line_dict:
        print(f"Final update after processing all lines.")
        if do_print_screen:
            clear_screen()
            print(health_msg)
            print(json.dumps(last_line_dict, indent=4))
            print(f"Update time (last, {do_update}): {get_current_time()}")
        if do_send_kafka:
            kafka_producer(KAFKA_TOPIC, message=last_line_dict, session_id=SESSION_ID)
    else:
        print("No new content to update.")

    msg = [{"END": "End of transcription stream."}]
    if do_print_screen:
        print(health_msg)
        print(msg)
    if do_send_kafka:
        kafka_producer(KAFKA_TOPIC, message=msg, session_id=SESSION_ID)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process a file (wav or jsonl) via the API.")
    parser.add_argument('--file', choices=['wav', 'jsonl'], required=True, help="Select which file type to process: wav or jsonl")
    args = parser.parse_args()

    if args.file == "wav":
        process_file(file_path=example_file_path)
    elif args.file == "jsonl":
        process_file(file_path=example_jsonl3)
