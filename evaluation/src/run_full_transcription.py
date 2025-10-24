import logging
from pathlib import Path
from typing import List, Dict, Any
from faster_whisper import WhisperModel
from io_utils import save_json
import os

logger = logging.getLogger(__name__)

HF_HOME = os.environ.get("HF_HOME", None)
if HF_HOME is None:
    raise EnvironmentError("HF_HOME environment variable is not set. Please set it to the Hugging Face cache directory.")

def transcribe_full_file(model_name: str, wav_path: str) -> Dict[str, Any]:
    """
    Transcribe a single audio file with faster_whisper and return a dict:
    {
      "wav": "/abs/path.wav",
      "ID": "<basename>",
      "asr": [ {start, end, text}, ... ],
      "transcript": "<full text>"
    }
    """
    model = WhisperModel(model_name, device="cpu", compute_type="auto")
    segments, info = model.transcribe(wav_path)
    seg_list = []
    pieces = []
    for s in segments:
        seg_list.append({"start": float(s.start), "end": float(s.end), "text": s.text})
        pieces.append(s.text)
    full_text = " ".join(pieces).strip()
    return {"wav": str(Path(wav_path).resolve()), "ID": Path(wav_path).stem, "asr": seg_list, "transcript": full_text}

def run_full_transcription(file_list: List[str], model_name: str, out_path: str) -> List[Dict[str, Any]]:
    """
    Transcribe a list of files and save as JSON to out_path.
    Returns list of transcription dicts.
    """
    results = []
    for wav in file_list:
        logger.info("Transcribing full file: %s with model %s", wav, model_name)
        res = transcribe_full_file(model_name, wav)
        results.append(res)
    save_json(results, out_path)
    logger.info("Saved full-file transcriptions to %s", out_path)
    return results

if __name__ == "__main__":
    import argparse
    from io_utils import read_file_list

    parser = argparse.ArgumentParser(description="Run full-file transcription for a list of wavs.")
    parser.add_argument("--config", "-c", required=False, help="YAML config (optional).")
    parser.add_argument("--file_list", "-f", required=True, help="Path to txt file list")
    parser.add_argument("--model", "-m", required=True, help="Whisper model name (e.g. tiny, large-v2)")
    parser.add_argument("--out", "-o", required=True, help="Output JSON path")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    wavs = read_file_list(args.file_list)
    run_full_transcription(wavs, args.model, args.out)
