"""Colab session bootstrap — run at the start of every new Colab session."""

from __future__ import annotations

import os
import sys
from pathlib import Path


DRIVE_ROOT_DEFAULT = "/content/drive/MyDrive/fairness_research"


def get_hf_token() -> str:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        return token.strip()
    try:
        from google.colab import userdata
        return userdata.get("HF_TOKEN").strip()
    except Exception:
        pass
    token = input("Paste Hugging Face token (hf_...): ").strip()
    if not token:
        raise RuntimeError("HF_TOKEN is required")
    return token


def bootstrap_session(drive_root: str | None = None, *, mount_drive: bool = False) -> Path:
    """Mount Drive (optional), set env vars, chdir to code/, add to sys.path."""
    root = Path(drive_root or os.environ.get("FAIRNESS_DRIVE_ROOT") or DRIVE_ROOT_DEFAULT)

    if mount_drive:
        from google.colab import drive
        drive.mount("/content/drive")

    code_dir = root / "code"
    if not code_dir.exists():
        raise FileNotFoundError(
            f"Missing {code_dir}. Upload fairness_research to Drive and run setup cell first."
        )

    os.environ["FAIRNESS_DRIVE_ROOT"] = str(root)
    os.chdir(code_dir)
    if str(code_dir) not in sys.path:
        sys.path.insert(0, str(code_dir))

    return root


def print_resume_status(drive_root: Path) -> None:
    from src.checkpoint import CheckpointManager
    from src.manifest import write_manifest
    ckpt = CheckpointManager(drive_root)
    write_manifest(drive_root)
    prog = ckpt.load_progress()
    print("\n=== RESUME STATUS (from Google Drive) ===")
    print(f"Phase: {prog.get('phase', '?')}")
    for name in ("generations", "scores_primary", "scores_secondary", "embeddings", "failures"):
        n = len(ckpt.load_csv(name))
        print(f"  {name}: {n} rows")
    print(f"Last run_key: {prog.get('last_run_key', 'none')}")
    print(f"Manifest: {drive_root / 'state' / 'MANIFEST.json'}")
    print(f"Summary:  {drive_root / 'state' / 'SESSION_SUMMARY.txt'}")
    print(f"Export:   {drive_root / 'exports' / 'fairness_experiment_latest.zip'}")
    print("=========================================\n")
