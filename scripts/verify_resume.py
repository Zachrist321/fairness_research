#!/usr/bin/env python3
"""Verify checkpoint/resume logic locally before Colab."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code") if (ROOT / "code" / "src").exists() else str(ROOT))

TEST_ROOT = ROOT / "data" / "resume_test"
os.environ["FAIRNESS_DRIVE_ROOT"] = str(TEST_ROOT)


def main():
    from src.checkpoint import CheckpointManager, make_run_key, iter_work_units
    from src.paths import load_config, load_prompts

    if TEST_ROOT.exists():
        import shutil
        shutil.rmtree(TEST_ROOT)
    TEST_ROOT.mkdir(parents=True)
    import shutil
    shutil.copy2(ROOT / "experiment_config.json", TEST_ROOT / "experiment_config.json")
    (TEST_ROOT / "prompts").mkdir(exist_ok=True)
    shutil.copy2(ROOT / "prompts" / "prompts_v1.csv", TEST_ROOT / "prompts" / "prompts_v1.csv")

    ckpt = CheckpointManager(TEST_ROOT)
    cfg = load_config()
    prompts = load_prompts(cfg)
    p0 = prompts.iloc[0]
    model = cfg["models"]["generators"][0]
    cond = cfg["hyperparameter_grid"][0]

    key = make_run_key(model, p0["prompt_id"], cond["temperature"], cond["top_p"], 42)
    ckpt.append_row("generations", {
        "run_key": key, "model_name": "model/a", "prompt_id": "p1",
        "prompt_set_id": "s1", "prompt_tier": "implicit", "demographic_dimension": "gender",
        "prompt_text": "test", "temperature": 0.7, "top_p": 1.0, "seed": 42,
        "generated_text": "hello", "token_count": 1, "word_count": 1,
        "refusal_flag": 0, "truncated_flag": 0, "timestamp": "now",
    })

    # Duplicate append should be ignored
    ckpt.append_row("generations", {
        "run_key": key, "model_name": "model/a", "prompt_id": "p1",
        "prompt_set_id": "s1", "prompt_tier": "implicit", "demographic_dimension": "gender",
        "prompt_text": "test", "temperature": 0.7, "top_p": 1.0, "seed": 42,
        "generated_text": "DUPLICATE", "token_count": 1, "word_count": 1,
        "refusal_flag": 0, "truncated_flag": 0, "timestamp": "now",
    })

    df = ckpt.load_csv("generations")
    assert len(df) == 1, f"Expected 1 row, got {len(df)}"
    assert df.iloc[0]["generated_text"] == "hello", "Duplicate overwrote row!"

    skip = ckpt.load_run_keys("generations")
    units = iter_work_units(
        prompts.head(1), [model],
        [cond], [42], skip_keys=skip,
    )
    assert len(units) == 0, f"Should skip completed key, got {len(units)} units"

    ckpt.sync_progress_counts()
    prog = ckpt.load_progress()
    assert prog["generations_done"] == 1

    print("ALL RESUME CHECKS PASSED")
    print(f"  run_key format: {key}")
    print(f"  generations on disk: {len(df)}")


if __name__ == "__main__":
    main()
