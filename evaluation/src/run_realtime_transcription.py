import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from io_utils import save_json
import time
import os
import requests
import json
import coloredlogs

HF_HOME = os.environ.get("HF_HOME", None)
if HF_HOME is None:
    raise EnvironmentError("HF_HOME environment variable is not set. Please set it to the Hugging Face cache directory.")

logger = logging.getLogger(__name__)

# Try to import the TranscriptionClient from whisper_live; if API differs adapt accordingly.
try:
    from whisper_live.client import TranscriptionClient
except Exception as e:
    TranscriptionClient = None
    logger.warning("Could not import TranscriptionClient from whisper_live: %s", e)


class _Collector:
    """
    Simple collector used as callback to gather segments and final transcript.
    """
    def __init__(self):
        self.segments = []
        self.full = ""

    def __call__(self, msg: dict):
        """
        Expected msg to follow the whisper_live client callback shape.
        We'll attempt to gather segments list or final transcript if available.
        """
        # Heuristic: message might contain 'segments' or 'transcript' or partial text.
        print("[DEBUG] Collector received message: %s", msg)
        if not msg:
            return
        if isinstance(msg, dict):
            if "segments" in msg:
                self.segments = msg["segments"]
                # compose transcript if segments present
                self.full = " ".join([s.get("text", "") for s in self.segments]).strip()
            elif "transcript" in msg:
                self.full = msg["transcript"]
            else:
                # fallback: if there's 'text' key
                text = msg.get("text")
                if text:
                    # append as pseudo-segment with timestamp if provided
                    start = float(msg.get("start", 0.0))
                    end = float(msg.get("end", start))
                    self.segments.append({"start": start, "end": end, "text": text})
                    self.full = " ".join([s.get("text", "") for s in self.segments]).strip()
        if isinstance(msg, list):
            # If a list of segments is sent
            self.segments = msg
            self.full = " ".join([s.get("text", "") for s in self.segments]).strip()

def client_from_file_collect(wav_file: str, server_ip: str = "localhost", port: int = 9090,
                             language: Optional[str] = None, model: str = "tiny",
                             transcription_callback=None, mute_audio_playback=True, timeout_s: int = 30):
    """
    Launch a TranscriptionClient pointing to WhisperLive server and run it on wav_file.
    The transcription_callback is invoked with messages; we collect and return final segments/transcript.
    Note: This function assumes TranscriptionClient can be called as in the README examples.

    Returns dict: {"wav": <abs>, "ID": <stem>, "asr": segments_list, "transcript": full_text}
    """
    if TranscriptionClient is None:
        raise ImportError("TranscriptionClient not available. Install whisper_live or adapt this function.")

    collector = _Collector()

    client = TranscriptionClient(
        server_ip,
        port,
        lang=language,
        translate=False,
        model=model,
        use_vad=True,
        mute_audio_playback=mute_audio_playback,
        transcription_callback=collector
    )

    logger.info("Starting realtime client for %s -> %s:%s (model=%s)", wav_file, server_ip, port, model)
    # Call the client with the wav path; many examples use client(wav_file) as callable
    # If the client is a class with run method, adapt accordingly.
    start = time.time()
    client(wav_file)
    # Wait until some text collected (simple blocking wait)
    waited = 0.0
    while waited < timeout_s:
        if collector.full:
            break
        time.sleep(0.2)
        waited = time.time() - start

    result = {
        "wav": str(Path(wav_file).resolve()),
        "ID": Path(wav_file).stem,
        "asr": collector.segments,
        "transcript": collector.full
    }
    return result

def client_from_file_api(wav_file: str, server_ip: str = "localhost", port: int = 9090, model: str = "tiny"):

    url = f"http://{server_ip}:8052/transcribe_file_evaluation"
    request_args = {"files": {"file": open(wav_file, "rb")}, "data": {"model": model},}
    request_kwargs = {"stream": True}

    # Unified streaming processing
    segments = []
    with requests.post(url, **request_args, **request_kwargs) as response:
        for line in response.iter_lines():
            if line:
                segments = json.loads(line.decode("utf-8"))
                logger.info(f"\nReceived {len(segments)} segments")
                for seg in segments:
                    logger.info(f"\t[{seg['start']} - {seg['end']}] {seg['text']}")
            else:
                logger.info("\n***Received empty line (flush)***\n")

    full = " ".join([s.get("text", "") for s in segments]).strip()
    full = full.replace("  ", " ")

    result = {
        "wav": str(Path(wav_file).resolve()),
        "ID": Path(wav_file).stem,
        "asr": segments,
        "transcript": full
    }
    return result

def run_realtime_transcription(file_list: List[str], model_name: str, out_path: str,
                               server_ip: str = "localhost", port: int = 9090, language: Optional[str] = None):
    results = []
    for wav in file_list:
        try:
            # res = client_from_file_collect(wav, server_ip=server_ip, port=port, language=language, model=model_name)
            res = client_from_file_api(wav, server_ip=server_ip, port=port, model = model_name)
            results.append(res)
        except Exception as e:
            logger.exception("Realtime transcription failed for %s: %s", wav, e)
    save_json(results, out_path)
    logger.info("Saved realtime transcriptions to %s", out_path)
    return results

if __name__ == "__main__":
    import argparse
    from io_utils import read_file_list

    parser = argparse.ArgumentParser(description="Run realtime (simulated) transcription using WhisperLive client.")
    parser.add_argument("--file_list", "-f", required=True, help="Path to txt file list")
    parser.add_argument("--model", "-m", required=True, help="Model name for realtime client")
    parser.add_argument("--out", "-o", required=True, help="Output JSON path")
    parser.add_argument("--server", default="localhost", help="WhisperLive server host")
    parser.add_argument("--port", default=9090, type=int, help="WhisperLive server port")
    parser.add_argument("--language", default=None, help="Language code (optional)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    coloredlogs.install(level="INFO", logger=logger)
    wavs = read_file_list(args.file_list)
    run_realtime_transcription(wavs, args.model, args.out, server_ip=args.server, port=args.port, language=args.language)
