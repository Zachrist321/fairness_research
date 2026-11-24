#!/usr/bin/env python3
"""Run locally to verify the supplement package before uploading to Colab."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
errors = []


def check(name, ok, detail=""):
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        errors.append(name)


def main():
    print("Validating joint_supplement_colab package...\n")

    required = [
        "Joint_Effect_Supplement.ipynb",
        "run_generation_supplement.py",
        "merge_and_analyze.py",
        "test_setup.py",
        "diagnose_checkpoint.py",
        "clean_checkpoint.py",
        "backup_checkpoint.py",
        "prompts_gender.csv",
        "data/v1_gender_existing.csv",
        "README.md",
    ]
    for f in required:
        check(f"file: {f}", (ROOT / f).exists())

    print()
    for script in ["run_generation_supplement.py", "merge_and_analyze.py", "test_setup.py"]:
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", str(ROOT / script)],
            capture_output=True,
        )
        check(f"syntax: {script}", r.returncode == 0, r.stderr.decode()[:80] if r.returncode else "")

    print()
    sys.path.insert(0, str(ROOT))
    from run_generation_supplement import (
        PACKAGE_VERSION, build_conditions, build_run_list, load_completed_keys, make_run_key,
    )
    check("package version v4", PACKAGE_VERSION == "4", f"got v{PACKAGE_VERSION}")
    import pandas as pd

    prompts = pd.read_csv(ROOT / "prompts_gender.csv")
    check("prompts_gender rows", len(prompts) == 27, f"got {len(prompts)}")

    v1 = pd.read_csv(ROOT / "data/v1_gender_existing.csv")
    check("v1_gender_existing rows", len(v1) == 974, f"got {len(v1)}")

    r0 = v1.iloc[0]
    key_ok = r0["run_key"] == make_run_key(
        r0["model_name"], r0["prompt_id"], r0["temperature"], r0["top_p"], r0["seed"]
    )
    check("run_key format matches V1", key_ok)

    completed, _, _ = load_completed_keys()
    check("V1 keys in skip set", len(set(v1["run_key"]) - completed) == 0)

    runs, completed, _, supp_n = build_run_list()
    expected = 970 - supp_n
    check("remaining to generate", len(runs) == expected, f"got {len(runs)}, expect {expected}")

    conds = build_conditions()
    check("8 conditions", len(conds) == 8, str(conds))

    print()
    r = subprocess.run(
        [sys.executable, str(ROOT / "merge_and_analyze.py")],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    check("merge_and_analyze.py runs", r.returncode == 0, r.stderr[-120:] if r.returncode else "")
    check(
        "figure created",
        (ROOT / "outputs/figures/fig_temp_sweep_x_tier.png").exists(),
    )

    print()
    if errors:
        print(f"FAILED: {len(errors)} check(s): {', '.join(errors)}")
        sys.exit(1)
    print("All checks passed. Safe to upload to Google Drive.")
    print(f"\nUpload folder: {ROOT}")
    print("Colab path:    /content/drive/MyDrive/joint_supplement_colab")


if __name__ == "__main__":
    main()
