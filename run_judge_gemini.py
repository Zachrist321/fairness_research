"""Phase 2 & 3: Gemini LLM-as-judge scoring for 10% sample (top stereotype similarity)."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.checkpoint import CheckpointManager, utc_now, DEFAULT_COLUMNS
from src.judge_gemini import GeminiJudge
from src.paths import drive_root, load_config

# Register scores_gemini columns in the checkpoint system
DEFAULT_COLUMNS["scores_gemini"] = DEFAULT_COLUMNS["scores_secondary"]

def main() -> None:
    config = load_config()
    drive = drive_root()
    os.environ.setdefault("FAIRNESS_DRIVE_ROOT", str(drive))
    ckpt = CheckpointManager(drive)

    # Read API Key
    api_key_path = drive / "outputs" / "api_key.env"
    if not api_key_path.exists():
        print(f"API key file not found at {api_key_path}")
        return
    
    api_key = api_key_path.read_text().strip()
    if not api_key:
        print("API key is empty")
        return

    # Load results_merged.csv to get the stereotype_similarity
    merged_path = drive / "outputs" / "results_merged.csv"
    if not merged_path.exists():
        print("No results_merged.csv found. Run analysis first.")
        return
    
    df = pd.read_csv(merged_path)
    
    # Select top 388 stories (10% of total) by stereotype_similarity
    top_388 = df.sort_values(by="stereotype_similarity", ascending=False).head(388)
    
    csv_name = "scores_gemini"
    skip = ckpt.load_run_keys(csv_name)
    todo = top_388[~top_388["run_key"].isin(skip)]

    print(f"Judge: Gemini-2.5-Flash | {len(top_388)} total target rows | {len(todo)} rows to score")

    if len(todo) == 0:
        print("All rows already scored.")
        return

    judge = GeminiJudge(api_key=api_key, model_id="gemini-2.5-flash")
    done = len(skip)
    
    try:
        judge.load()
        for idx, (_, row) in enumerate(tqdm(todo.iterrows(), total=len(todo))):
            run_key = row["run_key"]
            try:
                # Sleep 4.2 seconds between requests to stay under 15 RPM
                if idx > 0:
                    time.sleep(4.2)
                
                result = judge.score(str(row["generated_text"]))
                if not result.get("parse_ok"):
                    ckpt.log_failure(
                        "gemini", run_key,
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
                    "run_key": run_key,
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
                    "judge_model": "gemini-2.5-flash",
                    "timestamp": utc_now(),
                }
                ckpt.append_row(csv_name, out)
                done += 1
                ckpt.save_progress(phase="judge_gemini", scores_gemini_done=done, last_run_key=run_key)
            except Exception as e:
                ckpt.log_failure(
                    "gemini", run_key,
                    model_name=row["model_name"],
                    prompt_id=row["prompt_id"],
                    error_type=type(e).__name__,
                    error_message=str(e)[:500],
                )
    finally:
        judge.unload()

    ckpt.log_session(f"Gemini judge done. total={done}")
    print(f"Gemini judge complete. {done} rows saved.")

if __name__ == "__main__":
    main()
