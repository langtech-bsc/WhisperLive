from typing import List, Dict, Any
from jiwer import wer, cer, Compose, ToLowerCase, RemovePunctuation, RemoveMultipleSpaces, Strip
import logging
from tqdm import tqdm
from difflib import SequenceMatcher
from num2words import num2words
import re

logger = logging.getLogger(__name__)

class ReplaceNumbersWithWords:
    def __init__(self, lang="es"):
        self.lang = lang

    def __call__(self, text: str) -> str:
        def replace_number(match):
            number = match.group()
            try:
                # Convert to integer or float, handle large numbers safely
                return num2words(float(number) if "." in number else int(number), lang=self.lang)
            except Exception:
                return number  # fallback if something fails

        # Replace all numbers (integers and decimals)
        return re.sub(r"\d+(\.\d+)?", replace_number, text)

# Preprocessing pipeline used for both reference and hypothesis
DEFAULT_TRANSFORM = Compose([
    ToLowerCase(),
    ReplaceNumbersWithWords(lang="es"),   
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

def extract_error_context(ref, hyp, window=3):
    """
    Extract short contexts around mismatched parts between reference and hypothesis.
    Returns a list of dicts: [{"ref_context": ..., "hyp_context": ...}, ...]
    """
    ref_words = ref.split()
    hyp_words = hyp.split()
    sm = SequenceMatcher(None, ref_words, hyp_words)
    errors = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            # Grab context around the change
            ref_start = max(i1 - window, 0)
            ref_end = min(i2 + window, len(ref_words))
            hyp_start = max(j1 - window, 0)
            hyp_end = min(j2 + window, len(hyp_words))

            ref_context = " ".join(ref_words[ref_start:ref_end])
            hyp_context = " ".join(hyp_words[hyp_start:hyp_end])
            errors.append({"ref_context": ref_context, "hyp_context": hyp_context})
    return errors

def compute_single(reference: str, hypothesis: str, transform=DEFAULT_TRANSFORM) -> Dict[str, float]:
    """
    Compute WER and CER between reference and hypothesis strings (after transform).
    """
    ref = transform(reference)
    hyp = transform(hypothesis)
    w = wer(ref, hyp)
    c = cer(ref, hyp)
    errors = extract_error_context(ref, hyp)
    return {"wer": float(w), "cer": float(c), "ref": ref, "hyp": hyp, "errors": errors}

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
        metrics.append({"wav": wav, "wer": m["wer"], "cer": m["cer"], "ref": m["ref"], "hyp": m["hyp"], "errors": m["errors"]})
    return metrics
