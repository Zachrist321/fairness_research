"""Checkpoint I/O: Google Drive persistence and resume logic."""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

DEFAULT_COLUMNS = {
    "generations": [
        "run_key", "model_name", "prompt_id", "prompt_set_id", "prompt_tier",
        "demographic_dimension", "prompt_text", "temperature", "top_p", "seed",
        "generated_text", "token_count", "word_count", "refusal_flag",
        "truncated_flag", "timestamp",
    ],
    "scores_primary": [
        "run_key", "model_name", "prompt_id", "prompt_tier", "demographic_dimension",
        "temperature", "top_p", "seed", "stereotype_score", "stereotype_type",
        "justification", "judge_model", "timestamp",
    ],
    "scores_secondary": [
        "run_key", "model_name", "prompt_id", "prompt_tier", "demographic_dimension",
        "temperature", "top_p", "seed", "stereotype_score", "stereotype_type",
        "justification", "judge_model", "timestamp",
    ],
    "embeddings": [
        "run_key", "model_name", "prompt_id", "prompt_tier", "demographic_dimension",
        "temperature", "top_p", "seed", "semantic_distance", "stereotype_similarity",
        "timestamp",
    ],
    "failures": [
        "run_key", "phase", "model_name", "prompt_id", "temperature", "top_p",
        "seed", "error_type", "error_message", "timestamp",
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_run_key(model: str, prompt_id: str, temperature: float, top_p: float, seed: int) -> str:
    t = round(float(temperature), 6)
    p = round(float(top_p), 6)
    return f"{model}|{prompt_id}|{t}|{p}|{int(seed)}"


class CheckpointManager:
    def __init__(self, drive_root: str | Path):
        self.root = Path(drive_root)
        self.checkpoints = self.root / "checkpoints"
        self.state = self.root / "state"
        self.logs = self.root / "logs"
        self.outputs = self.root / "outputs"
        for d in (self.checkpoints, self.state, self.logs, self.outputs,
                  self.outputs / "stats", self.outputs / "figures"):
            d.mkdir(parents=True, exist_ok=True)

    def csv_path(self, name: str) -> Path:
        return self.checkpoints / f"{name}.csv"

    def backup_path(self, name: str) -> Path:
        return self.checkpoints / f"{name}.bak.csv"

    def progress_path(self) -> Path:
        return self.state / "progress.json"

    def load_csv(self, name: str) -> pd.DataFrame:
        path = self.csv_path(name)
        if not path.exists():
            return pd.DataFrame(columns=DEFAULT_COLUMNS.get(name, []))
        return pd.read_csv(path)

    def load_run_keys(self, name: str) -> set[str]:
        df = self.load_csv(name)
        if df.empty or "run_key" not in df.columns:
            return set()
        return set(df["run_key"].astype(str))

    def append_row(self, name: str, row: dict) -> None:
        """Read CSV, skip duplicate run_key, append one row, write back + backup."""
        path = self.csv_path(name)
        bak = self.backup_path(name)
        cols = DEFAULT_COLUMNS.get(name, list(row.keys()))

        if path.exists():
            df = pd.read_csv(path)
            if "run_key" in row and "run_key" in df.columns:
                if str(row["run_key"]) in df["run_key"].astype(str).values:
                    return  # already checkpointed — resume-safe
            if len(df) > 0 and len(df) % 50 == 0:
                shutil.copy2(path, bak)
        else:
            df = pd.DataFrame(columns=cols)

        for c in cols:
            if c not in row:
                row[c] = None
        df.loc[len(df)] = [row.get(c) for c in cols]

        tmp = path.with_suffix(".tmp.csv")
        df.to_csv(tmp, index=False)
        tmp.replace(path)
        self._touch_manifest()

    def _touch_manifest(self) -> None:
        try:
            from src.manifest import write_manifest
            write_manifest(self.root)
        except Exception:
            pass  # never block experiment on manifest write

    def sync_progress_counts(self) -> dict:
        """Refresh progress.json row counts from actual CSV files on Drive."""
        counts = {
            "generations_done": len(self.load_csv("generations")),
            "scores_primary_done": len(self.load_csv("scores_primary")),
            "scores_secondary_done": len(self.load_csv("scores_secondary")),
            "embeddings_done": len(self.load_csv("embeddings")),
            "failures_logged": len(self.load_csv("failures")),
        }
        result = self.save_progress(**counts)
        self._touch_manifest()
        return result

    def log_failure(self, phase: str, run_key: str, **kwargs) -> None:
        row = {
            "run_key": run_key,
            "phase": phase,
            "timestamp": utc_now(),
            **kwargs,
        }
        self.append_row("failures", row)

    def load_progress(self) -> dict:
        path = self.progress_path()
        if not path.exists():
            return {
                "experiment_version": "v1",
                "phase": "generation",
                "generations_done": 0,
                "scores_primary_done": 0,
                "scores_secondary_done": 0,
                "embeddings_done": 0,
            }
        with open(path) as f:
            return json.load(f)

    def save_progress(self, **updates) -> dict:
        prog = self.load_progress()
        prog.update(updates)
        prog["last_updated"] = utc_now()
        tmp = self.progress_path().with_suffix(".tmp.json")
        with open(tmp, "w") as f:
            json.dump(prog, f, indent=2)
        tmp.replace(self.progress_path())
        return prog

    def log_session(self, message: str) -> None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        log_file = self.logs / f"session_{stamp}.txt"
        with open(log_file, "a") as f:
            f.write(f"[{utc_now()}] {message}\n")

    def ensure_dirs(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)


def local_drive_root(config: dict) -> Path:
    """Allow local testing without Colab."""
    env = os.environ.get("FAIRNESS_DRIVE_ROOT")
    if env:
        return Path(env)
    return Path(config.get("drive_root", "/content/drive/MyDrive/fairness_research"))


def iter_work_units(
    prompts_df: pd.DataFrame,
    models: Iterable[str],
    grid: list[dict],
    seeds: list[int],
    *,
    skip_keys: set[str],
    pilot: dict | None = None,
) -> list[dict]:
    units = []
    for _, prompt in prompts_df.iterrows():
        for model in models:
            for cond in grid:
                for seed in seeds:
                    rk = make_run_key(
                        model, prompt["prompt_id"],
                        cond["temperature"], cond["top_p"], seed,
                    )
                    if rk in skip_keys:
                        continue
                    unit = {
                        "run_key": rk,
                        "model_name": model,
                        "prompt_id": prompt["prompt_id"],
                        "prompt_set_id": prompt.get("prompt_set_id", ""),
                        "prompt_tier": prompt["prompt_tier"],
                        "demographic_dimension": prompt["demographic_dimension"],
                        "prompt_text": prompt["prompt_text"],
                        "temperature": cond["temperature"],
                        "top_p": cond["top_p"],
                        "grid_step": cond.get("grid_step", ""),
                        "seed": seed,
                    }
                    if pilot and pilot.get("enabled"):
                        if model not in pilot.get("models", []):
                            continue
                        if prompt["prompt_id"] not in pilot.get("prompt_ids", []):
                            continue
                        allowed = {(c["temperature"], c["top_p"]) for c in pilot.get("conditions", [])}
                        if (cond["temperature"], cond["top_p"]) not in allowed:
                            continue
                        if seed not in pilot.get("seeds", []):
                            continue
                    units.append(unit)
    if pilot and pilot.get("enabled") and pilot.get("max_rows"):
        units = units[: pilot["max_rows"]]
    return units
