#!/usr/bin/env python3
"""Idempotent Drive setup — never wipes experiment progress or checkpoints."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def setup(drive_root: Path, *, sync_code: bool = True) -> None:
    folders = [
        "checkpoints", "state", "logs", "outputs/stats", "outputs/figures", "prompts", "code", "scripts",
    ]
    for f in folders:
        (drive_root / f).mkdir(parents=True, exist_ok=True)

    # Never overwrite live experiment config or progress (resume-safe)
    config_dest = drive_root / "experiment_config.json"
    if not config_dest.exists():
        shutil.copy2(ROOT / "experiment_config.json", config_dest)
        print("Created experiment_config.json on Drive")
    else:
        print("Kept existing experiment_config.json (resume-safe)")

    prompts_dest = drive_root / "prompts" / "prompts_v1.csv"
    if not prompts_dest.exists():
        shutil.copy2(ROOT / "prompts" / "prompts_v1.csv", prompts_dest)
        print("Created prompts_v1.csv on Drive")
    else:
        print("Kept existing prompts_v1.csv")

    progress_path = drive_root / "state" / "progress.json"
    if not progress_path.exists():
        progress = {
            "experiment_version": "v1",
            "phase": "setup",
            "generations_done": 0,
            "generations_total": 13608,
            "scores_primary_done": 0,
            "scores_secondary_done": 0,
            "embeddings_done": 0,
        }
        with open(progress_path, "w") as f:
            json.dump(progress, f, indent=2)
        print("Created progress.json")
    else:
        print("Kept existing progress.json (resume-safe)")

    if sync_code:
        code_dest = drive_root / "code"
        code_dest.mkdir(exist_ok=True)
        if (ROOT / "src").exists():
            src_dest = code_dest / "src"
            if src_dest.exists():
                shutil.rmtree(src_dest)
            shutil.copytree(ROOT / "src", src_dest)
        for script in ROOT.glob("run_*.py"):
            shutil.copy2(script, code_dest / script.name)
        shutil.copy2(ROOT / "scripts" / "setup_drive.py", drive_root / "scripts" / "setup_drive.py")
        print("Synced code/ from uploaded project folder")

    print(f"Setup OK at {drive_root}")


if __name__ == "__main__":
    drive = Path(os.environ.get("FAIRNESS_DRIVE_ROOT", "/content/drive/MyDrive/fairness_research"))
    setup(drive)
