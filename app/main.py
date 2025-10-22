import sys
sys.path.append('../WhisperLive/examples/client')
sys.path.append('../examples/client')
sys.path.append('./app/')
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from launch_client_from_file import client_from_file
import config

from queue import Queue
import threading
import os
from pydantic import BaseModel

# MODEL = "tiny"  # Default model, can be changed as needed
# HOST = "renfe-whisperlive-gpu-asr" # "localhost"
# PORT = "9090"  # Default port, can be changed as needed
MODEL = config.settings.ASR_MODEL
LANGUAGE = config.settings.ASR_LANGUAGE
MUTE_AUDIO_PLAYBACK = config.settings.ASR_MUTE_AUDIO_PLAYBACK
HOST = config.settings.ASR_SERVER
PORT = config.settings.ASR_PORT
KAFKA_BROKERS = [f"{config.settings.KAFKA_SERVER}:{config.settings.KAFKA_PORT}"]
KAFKA_TOPIC = config.settings.KAFKA_TOPIC
DO_PRINT_KAFKA_MESSAGES = config.settings.DO_PRINT_KAFKA_MESSAGES
DO_ALWAYS_SEND_ASR_KAFKA_MESSAGES = config.settings.DO_ALWAYS_SEND_ASR_KAFKA_MESSAGES

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def transcribe_file_endpoint(file_path: str):

    q = Queue()

    def transcription_callback(text):
        print(f"transcription_callback (put): {text}")
        q.put(text)  # Called by TranscriptionClient during processing

    def stream_generator():
        while True:
            chunk = q.get()
            if chunk == "__END__":
                break
            print(f"chunk: {chunk}")
            yield f"{chunk}\n"

    # Run client_from_file in a separate thread so it doesn't block
    def run_client():
        client_from_file(file_path, server_IP = HOST, port = PORT, model = MODEL, language = LANGUAGE, 
                         transcription_callback=transcription_callback, mute_audio_playback=MUTE_AUDIO_PLAYBACK)
        q.put("__END__")

    threading.Thread(target=run_client, daemon=True).start()

    return StreamingResponse(stream_generator(), media_type="text/plain")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "WhisperLive API is running"}

@app.get("/list_files")
async def list_files(folder: str = "/tmp"):
    abs_folder = os.path.abspath(folder)
    if not os.path.isdir(abs_folder):
        return {"error": "Folder does not exist"}
    files = [
        os.path.abspath(os.path.join(abs_folder, f))
        for f in os.listdir(abs_folder)
        if os.path.isfile(os.path.join(abs_folder, f)) and f.lower().endswith('.wav')
    ]
    return {"files": files}

# endpoint to remove a file given its basename
@app.delete("/remove_file")
async def remove_file(file_basename: str = Body(..., embed=True), folder: str = "/tmp"):
    """How to use the endpoint with curl and python requests
    * Example with curl:
    curl -X DELETE "http://localhost:8000/remove_file" -H "Content-Type: application/json" -d '{"file_basename": "your_file.wav", "folder": "/tmp"}'
    * Example with python requests:
    import requests
    response = requests.delete("http://localhost:8000/remove_file", json={"file_basename": "your_file.wav", "folder": "/tmp"})
    print(response.json())
    """

    abs_folder = os.path.abspath(folder)
    file_path = os.path.join(abs_folder, file_basename)
    if not os.path.isfile(file_path):
        return {"error": "File does not exist"}
    if not file_path.lower().endswith('.wav'):
        return {"error": "Only .wav files can be removed"}
    try:
        os.remove(file_path)
        return {"status": "success", "message": f"File {file_basename} removed"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/transcribe_file")
async def transcribe_file(file: UploadFile = File(...)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    return transcribe_file_endpoint(temp_path)

@app.post("/transcribe_local_file")
async def transcribe_local_file(local_file: str = Body(..., embed=True)):

    return transcribe_file_endpoint(local_file)


class FileRequest(BaseModel):
    file_path: str

@app.post("/simulate_trancription")
# async def simulate_trancription(request: FileRequest):
async def simulate_trancription(file: UploadFile = File(...)):
    """Simulate ASR transcription by reading a jsonl file with the following format and appending a delay corresponding to the end-start time difference.
    {"text": "some text", "start": 0.0, "end": 1.23}
    {"text": "some text", "start": 1.23, "end": 2.56}
    """
    import json
    import time

    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # file_path = request.file_path

    def stream_generator():
        try:
            with open(file_path, "r") as f:
                lines = f.read().splitlines()
                current_lines = []
                for line in lines:
                    if not line.strip():
                        continue
                    line_dict = json.loads(line)
                    current_lines.append(line_dict)
                    delay = line_dict.get("end", 0) - line_dict.get("start", 0)
                    print(f"SLEEP {delay} seconds and YIELD: {json.dumps(current_lines)}\n")
                    if delay > 0:
                        time.sleep(delay)
                    yield f"{json.dumps(current_lines)}\n"
                # Force flush at the end
                yield ""
        finally:
            if os.path.exists(file_path):
                print(f"(FastAPI) Removing temporary file: {file_path}")
                os.remove(file_path)

    return StreamingResponse(stream_generator(), media_type="application/json")


#############################
## TO SEND KAFKA MESSAGES  ##

from kafka import KafkaProducer
import json
import uuid

def generate_input_id():
    """Generate a unique input ID."""
    return str(uuid.uuid4())

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

def update_content(line, last_line_dict):
    """Check if the content has changed before printing."""

    print(f"update_content: line len {len(line)} vs last_line_dict len {len(last_line_dict)}")

    if DO_ALWAYS_SEND_ASR_KAFKA_MESSAGES:
        print(f"update_content (always) --> True")
        return True
    elif len(line) > len(last_line_dict) and len(last_line_dict) > 0:
        print(f"update_content (logic) --> True")
        return True
    print(f"update_content (logic) --> False")
    return False

from typing import List

class Segment(BaseModel):
    text: str
    start: float
    end: float

class TranscriptPayload(BaseModel):
    session_id: str
    full_transcript: str
    segments: List[Segment]

session_states = {}

@app.post("/send_kafka_message")
async def send_kafka_message(payload: TranscriptPayload):
    # Send each segment as a separate Kafka message
    
    global session_states

    print("\n=== New /send_kafka_message request ===")
    print(f"(start) Current session_states keys: {list(session_states.keys())}")

    session_id = payload.session_id
    line = [{"text": seg.text, "start": seg.start, "end": seg.end} for seg in payload.segments]
    last_line_dict = session_states.get(session_id, [])
    print(f"(middle) Session {session_id}. Total segments stored: {len(last_line_dict)}")
    do_update = update_content(line, last_line_dict)
    print(f"(middle) do_update: {do_update}")
    if session_id not in session_states:
        session_states[session_id] = []
    session_states[session_id] = line

    print(f"(end) Current session_states keys: {list(session_states.keys())}")
    print(f"Session {session_id} state updated. Total segments stored: {len(session_states[session_id])}")

    if do_update:
        kafka_producer(KAFKA_TOPIC, last_line_dict, session_id=session_id)
        return {
            "status": "ok",
            "session_id": session_id,
            "do_update": True,
            "message": f"Sent {len(payload.segments)} segments to Kafka for session {session_id}"
        }
    else:
        return {
            "status": "ok",
            "session_id": session_id,
            "do_update": False,
            "message": "No update sent to Kafka"
        }

# @app.post("/send_kafka_message")
# def send_kafka_message(line, last_line_dict, session_id="test_renfe"):
#     """Send a message to Kafka if the content has changed."""
#     do_update = update_content(line, last_line_dict)
#     if do_update:
#         kafka_producer(KAFKA_TOPIC, line, session_id=session_id)
#     return {"status": "message processed", "do_update": do_update}

############################

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
import numpy as np
import asyncio
import uuid
# print current directory
from whisper_live.client import TranscriptionClient


sessions = {}  # session_id -> client

SUPPORTED_LANGS = {
    "es": "Spanish",
    "ca": "Catalan",
    "gl": "Galician",
    "eu": "Basque",
    "en": "English",
}
SUPPORTED_MODELS = ["tiny", "small", "large-v2", "large-v3"]

@app.websocket("/stream")
async def stream_audio(
    ws: WebSocket,
    lang: str = Query("es", description="Language code (es, ca, gl, eu, en)"),
    model: str = Query("tiny", description="Model size (tiny, small, large-v2, large-v3)")
):
    await ws.accept()
    session_id = str(uuid.uuid4())

    if lang not in SUPPORTED_LANGS:
        lang = "es"
    if model not in SUPPORTED_MODELS:
        model = "tiny"

    print(f"[+] New session {session_id} | Lang={lang} | Model={model}")

    # Per-user transcription client
    client = TranscriptionClient(
        "localhost", 9090,
        lang=lang,
        model=model,
        use_vad=True,
        transcription_callback=lambda text, *_: (print("[RECOGNIZED]", text), 
                                                 asyncio.create_task(ws.send_text(text)))
    )
    client.external_feed = True
    sessions[session_id] = client

    print("client type:", type(client))
    print("client external_feed:", hasattr(client, "external_feed"))
    print("client feed_audio:", hasattr(client, "feed_audio"))
    print("TranscriptionClient feed_audio:", hasattr(TranscriptionClient, "feed_audio"))

    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.to_thread(client, None))  # background

    try:
        while True:
            msg = await ws.receive_bytes()
            audio = np.frombuffer(msg, dtype=np.int16)
            print(f"[DEBUG] Received {len(audio)} samples from session {session_id}")
            client.feed_audio(audio)
    except WebSocketDisconnect:
        print(f"[-] Session {session_id} disconnected")
        sessions.pop(session_id, None)
        client.close()
        await ws.close()
    except Exception as e:
        print(f"[ERROR] Exception in session {session_id}: {e}")
        sessions.pop(session_id, None)
        await ws.close()

###########################

# from fastapi import FastAPI, Request
# from fastapi.responses import StreamingResponse
# # import asyncio
# import websockets
# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.post("/streaming")
# async def streaming(request: Request):
#     # Connect internally to the ASR WebSocket server
#     uri = "ws://localhost:9090"
#     async with websockets.connect(uri) as ws:
#         async for chunk in request.stream():
#             await ws.send(chunk)

#         await ws.send(b"END")

#         async def text_stream():
#             async for msg in ws:
#                 yield msg + "\n"

#         return StreamingResponse(text_stream(), media_type="text/plain")

# @app.post("/streaming")
# async def streaming(request: Request):
#     data = await request.body()
#     print(f"Received {len(data)} bytes")
#     return {"status": "ok"}

# @app.post("/streaming")
# async def streaming(request: Request):
#     async def generate_transcript():
#         async for chunk in request.stream():
#             # Here, send chunk to your ASR WebSocket
#             # and yield incremental text
#             if isinstance(chunk, str):
#                 chunk = chunk.encode("utf-8")  # only if your input was actually text (rare)
#             yield f"chunk: {len(chunk)} bytes\n"
#         yield "done\n"

#     return StreamingResponse(generate_transcript(), media_type="text/plain")

################################

# import asyncio
# import websockets
# import json
# from fastapi import FastAPI, Request, HTTPException
# from fastapi.responses import StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # app = FastAPI()

# # Configure CORS for local development
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins, adjust for production
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

# # Configuration for the backend ASR WebSocket server
# ASR_SERVER_URI = "ws://localhost:9090"

# async def stream_audio_to_asr(request: Request, asr_ws: websockets.WebSocketClientProtocol):
#     """Reads audio chunks from the incoming HTTP request and forwards them to the ASR WebSocket server."""
#     try:
#         init_message = {
#             "uid": f"http-stream-{id(request)}", "language": None, "task": "transcribe",
#             "model": "small", "use_vad": True,
#         }
#         await asr_ws.send(json.dumps(init_message))
        
#         async for chunk in request.stream():
#             await asr_ws.send(chunk)
        
#         await asr_ws.send("END_OF_AUDIO")
#         logger.info("Finished streaming audio from client to ASR server.")
#     except Exception as e:
#         logger.error(f"Error streaming audio to ASR: {e}")

# async def get_transcript_from_asr(asr_ws: websockets.WebSocketClientProtocol, response_queue: asyncio.Queue):
#     """Receives transcription results from the ASR server and puts them into a queue."""
#     try:
#         while True:
#             transcript_chunk = await asr_ws.recv()
#             await response_queue.put(transcript_chunk)
#     except websockets.exceptions.ConnectionClosed:
#         logger.info("ASR server connection closed.")
#         await response_queue.put(None)
#     except Exception as e:
#         logger.error(f"Error receiving transcript from ASR: {e}")
#         await response_queue.put(None)

# @app.post("/streaming")
# async def streaming_endpoint(request: Request):
#     """
#     Handles a streaming HTTP POST. It proxies audio to a backend ASR WebSocket server
#     and streams the transcription results back to the client.
#     """
    
#     # --- ADDED: Initial check for ASR server connection ---
#     try:
#         # Try to connect before starting the full process
#         connection_test = await websockets.connect(ASR_SERVER_URI)
#         await connection_test.close()
#     except Exception as e:
#         logger.error(f"Could not connect to ASR server at {ASR_SERVER_URI}. Please ensure it is running. Error: {e}")
#         raise HTTPException(
#             status_code=502,
#             detail=f"Bad Gateway: Could not connect to the backend ASR server at {ASR_SERVER_URI}."
#         )

#     async def response_generator():
#         response_queue = asyncio.Queue()
#         try:
#             async with websockets.connect(ASR_SERVER_URI) as asr_websocket:
#                 logger.info("Successfully connected to ASR server.")
                
#                 audio_stream_task = asyncio.create_task(stream_audio_to_asr(request, asr_websocket))
#                 transcript_receive_task = asyncio.create_task(get_transcript_from_asr(asr_websocket, response_queue))

#                 while True:
#                     result = await response_queue.get()
#                     if result is None: break
#                     yield result + "\n"
                
#                 await audio_stream_task
#         except Exception as e:
#             error_message = f"An unexpected error occurred: {e}"
#             logger.error(error_message)
#             yield f'{{"error": "{error_message}"}}\n'

#     return StreamingResponse(response_generator(), media_type="application/x-ndjson")

