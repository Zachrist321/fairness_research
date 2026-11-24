"""Phase 1: Generate text completions and checkpoint to Drive."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.checkpoint import CheckpointManager, iter_work_units, utc_now
from src.generate_hf import HFGenerator
from src.paths import drive_root, load_config, load_prompts


def main(pilot: bool = False) -> None:
    config = load_config()
    if pilot:
        config["pilot"] = {**config.get("pilot", {}), "enabled": True}

    drive = drive_root()
    os.environ.setdefault("FAIRNESS_DRIVE_ROOT", str(drive))
    ckpt = CheckpointManager(drive)
    ckpt.ensure_dirs()

    prompts = load_prompts(config)
    skip = ckpt.load_run_keys("generations")
    units = iter_work_units(
        prompts,
        config["models"]["generators"],
        config["hyperparameter_grid"],
        config["seeds"],
        skip_keys=skip,
        pilot=config.get("pilot") if pilot or config.get("pilot", {}).get("enabled") else None,
    )

    print(f"Drive root: {drive}")
    print(f"Skipping {len(skip)} completed rows. {len(units)} remaining.")

    gen_cfg = config["generation"]
    by_model: dict[str, list] = {}
    for u in units:
        by_model.setdefault(u["model_name"], []).append(u)

    done = len(skip)
    for model_id, model_units in by_model.items():
        print(f"\n=== Loading {model_id} ===")
        gen = HFGenerator(model_id, load_in_4bit=gen_cfg.get("load_in_4bit", True))
        try:
            for unit in tqdm(model_units, desc=model_id.split("/")[-1]):
                try:
                    out = gen.generate(
                        unit["prompt_text"],
                        temperature=unit["temperature"],
                        top_p=unit["top_p"],
                        seed=unit["seed"],
                        max_new_tokens=gen_cfg.get("max_new_tokens", 400),
                    )
                    row = {
                        **unit,
                        **out,
                        "timestamp": utc_now(),
                    }
                    ckpt.append_row("generations", row)
                    done += 1
                    ckpt.save_progress(
                        phase="generation",
                        current_model=model_id,
                        generations_done=done,
                        generations_total=config["counts"]["generations_total"],
                        last_run_key=unit["run_key"],
                    )
                except Exception as e:
                    ckpt.log_failure(
                        "generation", unit["run_key"],
                        model_name=model_id,
                        prompt_id=unit["prompt_id"],
                        temperature=unit["temperature"],
                        top_p=unit["top_p"],
                        seed=unit["seed"],
                        error_type=type(e).__name__,
                        error_message=str(e)[:500],
                    )
        finally:
            gen.unload()

    ckpt.log_session(f"Generation complete. total_done={done}")
    ckpt.sync_progress_counts()
    _export(drive)
    print(f"Generation phase done. {done} rows on Drive.")


def _export(drive):
    try:
        from run_export import export_bundle
        z = export_bundle(drive)
        print(f"Saved export bundle: {z}")
    except Exception as e:
        print(f"Export skipped: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    if not os.environ.get("HF_TOKEN") and not os.environ.get("HUGGING_FACE_HUB_TOKEN"):
        print("WARNING: Set HF_TOKEN before running (Hugging Face access token).")
    main(pilot=args.pilot)
