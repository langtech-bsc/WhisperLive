from typing import List, Dict, Any
from jiwer import wer, cer, Compose, ToLowerCase, RemovePunctuation, RemoveMultipleSpaces, Strip
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

# Preprocessing pipeline used for both reference and hypothesis
DEFAULT_TRANSFORM = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

def compute_single(reference: str, hypothesis: str, transform=DEFAULT_TRANSFORM) -> Dict[str, float]:
    """
    Compute WER and CER between reference and hypothesis strings (after transform).
    """
    ref = transform(reference)
    hyp = transform(hypothesis)
    w = wer(ref, hyp)
    c = cer(ref, hyp)
    return {"wer": float(w), "cer": float(c), "ref": ref, "hyp": hyp}

def compute_per_file_metrics(
    full_transcriptions: List[Dict[str, Any]],
    realtime_transcriptions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Both inputs expected to be lists of dicts with keys:
      - "wav": path
      - "transcript": text

    Output: list of dicts with "wav", "wer", "cer"
    """
    # Build map for quick lookup
    full_map = {entry["wav"]: entry for entry in full_transcriptions}
    rt_map = {entry["wav"]: entry for entry in realtime_transcriptions}

    metrics = []
    for wav, full_entry in tqdm(full_map.items(), desc="Computing metrics"):
        ref = full_entry.get("transcript", "")
        rt_entry = rt_map.get(wav)
        if rt_entry is None:
            logger.warning("No realtime transcription for %s; skipping", wav)
            continue
        hyp = rt_entry.get("transcript", "")
        m = compute_single(ref, hyp)
        metrics.append({"wav": wav, "wer": m["wer"], "cer": m["cer"], "ref": m["ref"], "hyp": m["hyp"]})
    return metrics
