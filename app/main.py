import sys
sys.path.append('../WhisperLive/examples/client')
sys.path.append('../examples/client')
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from launch_client_from_file import client_from_file
import config

from queue import Queue
import threading
# MODEL = "tiny"  # Default model, can be changed as needed
# HOST = "renfe-whisperlive-gpu-asr" # "localhost"
# PORT = "9090"  # Default port, can be changed as needed
MODEL = config.settings.ASR_MODEL
LANGUAGE = config.settings.ASR_LANGUAGE
MUTE_AUDIO_PLAYBACK = config.settings.ASR_MUTE_AUDIO_PLAYBACK
HOST = config.settings.ASR_SERVER
PORT = config.settings.ASR_PORT

app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "WhisperLive API is running"}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    q = Queue()

    def transcription_callback(text):
        q.put(text)  # Called by TranscriptionClient during processing

    def stream_generator():
        while True:
            chunk = q.get()
            if chunk == "__END__":
                break
            yield f"{chunk}\n"

    # Run client_from_file in a separate thread so it doesn't block
    def run_client():
        client_from_file(temp_path, server_IP = HOST, port = PORT, model = MODEL, language = LANGUAGE, 
                         transcription_callback=transcription_callback, mute_audio_playback=MUTE_AUDIO_PLAYBACK)
        q.put("__END__")

    threading.Thread(target=run_client, daemon=True).start()

    return StreamingResponse(stream_generator(), media_type="text/plain")
