"""
Run this BEFORE generation to see exactly what the script will skip.

  !python diagnose_checkpoint.py
"""

from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from run_generation_supplement import (
    DRIVE_CSV, LOCAL_CSV, PACKAGE_VERSION, PROGRESS_TXT, V1_CSV,
    ROOT as SCRIPT_ROOT, build_run_list, is_valid_story, load_completed_keys,
    bootstrap_checkpoints,
)


def count_csv_pandas(path: Path) -> int:
    if not path.exists():
        return -1
    import pandas as pd
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    if "run_key" not in df.columns:
        return -2
    if path.name == "generations_supplement.csv":
        if "generated_text" not in df.columns:
            return -3
        return int(df["generated_text"].apply(is_valid_story).sum())
    return len(df)


def main():
    print("=== CHECKPOINT DIAGNOSTIC ===\n")
    print(f"Package version: {PACKAGE_VERSION}  (need v4 on Colab)\n")
    print(f"Colab working directory:  {os.getcwd()}")
    print(f"Script folder (ROOT):     {SCRIPT_ROOT}")
    print(f"Same folder?               {Path(os.getcwd()).resolve() == SCRIPT_ROOT.resolve()}")
    print()

    for label, path in [
        ("V1 data", V1_CSV),
        ("Drive checkpoint", DRIVE_CSV),
        ("Local checkpoint", LOCAL_CSV),
    ]:
        print(f"{label}:")
        print(f"  Path:    {path}")
        print(f"  Exists:  {path.exists()}")
        if path.exists():
            print(f"  Size:    {path.stat().st_size:,} bytes")
            n = count_csv_pandas(path)
            if n >= 0:
                print(f"  Stories: {n}")
            else:
                print(f"  Stories: ERROR reading file (code {n})")
        print()

    out_dir = SCRIPT_ROOT / "outputs"
    if out_dir.exists():
        print("Files in outputs/:")
        for f in sorted(out_dir.iterdir()):
            print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
    else:
        print("outputs/ folder DOES NOT EXIST on Drive!")
    print()

    bootstrap_checkpoints()
    completed, v1_n, supp_n = load_completed_keys()
    runs, _, _, _ = build_run_list()

    print("What the generation script will do:")
    print(f"  Skip (V1):         {v1_n}")
    print(f"  Skip (supplement): {supp_n}")
    print(f"  Total skip:        {len(completed)}")
    print(f"  Still generate:    {len(runs)}")
    print()

    if DRIVE_CSV.exists():
        import pandas as pd
        df = pd.read_csv(DRIVE_CSV, encoding="utf-8-sig", low_memory=False)
        invalid = int((~df["generated_text"].apply(is_valid_story)).sum())
        if invalid:
            print(f"WARNING: {invalid} rows in checkpoint are empty/too-short (will NOT be skipped)")
            print("  Run: !python clean_checkpoint.py")
            print()

    if PROGRESS_TXT.exists():
        prog = PROGRESS_TXT.read_text(encoding="utf-8")
        for line in prog.splitlines():
            if line.startswith("completed="):
                claimed = line.split("=", 1)[1].strip()
                actual = f"{len(completed)}/1944"
                if claimed != actual:
                    print(f"WARNING: progress file says {claimed} but valid stories = {actual}")
                    print("  Run: !python clean_checkpoint.py")
                else:
                    print(f"Progress file matches valid stories: {actual}")
                break
        print()

    if supp_n == 0:
        print("*** PROBLEM: supplement checkpoint = 0 stories ***")
        print("The script will regenerate ALL ~970 new stories.")
        print()
        print("If you had ~400 left, this file should have ~570 rows:")
        print(f"  {DRIVE_CSV}")
        print()
        print("Check:")
        print("  1. Is generations_supplement.csv in outputs/ on THIS Drive?")
        print("  2. Did you upload the folder FROM old Drive (with outputs/),")
        print("     or the original empty package from your computer?")
    elif len(runs) <= 450:
        print(f"Looks correct — about {len(runs)} stories left to generate.")
    else:
        print(f"Expected ~400 left but script sees {len(runs)}.")
        print("Checkpoint may be incomplete — check file size above.")


if __name__ == "__main__":
    main()
