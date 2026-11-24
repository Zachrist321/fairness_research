"""
Joint Effect Supplement — Generation
=====================================
Fills missing gender stories for a richer temperature / top-p grid.

CHECKPOINT STRATEGY (Colab):
  - Writes to /content/supplement_ckpt/ first (fast, reliable local disk)
  - Copies to Drive outputs/ after every story
  - On startup, merges Drive + local (keeps all valid stories)
  - Progress counter = valid rows on disk only

Usage (Colab):
  !python run_generation_supplement.py
"""

from __future__ import annotations

import csv
import os
import shutil
import time
from pathlib import Path

PACKAGE_VERSION = "4"

# ── Grid ─────────────────────────────────────────────────────────────────────
TEMP_SWEEP = [0.3, 0.5, 0.7, 1.0, 1.3, 1.5]
TOP_P_SWEEP = [0.3, 0.9]
TOP_P_FIXED = 1.0
SEEDS = [42, 123, 456]
MAX_NEW_TOKENS = 400
DO_SAMPLE = True
MIN_WORDS = 20

MODELS = [
    "meta-llama/Llama-3.1-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "Qwen/Qwen2.5-7B-Instruct",
]

ROOT = Path(__file__).resolve().parent
PROMPTS_CSV = ROOT / "prompts_gender.csv"
V1_CSV = ROOT / "data" / "v1_gender_existing.csv"
OUT_DIR = ROOT / "outputs"
DRIVE_CSV = OUT_DIR / "generations_supplement.csv"
LOCAL_DIR = Path("/content/supplement_ckpt")
LOCAL_CSV = LOCAL_DIR / "generations_supplement.csv"
FAIL_CSV = OUT_DIR / "failures_supplement.csv"
PROGRESS_TXT = OUT_DIR / "progress_supplement.txt"

FIELDNAMES = [
    "run_key", "model_name", "prompt_id", "prompt_set_id", "prompt_tier",
    "demographic_dimension", "prompt_text", "temperature", "top_p", "seed",
    "generated_text", "word_count", "refusal_flag", "truncated_flag",
]
FAIL_FIELDS = ["run_key", "model_name", "error_type", "error_message"]


def make_run_key(model: str, prompt_id: str, temperature: float, top_p: float, seed: int) -> str:
    t = round(float(temperature), 6)
    p = round(float(top_p), 6)
    return f"{model}|{prompt_id}|{t}|{p}|{int(seed)}"


def build_conditions() -> list[tuple[float, float]]:
    pairs = {(t, TOP_P_FIXED) for t in TEMP_SWEEP}
    pairs.update((1.0, p) for p in TOP_P_SWEEP)
    return sorted(pairs)


def load_prompts():
    import pandas as pd
    return pd.read_csv(PROMPTS_CSV).to_dict("records")


def is_valid_story(text: str) -> bool:
    t = str(text or "").strip()
    if not t or t.lower() == "nan":
        return False
    return len(t.split()) >= MIN_WORDS


def _read_checkpoint_rows(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    import pandas as pd
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    rows = []
    for _, row in df.iterrows():
        d = {k: row.get(k, "") for k in FIELDNAMES}
        if str(d.get("run_key", "")).strip() and is_valid_story(d.get("generated_text", "")):
            rows.append(d)
    return rows


def merge_checkpoint_rows(*sources: list[dict]) -> list[dict]:
    """One row per run_key; later source wins (local over drive on tie)."""
    by_key: dict[str, dict] = {}
    for rows in sources:
        for row in rows:
            by_key[str(row["run_key"]).strip()] = row
    return [by_key[k] for k in sorted(by_key)]


def write_checkpoint_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDNAMES})
        f.flush()
        os.fsync(f.fileno())


def _colab_local_available() -> bool:
    return Path("/content").is_dir() and os.access("/content", os.W_OK)


def bootstrap_checkpoints() -> int:
    """Merge Drive + local checkpoints; write both copies. Returns valid supplement count."""
    drive_rows = _read_checkpoint_rows(DRIVE_CSV)
    local_rows = _read_checkpoint_rows(LOCAL_CSV) if _colab_local_available() else []
    merged = merge_checkpoint_rows(drive_rows, local_rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if merged:
        write_checkpoint_csv(DRIVE_CSV, merged)
        if _colab_local_available():
            write_checkpoint_csv(LOCAL_CSV, merged)
    return len(merged)


def active_checkpoint_path() -> Path:
    if _colab_local_available():
        LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        return LOCAL_CSV
    return DRIVE_CSV


def sync_to_drive(rows: list[dict]) -> None:
    """Write full checkpoint to Drive and verify row count."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_checkpoint_csv(DRIVE_CSV, rows)
    drive_n = len(_read_checkpoint_rows(DRIVE_CSV))
    if drive_n != len(rows):
        raise RuntimeError(
            f"DRIVE SAVE FAILED: wrote {len(rows)} stories but Drive file has {drive_n}. "
            "Run Cell 4b to download backup from /content before disconnecting."
        )


def count_valid_supplement() -> int:
    merged = merge_checkpoint_rows(
        _read_checkpoint_rows(DRIVE_CSV),
        _read_checkpoint_rows(LOCAL_CSV) if _colab_local_available() else [],
    )
    return len(merged)


def load_completed_keys() -> tuple[set[str], int, int]:
    keys: set[str] = set()
    v1_count = 0
    supp_keys: set[str] = set()

    if V1_CSV.exists():
        import pandas as pd
        df = pd.read_csv(V1_CSV, encoding="utf-8-sig", low_memory=False)
        for _, row in df.iterrows():
            rk = str(row.get("run_key", "")).strip()
            if rk:
                keys.add(rk)
                v1_count += 1

    merged = merge_checkpoint_rows(
        _read_checkpoint_rows(DRIVE_CSV),
        _read_checkpoint_rows(LOCAL_CSV) if _colab_local_available() else [],
    )
    for row in merged:
        rk = str(row["run_key"]).strip()
        keys.add(rk)
        supp_keys.add(rk)

    return keys, v1_count, len(supp_keys)


def append_story_row(row: dict) -> int:
    """Add one story; rewrite full CSV to local + Drive; verify both."""
    existing = merge_checkpoint_rows(
        _read_checkpoint_rows(DRIVE_CSV),
        _read_checkpoint_rows(LOCAL_CSV) if _colab_local_available() else [],
    )
    rk = str(row["run_key"]).strip()
    if any(str(r["run_key"]).strip() == rk for r in existing):
        return len(existing)

    merged = existing + [{k: row.get(k, "") for k in FIELDNAMES}]
    before = len(existing)
    if len(merged) != before + 1:
        raise RuntimeError("checkpoint merge failed")

    if _colab_local_available():
        write_checkpoint_csv(LOCAL_CSV, merged)
        local_n = len(_read_checkpoint_rows(LOCAL_CSV))
        if local_n != len(merged):
            raise RuntimeError(f"local save failed: {local_n} != {len(merged)}")

    sync_to_drive(merged)
    return len(merged)


def save_progress(done: int, total: int, run_key: str) -> None:
    PROGRESS_TXT.write_text(
        f"package_version={PACKAGE_VERSION}\n"
        f"last_completed_run_key={run_key}\n"
        f"completed={done}/{total}\n"
        f"updated={time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n",
        encoding="utf-8",
    )
    if DRIVE_CSV.exists() and LOCAL_CSV.exists() and LOCAL_CSV != DRIVE_CSV:
        try:
            shutil.copy2(PROGRESS_TXT, OUT_DIR / ".progress_synced")
        except OSError:
            pass


def sync_progress_from_checkpoint(total: int) -> int:
    completed, _, _ = load_completed_keys()
    done = len(completed)
    merged = merge_checkpoint_rows(
        _read_checkpoint_rows(DRIVE_CSV),
        _read_checkpoint_rows(LOCAL_CSV) if _colab_local_available() else [],
    )
    last_key = str(merged[-1]["run_key"]).strip() if merged else ""
    if last_key:
        save_progress(done, total, last_key)
    return done


def is_refusal(text: str) -> bool:
    phrases = [
        "i cannot", "i'm unable", "i can't", "i am unable",
        "inappropriate", "i won't", "i will not", "i apologize",
        "as an ai", "i don't think it's appropriate",
    ]
    t = text.lower().strip()
    return len(t) < 20 or any(t.startswith(p) or p in t[:120] for p in phrases)


def generate(model, tokenizer, prompt_text, temperature, top_p, seed, device):
    import torch

    torch.manual_seed(seed)
    if device == "cuda":
        torch.cuda.manual_seed_all(seed)

    messages = [{"role": "user", "content": prompt_text}]
    if hasattr(tokenizer, "apply_chat_template"):
        input_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
        )
    else:
        input_text = prompt_text

    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]
    pad_id = tokenizer.eos_token_id or tokenizer.pad_token_id or 0

    with torch.no_grad():
        output = model.generate(
            inputs["input_ids"],
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=DO_SAMPLE,
            temperature=max(float(temperature), 0.01),
            top_p=top_p,
            pad_token_id=pad_id,
        )

    new_tokens = output[0][input_len:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def _hf_token():
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        return token
    try:
        from huggingface_hub import get_token
        return get_token()
    except ImportError:
        from huggingface_hub import HfFolder
        return HfFolder.get_token()


def load_model_and_tokenizer(model_id: str, quant_config):
    import gc
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    token = _hf_token()
    if not token:
        raise RuntimeError(
            "No HuggingFace token. Run login() in the notebook cell above first."
        )

    print(f"  Downloading tokenizer for {model_id} ...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def _load(quant):
        load_kwargs: dict = {"token": token, "device_map": "auto"}
        if quant is not None:
            load_kwargs["quantization_config"] = quant
        else:
            load_kwargs["torch_dtype"] = (
                torch.float16 if torch.cuda.is_available() else torch.float32
            )
        print(f"  Downloading model weights ({'4-bit' if quant else 'float16'}) ...")
        model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)
        model.eval()
        return model

    try:
        model = _load(quant_config)
    except Exception as e:
        if quant_config is None:
            raise
        print(f"  4-bit load failed: {e}")
        print("  Retrying in float16 ...")
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        model = _load(None)

    return model, tokenizer


def preflight_check():
    import torch

    print(f"=== PRE-FLIGHT CHECK (package v{PACKAGE_VERSION}) ===")
    if not torch.cuda.is_available():
        raise RuntimeError(
            "No GPU. Runtime → Change runtime type → T4 GPU."
        )
    print(f"GPU: {torch.cuda.get_device_name(0)}")

    try:
        from huggingface_hub import get_token, whoami
        token = get_token()
    except ImportError:
        from huggingface_hub import HfFolder, whoami
        token = HfFolder.get_token()

    token = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        raise RuntimeError("No HuggingFace token. Run login() first.")
    user = whoami()
    print(f"HuggingFace: {user.get('name', user)}")

    from transformers import AutoTokenizer
    AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", token=token)
    print("Llama access OK.\n")


def build_run_list():
    prompts = load_prompts()
    completed, v1_n, supp_n = load_completed_keys()
    runs = []
    for model in MODELS:
        for prompt in prompts:
            for temp, top_p in build_conditions():
                for seed in SEEDS:
                    key = make_run_key(model, prompt["prompt_id"], temp, top_p, seed)
                    if key in completed:
                        continue
                    runs.append({
                        "run_key": key,
                        "model_name": model,
                        "prompt_id": prompt["prompt_id"],
                        "prompt_set_id": prompt["prompt_set_id"],
                        "prompt_tier": prompt["prompt_tier"],
                        "demographic_dimension": prompt["demographic_dimension"],
                        "prompt_text": prompt["prompt_text"],
                        "temperature": temp,
                        "top_p": top_p,
                        "seed": seed,
                    })
    return runs, completed, v1_n, supp_n


def main():
    import torch
    from transformers import BitsAndBytesConfig

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    preflight_check()

    merged_n = bootstrap_checkpoints()
    print(f"Script folder: {ROOT}")
    print(f"Package version: {PACKAGE_VERSION}")
    print(f"Local checkpoint:  {LOCAL_CSV}")
    print(f"Drive checkpoint: {DRIVE_CSV}")
    print(f"Merged valid supplement stories: {merged_n}")
    print()

    runs, completed, v1_n, supp_n = build_run_list()
    total_target = len(load_prompts()) * len(build_conditions()) * len(SEEDS) * len(MODELS)
    actual_done = sync_progress_from_checkpoint(total_target)

    print(f"Target grid: {total_target}")
    print(f"  V1 skip:         {v1_n}")
    print(f"  Supplement skip: {supp_n}")
    print(f"  Total valid:     {actual_done}")
    print(f"  Remaining:       {len(runs)}")
    print(f"  Conditions: {build_conditions()}")
    print()

    if not runs:
        print("Nothing to generate. Run merge_and_analyze.py next.")
        return

    print("Each story: save local → copy Drive → verify count")
    print()

    fail_header = not FAIL_CSV.exists()
    fail_file = open(FAIL_CSV, "a", newline="", encoding="utf-8")
    fail_writer = csv.DictWriter(fail_file, fieldnames=FAIL_FIELDS)
    if fail_header:
        fail_writer.writeheader()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    quant_config = None
    if device == "cuda":
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

    current_model = None
    model, tokenizer = None, None

    try:
        for run in runs:
            if run["model_name"] != current_model:
                print(f"\nLoading {run['model_name']} (4-bit)...")
                if model is not None:
                    del model
                if tokenizer is not None:
                    del tokenizer
                if device == "cuda":
                    torch.cuda.empty_cache()
                model, tokenizer = load_model_and_tokenizer(run["model_name"], quant_config)
                current_model = run["model_name"]
                print("Loaded.")

            try:
                t0 = time.time()
                text = generate(
                    model, tokenizer,
                    run["prompt_text"],
                    run["temperature"],
                    run["top_p"],
                    run["seed"],
                    device,
                )
                elapsed = time.time() - t0
                if not is_valid_story(text):
                    raise RuntimeError(
                        f"empty or too-short ({len(text.split())} words)"
                    )
                row = {
                    **run,
                    "generated_text": text,
                    "word_count": len(text.split()),
                    "refusal_flag": 1 if is_refusal(text) else 0,
                    "truncated_flag": 0,
                }
                supp_n = append_story_row(row)
                done = 974 + supp_n  # v1 + supplement on disk
                if done != sync_progress_from_checkpoint(total_target):
                    raise RuntimeError("progress count mismatch after save")
                pct = done / total_target * 100
                drive_bytes = DRIVE_CSV.stat().st_size if DRIVE_CSV.exists() else 0
                print(
                    f"[{done}/{total_target} {pct:.0f}%] "
                    f"{run['model_name'].split('/')[-1]} "
                    f"{run['prompt_id']} T={run['temperature']} top_p={run['top_p']} "
                    f"seed={run['seed']} words={row['word_count']} ({elapsed:.1f}s) "
                    f"saved={supp_n} drive={drive_bytes:,}b"
                )
            except Exception as e:
                fail_writer.writerow({
                    "run_key": run["run_key"],
                    "model_name": run["model_name"],
                    "error_type": type(e).__name__,
                    "error_message": str(e)[:200],
                })
                fail_file.flush()
                os.fsync(fail_file.fileno())
                print(f"  FAILED (will retry): {e}")

    finally:
        fail_file.close()
        bootstrap_checkpoints()
        supp_n = count_valid_supplement()
        print(f"\nDone. Supplement stories on disk: {supp_n}")
        print(f"  Local: {LOCAL_CSV} ({LOCAL_CSV.stat().st_size if LOCAL_CSV.exists() else 0:,} bytes)")
        print(f"  Drive: {DRIVE_CSV} ({DRIVE_CSV.stat().st_size if DRIVE_CSV.exists() else 0:,} bytes)")
        print("Re-run this script after disconnect to resume.")


if __name__ == "__main__":
    main()
