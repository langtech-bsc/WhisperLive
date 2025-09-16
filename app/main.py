import sys
sys.path.append('../WhisperLive/examples/client')
sys.path.append('../examples/client')
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import StreamingResponse
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

app = FastAPI()

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
async def list_files(folder: str = "/app/data"):
    abs_folder = os.path.abspath(folder)
    if not os.path.isdir(abs_folder):
        return {"error": "Folder does not exist"}
    files = [
        os.path.abspath(os.path.join(abs_folder, f))
        for f in os.listdir(abs_folder)
        if os.path.isfile(os.path.join(abs_folder, f)) and f.lower().endswith('.wav')
    ]
    return {"files": files}

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
async def simulate_trancription(request: FileRequest):
    """Simulate ASR transcription by reading a jsonl file with the following format and appending a delay corresponding to the end-start time difference.
    {"text": "some text", "start": 0.0, "end": 1.23}
    {"text": "some text", "start": 1.23, "end": 2.56}
    """
    import json
    import time

    file_path = request.file_path

    def stream_generator():
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
    return StreamingResponse(stream_generator(), media_type="application/json")
