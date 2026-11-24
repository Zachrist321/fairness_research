#!/usr/bin/env python3
"""Idempotent Drive setup — never wipes experiment progress or checkpoints."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CONFIG = Path(__file__).parent / "canonical_experiment_config.json"


def _load_canonical_config() -> dict:
    """Source of truth for design — works on Colab even if Drive root config is stale."""
    if CANONICAL_CONFIG.exists():
        return json.loads(CANONICAL_CONFIG.read_text())
    return json.loads((ROOT / "experiment_config.json").read_text())


def setup(drive_root: Path, *, sync_code: bool = True) -> None:
    folders = [
        "checkpoints", "state", "logs", "outputs/stats", "outputs/figures", "prompts", "code", "scripts",
    ]
    for f in folders:
        (drive_root / f).mkdir(parents=True, exist_ok=True)

    # Sync config when experiment_version changes (fixes scaled-design updates).
    # Checkpoints are never touched — only the design file and progress total.
    config_dest = drive_root / "experiment_config.json"
    local_cfg = _load_canonical_config()
    local_ver = local_cfg.get("experiment_version", "v1")
    if not config_dest.exists():
        shutil.copy2(CANONICAL_CONFIG if CANONICAL_CONFIG.exists() else ROOT / "experiment_config.json", config_dest)
        print("Created experiment_config.json on Drive")
    else:
        remote_ver = json.loads(config_dest.read_text()).get("experiment_version", "v1")
        if remote_ver != local_ver:
            shutil.copy2(CANONICAL_CONFIG if CANONICAL_CONFIG.exists() else ROOT / "experiment_config.json", config_dest)
            print(f"Updated experiment_config.json ({remote_ver} → {local_ver})")
        else:
            print("Kept existing experiment_config.json (same version)")

    prompts_dest = drive_root / "prompts" / "prompts_v1.csv"
    if not prompts_dest.exists():
        shutil.copy2(ROOT / "prompts" / "prompts_v1.csv", prompts_dest)
        print("Created prompts_v1.csv on Drive")
    else:
        print("Kept existing prompts_v1.csv")

    progress_path = drive_root / "state" / "progress.json"

    def _patch_progress_total() -> None:
        if not progress_path.exists():
            return
        prog = json.loads(progress_path.read_text())
        total = local_cfg.get("counts", {}).get("generations_total", 3888)
        if prog.get("generations_total") != total or prog.get("experiment_version") != local_ver:
            prog["generations_total"] = total
            prog["experiment_version"] = local_ver
            with open(progress_path, "w") as f:
                json.dump(prog, f, indent=2)
            print(f"Patched progress.json → generations_total={total}")

    if not progress_path.exists():
        progress = {
            "experiment_version": local_ver,
            "phase": "setup",
            "generations_done": 0,
            "generations_total": local_cfg.get("counts", {}).get("generations_total", 3888),
            "scores_primary_done": 0,
            "scores_secondary_done": 0,
            "embeddings_done": 0,
        }
        with open(progress_path, "w") as f:
            json.dump(progress, f, indent=2)
        print("Created progress.json")
    else:
        print("Kept existing progress.json (resume-safe)")
    _patch_progress_total()

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
            print("Synced code/ from uploaded project folder")
        else:
            print("NOTE: No src/ at Drive root — upload src/ from Mac to refresh code/")

    # Always refresh scripts/ helpers (canonical config + setup)
    scripts_dest = drive_root / "scripts"
    scripts_dest.mkdir(exist_ok=True)
    setup_dest = scripts_dest / "setup_drive.py"
    if Path(__file__).resolve() != setup_dest.resolve():
        shutil.copy2(Path(__file__), setup_dest)
    canon_src = CANONICAL_CONFIG if CANONICAL_CONFIG.exists() else ROOT / "experiment_config.json"
    canon_dest = scripts_dest / "canonical_experiment_config.json"
    if canon_src.exists() and canon_src.resolve() != canon_dest.resolve():
        shutil.copy2(canon_src, canon_dest)
        print("Synced scripts/canonical_experiment_config.json")

    print(f"Setup OK at {drive_root}")


if __name__ == "__main__":
    drive = Path(os.environ.get("FAIRNESS_DRIVE_ROOT", "/content/drive/MyDrive/fairness_research"))
    setup(drive)
