"""
Remove invalid rows from generations_supplement.csv (empty / too-short stories).

Run before generation if progress looked ahead of real saved stories:

  !python clean_checkpoint.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from run_generation_supplement import (
    DRIVE_CSV, PACKAGE_VERSION, is_valid_story,
    sync_progress_from_checkpoint, write_checkpoint_csv,
    _read_checkpoint_rows, merge_checkpoint_rows, bootstrap_checkpoints,
)

TOTAL_TARGET = 27 * 8 * 3 * 3


def main():
    print(f"clean_checkpoint (package v{PACKAGE_VERSION})")
    bootstrap_checkpoints()
    if not DRIVE_CSV.exists():
        print(f"No checkpoint at {DRIVE_CSV}")
        return

    import pandas as pd

    df = pd.read_csv(DRIVE_CSV, encoding="utf-8-sig", low_memory=False)
    valid_mask = df["generated_text"].apply(is_valid_story)
    bad = int((~valid_mask).sum())
    before = len(df)

    # keep last valid row per run_key
    valid_df = df[valid_mask].copy()
    dupes = int(valid_df["run_key"].duplicated(keep="last").sum())
    valid_df = valid_df.drop_duplicates(subset="run_key", keep="last")

    if bad == 0 and dupes == 0:
        done = sync_progress_from_checkpoint(TOTAL_TARGET)
        print(f"Checkpoint OK — {len(valid_df)} valid stories, progress synced to {done}/{TOTAL_TARGET}")
        return

    backup = DRIVE_CSV.with_name("generations_supplement_backup.csv")
    shutil.copy2(DRIVE_CSV, backup)
    write_checkpoint_csv(DRIVE_CSV, valid_df.to_dict("records"))
    from run_generation_supplement import LOCAL_CSV, LOCAL_DIR
    if LOCAL_DIR.exists() or Path("/content").exists():
        LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        write_checkpoint_csv(LOCAL_CSV, valid_df.to_dict("records"))

    done = sync_progress_from_checkpoint(TOTAL_TARGET)

    print(f"Cleaned checkpoint: {DRIVE_CSV}")
    print(f"  Backup:           {backup}")
    print(f"  Rows before:      {before}")
    print(f"  Invalid removed:  {bad}")
    print(f"  Duplicates removed: {dupes}")
    print(f"  Valid kept:       {len(valid_df)}")
    print(f"  Progress synced:  {done}/{TOTAL_TARGET}")
    print(f"  Remaining:        {TOTAL_TARGET - done}")


if __name__ == "__main__":
    main()
