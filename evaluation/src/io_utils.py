import json
import yaml
import csv
from pathlib import Path
from typing import Any, Dict, List, Union
import logging

logger = logging.getLogger(__name__)

def load_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_yaml(data: Dict[str, Any], path: Union[str, Path]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

def load_json(path: Union[str, Path]) -> Any:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json(obj: Any, path: Union[str, Path]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def save_csv(rows: List[Dict[str, Any]], path: Union[str, Path]) -> None:

    logging.info("Saving CSV to %s", path)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        logger.warning("save_csv called with empty rows.")
        return
    # Use union of keys for header
    keys = []
    for r in rows:
        for k in r.keys():
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def read_file_list(path: Union[str, Path]) -> List[str]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    return lines
