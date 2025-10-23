import logging
from pathlib import Path
from typing import Dict, Any, List
import argparse
import shutil
import json

from io_utils import load_yaml, save_yaml, save_json, save_csv, read_file_list, load_json
from run_full_transcription import run_full_transcription
from run_realtime_transcription import run_realtime_transcription
from compute_metrics import compute_per_file_metrics
from plot_results import plot_scatter_duration, plot_comparison_box

logger = logging.getLogger(__name__)

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def read_metadata_for_files(file_list: List[str]) -> List[Dict[str, Any]]:
    """
    Lightweight metadata extraction: duration (via soundfile if available) and path.
    Falls back to duration=None if library missing.
    """
    try:
        import soundfile as sf
    except Exception:
        logger.warning("soundfile not available; duration metadata will be None.")
        return [{"wav": str(Path(w).resolve()), "duration": None} for w in file_list]

    metas = []
    for w in file_list:
        try:
            with sf.SoundFile(w) as f:
                duration = len(f) / f.samplerate
            metas.append({"wav": str(Path(w).resolve()), "duration": float(duration)})
        except Exception as e:
            logger.warning("Could not read %s: %s", w, e)
            metas.append({"wav": str(Path(w).resolve()), "duration": None})
    return metas

def main(config_path: str):
    cfg = load_yaml(config_path)
    # Compose result folder
    cfg_name = Path(config_path).stem
    out_base = Path(cfg.get("output", {}).get("folder", "evaluation/results")) / cfg_name
    ensure_dir(out_base)
    # Save copy of config used
    save_yaml(cfg, out_base / "config_used.yaml")

    # read file list
    file_list_path = cfg["data"]["file_list"]
    files = read_file_list(file_list_path)
    # metadata
    metadata = read_metadata_for_files(files)
    save_json(metadata, out_base / "metadata" / "metadata.json")

    models = cfg.get("models", ["tiny"])
    steps = cfg.get("steps", {})
    metrics_store = {}  # per-model metrics lists

    for model in models:
        model_safe = model.replace("/", "_")
        logger.info("Processing model %s", model)

        # Prepare output paths
        transcriptions_dir = out_base / "transcriptions"
        full_out = transcriptions_dir / "full" / f"{model_safe}.json"
        rt_out = transcriptions_dir / "real_time" / f"{model_safe}.json"
        ensure_dir(full_out.parent)
        ensure_dir(rt_out.parent)

        if steps.get("do_full_file_transcription", True):
            full_res = run_full_transcription(files, model, str(full_out))
        else:
            full_res = load_json_if_exists(full_out)

        if steps.get("do_real_time_transcription", True):
            rt_res = run_realtime_transcription(files, model, str(rt_out))
        else:
            rt_res = load_json_if_exists(rt_out)

        if steps.get("do_compute_metrics", True):
            metrics = compute_per_file_metrics(full_res, rt_res)
            # save metrics
            ensure_dir(out_base / "metrics")
            save_json(metrics, out_base / "metrics" / f"{model_safe}.json")
            metrics_store[model_safe] = metrics

    # summary CSV
    rows = []
    for m, vals in metrics_store.items():
        if not vals:
            continue
        avg_wer = sum(v["wer"] for v in vals) / len(vals)
        avg_cer = sum(v["cer"] for v in vals) / len(vals)
        rows.append({"model": m, "avg_WER": f"{avg_wer:.4f}", "avg_CER": f"{avg_cer:.4f}", "num_files": len(vals)})
    save_csv(rows, out_base / "summary.csv")

    # plotting
    if steps.get("do_plots", True) and metrics_store:
        # scatter for each metric across first model (use metrics+metadata)
        # Use metadata file for durations
        try:
            metadata_list = load_json(out_base / "metadata" / "metadata.json")
        except Exception:
            metadata_list = metadata
        # per-metric scatter (WER & CER) for first model only (can be extended)
        for metric_key, png_name in [("wer", "wer_duration.png"), ("cer", "cer_duration.png")]:
            # use first model to generate scatter, but could be changed to aggregate
            first_model = next(iter(metrics_store.keys()))
            plot_scatter_duration(metrics_store[first_model], metadata_list, str(out_base / "plots" / png_name), metric_key=metric_key)
        # comparison boxplots across models
        plot_comparison_box(metrics_store, str(out_base / "plots" / "wer_comparison.png"), metric_key="wer")
        plot_comparison_box(metrics_store, str(out_base / "plots" / "cer_comparison.png"), metric_key="cer")

    logger.info("Evaluation completed. Results saved to %s", out_base)

def load_json_if_exists(path):
    p = Path(path)
    if p.exists():
        return load_json(p)
    return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the full evaluation pipeline described by a YAML config.")
    parser.add_argument("--config", "-c", required=True, help="Path to YAML config")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    main(args.config)
