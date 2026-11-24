# Joint Effect Supplement — Colab Instructions

## What this does

Adds more temperature and top-p settings to your existing V1 gender stories.

**After merge you get:**
- **6 temperatures** at top_p = 1.0: 0.3, 0.5, 0.7, 1.0, 1.3, 1.5
- **2 top_p values** at T = 1.0: 0.3, 0.9

V1 stories in `data/v1_gender_existing.csv` are reused. The script only generates what is missing (~970 new stories for 3 models).

---

## What to upload to Google Drive

Upload the whole folder:

```
joint_supplement_colab/
  Joint_Effect_Supplement.ipynb
  run_generation_supplement.py
  merge_and_analyze.py
  prompts_gender.csv
  data/
    v1_gender_existing.csv
```

Put it at: `My Drive/joint_supplement_colab/`

---

## Colab steps

1. Open `Joint_Effect_Supplement.ipynb` in Colab
2. **Runtime → Change runtime type → T4 GPU**
3. Run cells 1 → 6 in order

| Cell | What it does |
|------|----------------|
| 1 | Mount Drive, go to folder |
| 2 | Install packages + HuggingFace login (needed for Llama) |
| 3 | Generate missing stories (~3–4 hours for 3 models) |
| 4 | Merge with V1 + run analysis |
| 5 | Show figure inline |
| 6 | Download results zip |

---

## If you see FAILED when downloading models

Most common cause: **Llama license not accepted** or **token missing on download**.

1. Open https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
2. Log in with the **same account** as your token
3. Click **"Agree and access repository"**
4. Create a token at https://huggingface.co/settings/tokens (Write permission)
5. In Colab run **Cell 2** (login) then **Cell 3** (`test_setup.py`)
6. Only run **Cell 4** when Cell 3 prints `Pre-flight check passed`

Re-upload the updated folder from your machine — the script now uses `token=True` (required for Llama).

---

## If Colab disconnects

Re-run **Cell 3** only. Nothing is lost.

How it works:
- Every finished story is written immediately to `outputs/generations_supplement.csv`
- The file is flushed to Google Drive after each story
- On restart, the script reads that file and **skips every run_key already saved**
- Failed runs (logged in `failures_supplement.csv`) are **not** skipped — they are retried
- Check `outputs/progress_supplement.txt` to see the last completed story

Example after disconnect:
```
Already on file: 1050 run_keys
Remaining to generate: 894
```
The number goes down each time you re-run Cell 3 until it hits zero.

---

## What you download

```
outputs/
  generations_supplement.csv   — new stories only
  generations_merged_gender.csv — V1 + new combined
  annotations_supplement.csv   — gender markers scored
  figures/fig_temp_sweep_x_tier.png
```

Bring the zip back here and we update the paper with the stronger regression results.

---

## Optional: one model only

Edit `MODELS` in `run_generation_supplement.py` and keep only Llama:

```python
MODELS = [
    "meta-llama/Llama-3.1-8B-Instruct",
]
```

That cuts generation time to about 1 hour.
