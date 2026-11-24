"""Experiment manifest — human + machine readable snapshot after every save."""

from __future__ import annotations

import json
from pathlib import Path

from src.checkpoint import CheckpointManager, utc_now
from src.paths import load_config


def _file_info(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "rows": 0, "bytes": 0}
    info = {"exists": True, "bytes": path.stat().st_size, "path": str(path)}
    if path.suffix.lower() == ".csv":
        info["rows"] = _count_csv_rows(path)
    else:
        info["rows"] = None
    return info


def _count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        import pandas as pd
        return int(pd.read_csv(path, usecols=["run_key"]).shape[0])
    except Exception:
        import csv
        with open(path, newline="", encoding="utf-8") as f:
            return sum(1 for _ in csv.DictReader(f))


def build_manifest(drive_root: Path) -> dict:
    ckpt = CheckpointManager(drive_root)
    prog = ckpt.load_progress()
    try:
        cfg = load_config()
    except Exception:
        cfg = {}

    files = {
        "generations": _file_info(ckpt.csv_path("generations")),
        "scores_primary": _file_info(ckpt.csv_path("scores_primary")),
        "scores_secondary": _file_info(ckpt.csv_path("scores_secondary")),
        "embeddings": _file_info(ckpt.csv_path("embeddings")),
        "failures": _file_info(ckpt.csv_path("failures")),
        "results_merged": _file_info(drive_root / "outputs" / "results_merged.csv"),
        "progress": _file_info(ckpt.progress_path()),
        "experiment_config": _file_info(drive_root / "experiment_config.json"),
    }

    total_expected = cfg.get("counts", {}).get("generations_total", 13608)
    gen_done = files["generations"]["rows"]
    pri_done = files["scores_primary"]["rows"]
    sec_done = files["scores_secondary"]["rows"]
    emb_done = files["embeddings"]["rows"]

    pilot_on = cfg.get("pilot", {}).get("enabled", False)

    return {
        "format_version": "1.0",
        "project": "fairness_research_stereotype_hyperparameters",
        "experiment_version": cfg.get("experiment_version", prog.get("experiment_version", "v1")),
        "generated_at": utc_now(),
        "drive_root": str(drive_root),
        "phase": prog.get("phase", "unknown"),
        "pilot_mode": pilot_on,
        "last_run_key": prog.get("last_run_key"),
        "progress": prog,
        "row_counts": {
            "generations": gen_done,
            "scores_primary": pri_done,
            "scores_secondary": sec_done,
            "embeddings": emb_done,
            "failures": files["failures"]["rows"],
        },
        "remaining": {
            "generations": max(0, total_expected - gen_done) if not pilot_on else "pilot_or_unknown",
            "scores_primary": max(0, gen_done - pri_done),
            "embeddings": max(0, gen_done - emb_done),
        },
        "totals_expected": cfg.get("counts", {}),
        "files": files,
        "how_to_resume": (
            "Mount Drive, run Colab cells 1-2, then re-run the phase cell that matches "
            "'phase' above. Completed run_keys in checkpoints/*.csv are skipped automatically."
        ),
        "how_to_share_with_assistant": (
            "Run run_export.py or Colab Cell 12. Upload the zip OR the entire "
            "fairness_research/checkpoints/ folder. Include state/MANIFEST.json."
        ),
    }


def write_manifest(drive_root: Path) -> Path:
    drive_root = Path(drive_root)
    state_dir = drive_root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(drive_root)
    manifest_path = state_dir / "MANIFEST.json"
    tmp = manifest_path.with_suffix(".tmp.json")
    with open(tmp, "w") as f:
        json.dump(manifest, f, indent=2)
    tmp.replace(manifest_path)

    summary_path = state_dir / "SESSION_SUMMARY.txt"
    lines = [
        "FAIRNESS RESEARCH — SESSION SUMMARY",
        "=" * 50,
        f"Updated: {manifest['generated_at']}",
        f"Phase: {manifest['phase']}",
        f"Pilot mode: {manifest['pilot_mode']}",
        "",
        "ROW COUNTS (what is saved on Drive):",
        f"  generations:      {manifest['row_counts']['generations']}",
        f"  scores_primary:   {manifest['row_counts']['scores_primary']}",
        f"  scores_secondary:{manifest['row_counts']['scores_secondary']}",
        f"  embeddings:       {manifest['row_counts']['embeddings']}",
        f"  failures:         {manifest['row_counts']['failures']}",
        "",
        "REMAINING WORK:",
        f"  generations:      {manifest['remaining']['generations']}",
        f"  scores_primary:   {manifest['remaining']['scores_primary']}",
        f"  embeddings:       {manifest['remaining']['embeddings']}",
        "",
        f"Last completed run_key: {manifest.get('last_run_key', 'none')}",
        "",
        "FILES ON DRIVE:",
    ]
    for name, info in manifest["files"].items():
        if info.get("exists"):
            rows = info["rows"]
            row_str = f"{rows} rows" if rows is not None else "json"
            lines.append(f"  {name}: {row_str} ({info['bytes']} bytes)")
    lines.extend([
        "",
        "TO SHARE WITH YOUR ASSISTANT:",
        "  1. Run: python run_export.py  (or Colab Cell 12)",
        "  2. Download: exports/fairness_experiment_latest.zip",
        "  3. Upload that zip in chat — assistant reads MANIFEST.json + CSVs immediately",
        "",
    ])
    summary_path.write_text("\n".join(lines), encoding="utf-8")

    readme = drive_root / "checkpoints" / "README.txt"
    readme.write_text(
        "CHECKPOINT FILES — each row = one completed experiment unit\n\n"
        "generations.csv      — model outputs (text, temperature, top_p, seed)\n"
        "scores_primary.csv   — Llama judge stereotype scores (0-3)\n"
        "scores_secondary.csv — Mistral judge (10% subsample for Cohen's kappa)\n"
        "embeddings.csv       — semantic distance vs stereotype references\n"
        "failures.csv         — errors/refusals (does not block resume)\n"
        "*.bak.csv            — backup snapshots every 50 rows\n\n"
        "Join key for all tables: run_key\n"
        "Format: model|prompt_id|temperature|top_p|seed\n",
        encoding="utf-8",
    )

    return manifest_path
