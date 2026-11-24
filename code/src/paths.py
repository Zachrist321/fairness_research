"""Shared paths for local Mac testing and Colab Drive execution."""

from __future__ import annotations

import json
import os
from pathlib import Path

# Code directory (where run_*.py live)
CODE_ROOT = Path(__file__).resolve().parent


def drive_root() -> Path:
    env = os.environ.get("FAIRNESS_DRIVE_ROOT")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[1]


def load_config() -> dict:
    with open(drive_root() / "experiment_config.json") as f:
        return json.load(f)


def load_prompts(config: dict | None = None):
    import pandas as pd
    cfg = config or load_config()
    rel = cfg.get("prompts_file", "prompts/prompts_v1.csv")
    return pd.read_csv(drive_root() / rel)
