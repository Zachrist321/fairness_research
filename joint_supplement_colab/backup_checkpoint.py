"""
Sync checkpoint Drive + local, write numbered backup on Drive.

  !python backup_checkpoint.py

To download to your computer, run the next lines in the SAME notebook cell
or in a separate cell (not via !python — that breaks Colab download):

  from google.colab import files
  files.download("outputs/generations_supplement.csv")
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from run_generation_supplement import (
    DRIVE_CSV, LOCAL_CSV, PACKAGE_VERSION, bootstrap_checkpoints, count_valid_supplement,
)


def main():
    print(f"backup_checkpoint (package v{PACKAGE_VERSION})")
    n = bootstrap_checkpoints()
    print(f"Valid supplement stories: {n}")
    print(f"  Drive: {DRIVE_CSV} ({DRIVE_CSV.stat().st_size if DRIVE_CSV.exists() else 0:,} bytes)")
    if LOCAL_CSV.exists():
        print(f"  Local: {LOCAL_CSV} ({LOCAL_CSV.stat().st_size:,} bytes)")

    backup = DRIVE_CSV.parent / f"generations_supplement_backup_{n}.csv"
    if DRIVE_CSV.exists():
        shutil.copy2(DRIVE_CSV, backup)
        print(f"  Drive backup: {backup.name}")

    remaining = 970 - n
    print(f"  Supplement remaining: {remaining} (then merge with 974 V1 = {1944 - 974 - remaining}/1944 done)")
    print()
    print("To download to your Mac, run IN a notebook cell (not !python):")
    print('  from google.colab import files')
    print(f'  files.download("{DRIVE_CSV}")')


if __name__ == "__main__":
    main()
