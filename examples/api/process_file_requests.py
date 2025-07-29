import requests
import os
import json 
import datetime
from kafka import KafkaProducer

url = "http://localhost:8000/transcribe"
file_path = "/home/mumbert/Descargas/RENFE_logs/audios/1cd8983e-f38b-4df6-9510-7b973e006a17_only_conversation.wav"

def clear_screen():
    """Clears the console screen."""
    os.system("cls" if os.name == "nt" else "clear")

def get_current_time():
    """Get the current time formatted as yy-mm-dd HH:MM:SS.sss."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

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

def update_content(line, last_line_dict):
    """Check if the content has changed before printing."""
    if len(line) > len(last_line_dict) and len(last_line_dict) > 0:
        return True
    return False

last_line_dict = []
do_update = False
do_print_screen = True
do_send_kafka = True
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
                        print(json.dumps(last_line_dict, indent=4))
                        print(f"Update time (loop, {do_update}): {get_current_time()}")
                    if do_send_kafka:
                        kafka_producer("asr", message = last_line_dict)
                last_line_dict = line_dict

if not do_update:
    if do_print_screen:
        clear_screen()
        print(json.dumps(last_line_dict, indent=4))
        print(f"Update time (last, {do_update}): {get_current_time()}")
    if do_send_kafka:
        kafka_producer("asr", message = last_line_dict)

msg = [{"END": "End of transcription stream."}]
if do_print_screen:
    print(msg)
if do_send_kafka:
    kafka_producer("asr", message = msg)
