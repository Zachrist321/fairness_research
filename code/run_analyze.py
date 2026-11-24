"""Phase 5: Statistical analysis and figures."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.analyze import run_analysis
from src.checkpoint import CheckpointManager
from src.paths import drive_root, load_config


def main() -> None:
    config = load_config()
    drive = drive_root()
    ckpt = CheckpointManager(drive)

    print("Running analysis...")
    results = run_analysis(drive)
    ckpt.sync_progress_counts()
    ckpt.log_session(f"Analysis complete: {results}")
    _export(drive)
    print("Analysis results:", results)
    print(f"Outputs in {drive / 'outputs'}")


def _export(drive):
    try:
        from run_export import export_bundle
        z = export_bundle(drive)
        print(f"Saved export bundle: {z}")
    except Exception as e:
        print(f"Export skipped: {e}")


if __name__ == "__main__":
    main()
