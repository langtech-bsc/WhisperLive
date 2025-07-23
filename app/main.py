import sys
sys.path.append('../WhisperLive/examples/client')
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from launch_client_from_file import client_from_file

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

router = FastAPI()

def return_transcription(current_transcription):
    """Callback function to handle transcription updates."""
    kafka_producer("asr", message = json.loads(current_transcription))

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    return StreamingResponse(client_from_file(temp_path, 
                                              transcription_callback = return_transcription), 
                                              media_type="text/plain")

