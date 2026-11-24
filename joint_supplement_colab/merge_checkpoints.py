"""
Merge two supplement checkpoint files (e.g. old Drive + new Drive).

Use when you switched Google accounts and have generations_supplement.csv
from BOTH places.

Usage in Colab:
  1. Upload old CSV to Drive as:  outputs/generations_supplement_OLD.csv
  2. Keep new CSV at:            outputs/generations_supplement.csv
  3. Run:  !python merge_checkpoints.py
  4. Re-run: !python run_generation_supplement.py
     (should show only ~400 remaining)
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
NEW_CSV = OUT / "generations_supplement.csv"
OLD_CSV = OUT / "generations_supplement_OLD.csv"
MERGED_CSV = OUT / "generations_supplement.csv"
BACKUP_CSV = OUT / "generations_supplement_backup.csv"

FIELDNAMES = [
    "run_key", "model_name", "prompt_id", "prompt_set_id", "prompt_tier",
    "demographic_dimension", "prompt_text", "temperature", "top_p", "seed",
    "generated_text", "word_count", "refusal_flag", "truncated_flag",
]


def load_rows(path: Path) -> dict[str, dict]:
  rows = {}
  if not path.exists():
    return rows
  with open(path, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
      rk = (row.get("run_key") or "").strip()
      text = (row.get("generated_text") or "").strip()
      if rk and text:
        rows[rk] = row
  return rows


def main():
  OUT.mkdir(parents=True, exist_ok=True)

  sources = []
  if OLD_CSV.exists():
    sources.append(("OLD", OLD_CSV))
  if NEW_CSV.exists():
    sources.append(("NEW", NEW_CSV))

  if not sources:
    print("No checkpoint files found.")
    print(f"Put your old Drive CSV here: {OLD_CSV}")
    print(f"Put your new Drive CSV here: {NEW_CSV}")
    return

  merged: dict[str, dict] = {}
  for label, path in sources:
    rows = load_rows(path)
    print(f"  {label} ({path.name}): {len(rows)} stories")
    merged.update(rows)  # NEW overwrites OLD if same key

  print(f"\nMerged total: {len(merged)} unique stories")

  if NEW_CSV.exists():
    NEW_CSV.rename(BACKUP_CSV)
    print(f"Backed up current file to {BACKUP_CSV.name}")

  with open(MERGED_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
    w.writeheader()
    for rk in sorted(merged.keys()):
      w.writerow(merged[rk])

  print(f"Wrote {MERGED_CSV}")
  print("\nNow run:  !python run_generation_supplement.py")
  print("It should show Supplement stories (skip) close to your real progress.")


if __name__ == "__main__":
  main()
