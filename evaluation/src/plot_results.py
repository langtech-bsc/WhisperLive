import matplotlib.pyplot as plt
from typing import List, Dict, Any
from pathlib import Path
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def plot_scatter_duration(metrics: List[Dict[str, Any]], metadata: List[Dict[str, Any]], out_png: str, metric_key: str = "wer"):
    """
    Plot scatter metric (wer/cer) vs duration.
    metrics: list of dicts {"wav": path, "wer": float, ...}
    metadata: list of dicts {"wav": path, "duration": float, ...}
    """
    df_metrics = pd.DataFrame(metrics)
    df_meta = pd.DataFrame(metadata)
    df = df_metrics.merge(df_meta, on="wav", how="left")
    if df.empty:
        logger.warning("No data to plot for %s", metric_key)
        return
    plt.figure(figsize=(6,4))
    plt.scatter(df["duration"], df[metric_key], alpha=0.6)
    plt.xlabel("Duration (s)")
    plt.ylabel(metric_key.upper())
    plt.title(f"{metric_key.upper()} vs Duration")
    plt.grid(True, linestyle="--", alpha=0.4)
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, bbox_inches="tight")
    plt.close()
    logger.info("Saved scatter plot to %s", out_png)

def plot_comparison_box(metrics_by_model: Dict[str, List[Dict[str, Any]]], out_png: str, metric_key: str = "wer"):
    """
    Create a boxplot comparing multiple models.
    metrics_by_model: {"tiny": [{...}, ...], "large-v2": [{...}, ...]}
    """
    label_order = list(metrics_by_model.keys())
    data = []
    for m in label_order:
        vals = [x.get(metric_key, None) for x in metrics_by_model[m]]
        vals = [v for v in vals if v is not None]
        data.append(vals)
    plt.figure(figsize=(8,4))
    plt.boxplot(data, labels=label_order, showmeans=True)
    plt.ylabel(metric_key.upper())
    plt.title(f"Comparison of {metric_key.upper()} across models")
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, bbox_inches="tight")
    plt.close()
    logger.info("Saved comparison boxplot to %s", out_png)
