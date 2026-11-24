"""Phase 4: Semantic distance embeddings."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from tqdm import tqdm

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.checkpoint import CheckpointManager, utc_now
from src.embed_stereoset import EmbeddingScorer
from src.paths import drive_root, load_config


def main() -> None:
    config = load_config()
    drive = drive_root()
    os.environ.setdefault("FAIRNESS_DRIVE_ROOT", str(drive))
    ckpt = CheckpointManager(drive)

    gen_df = ckpt.load_csv("generations")
    skip = ckpt.load_run_keys("embeddings")
    todo = gen_df[~gen_df["run_key"].isin(skip)]
    print(f"Embeddings: {len(todo)} rows remaining")

    scorer = EmbeddingScorer(config["models"]["embedding"])
    done = len(skip)
    try:
        scorer.load()
        for _, row in tqdm(todo.iterrows(), total=len(todo)):
            try:
                scores = scorer.score(str(row["generated_text"]), str(row["demographic_dimension"]))
                out = {
                    "run_key": row["run_key"],
                    "model_name": row["model_name"],
                    "prompt_id": row["prompt_id"],
                    "prompt_tier": row["prompt_tier"],
                    "demographic_dimension": row["demographic_dimension"],
                    "temperature": row["temperature"],
                    "top_p": row["top_p"],
                    "seed": int(row["seed"]),
                    "semantic_distance": scores["semantic_distance"],
                    "stereotype_similarity": scores["stereotype_similarity"],
                    "timestamp": utc_now(),
                }
                ckpt.append_row("embeddings", out)
                done += 1
                if done % 10 == 0:
                    ckpt.save_progress(phase="embed", embeddings_done=done)
            except Exception as e:
                ckpt.log_failure(
                    "embed", row["run_key"],
                    model_name=row["model_name"],
                    prompt_id=row["prompt_id"],
                    error_type=type(e).__name__,
                    error_message=str(e)[:500],
                )
    finally:
        scorer.unload()

    ckpt.sync_progress_counts()
    ckpt.log_session(f"Embeddings done. total={done}")
    _export(drive)
    print(f"Embeddings complete. {done} rows saved.")


def _export(drive):
    try:
        from run_export import export_bundle
        z = export_bundle(drive)
        print(f"Saved export bundle: {z}")
    except Exception as e:
        print(f"Export skipped: {e}")


if __name__ == "__main__":
    main()
