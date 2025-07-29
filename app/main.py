import sys
sys.path.append('../WhisperLive/examples/client')
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from launch_client_from_file import client_from_file

import json

from queue import Queue
import threading

app = FastAPI()

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
        client_from_file(temp_path, model = "medium", transcription_callback=transcription_callback)
        q.put("__END__")

    threading.Thread(target=run_client, daemon=True).start()

    return StreamingResponse(stream_generator(), media_type="text/plain")
