"""Phase 2 & 3: Primary and secondary LLM-as-judge scoring."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.checkpoint import CheckpointManager, utc_now
from src.embed_stereoset import select_secondary_sample
from src.judge_hf import HFJudge
from src.paths import drive_root, load_config


def main(phase: str = "primary") -> None:
    config = load_config()
    drive = drive_root()
    os.environ.setdefault("FAIRNESS_DRIVE_ROOT", str(drive))
    ckpt = CheckpointManager(drive)

    gen_df = ckpt.load_csv("generations")
    if gen_df.empty:
        print("No generations found. Run generation phase first.")
        return

    if phase == "primary":
        csv_name = "scores_primary"
        judge_model = config["models"]["judge_primary"]
        skip = ckpt.load_run_keys(csv_name)
        todo = gen_df[~gen_df["run_key"].isin(skip)]
    else:
        csv_name = "scores_secondary"
        judge_model = config["models"]["judge_secondary"]
        skip = ckpt.load_run_keys(csv_name)
        primary_done = ckpt.load_run_keys("scores_primary")
        pool = gen_df[gen_df["run_key"].isin(primary_done)]
        sample_keys = select_secondary_sample(
            pool["run_key"],
            config.get("secondary_judge_fraction", 0.1),
            config.get("secondary_judge_sample_seed", 2026),
        )
        todo = pool[pool["run_key"].isin(sample_keys) & ~pool["run_key"].isin(skip)]

    print(f"Judge: {judge_model} | Phase: {phase} | {len(todo)} rows to score")

    judge = HFJudge(judge_model, load_in_4bit=config["generation"].get("load_in_4bit", True))
    skip_count = len(skip)
    saved = 0
    failed = 0
    try:
        judge.load()
        for _, row in tqdm(todo.iterrows(), total=len(todo)):
            try:
                result = judge.score(str(row["generated_text"]))
                if not result.get("parse_ok"):
                    failed += 1
                    ckpt.log_failure(
                        phase, row["run_key"],
                        model_name=row["model_name"],
                        prompt_id=row["prompt_id"],
                        temperature=row["temperature"],
                        top_p=row["top_p"],
                        seed=int(row["seed"]),
                        error_type="parse_error",
                        error_message=result.get("justification", "")[:200],
                    )
                    continue
                out = {
                    "run_key": row["run_key"],
                    "model_name": row["model_name"],
                    "prompt_id": row["prompt_id"],
                    "prompt_tier": row["prompt_tier"],
                    "demographic_dimension": row["demographic_dimension"],
                    "temperature": row["temperature"],
                    "top_p": row["top_p"],
                    "seed": int(row["seed"]),
                    "stereotype_score": result["stereotype_score"],
                    "stereotype_type": result["stereotype_type"],
                    "justification": result["justification"],
                    "judge_model": judge_model,
                    "timestamp": utc_now(),
                }
                ckpt.append_row(csv_name, out)
                saved += 1
                key = "scores_primary_done" if phase == "primary" else "scores_secondary_done"
                ckpt.save_progress(
                    phase=f"judge_{phase}",
                    **{key: skip_count + saved},
                    last_run_key=row["run_key"],
                )
            except Exception as e:
                failed += 1
                ckpt.log_failure(
                    phase, row["run_key"],
                    model_name=row["model_name"],
                    prompt_id=row["prompt_id"],
                    error_type=type(e).__name__,
                    error_message=str(e)[:500],
                )
    finally:
        judge.unload()

    ckpt.log_session(f"Judge {phase} done. saved={skip_count + saved} new={saved} failed={failed}")
    ckpt.sync_progress_counts()
    _export(drive)
    print(f"Judge {phase} complete. {saved} new rows saved ({skip_count + saved} total on Drive). {failed} failed this run.")


def _export(drive):
    try:
        from run_export import export_bundle
        z = export_bundle(drive)
        print(f"Saved export bundle: {z}")
    except Exception as e:
        print(f"Export skipped: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["primary", "secondary"], default="primary")
    args = parser.parse_args()
    main(phase=args.phase)
