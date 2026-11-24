# Joint Effect V2 — Colab Run Instructions

## What this experiment tests

The V1 experiment used only 4 temperature conditions and a binary (male/female) outcome.
That design could not detect the interaction.

This experiment fixes both problems:
- 10 temperature values (0.1 to 2.0) → temperature as a continuous predictor
- Continuous outcome: female marker proportion in the first 180 words [0.0–1.0]
- Explicit prompts kept as a control (should show flat slope if the model follows instructions)
- 5 seeds per condition → lower variance
- 8-bit quantization → more accurate than 4-bit

If the joint effect exists, you will see:
- Implicit prompts: female_ratio changes as temperature increases (slope ≠ 0)
- Explicit prompts: female_ratio stays flat (slope ≈ 0, model follows instruction)
- The interaction term in the regression will be significant

---

## Step 1 — Upload files to Colab

Upload both files to your Colab session (or to Google Drive):
- `run_generation_v2.py`
- `analyze_joint_v2.py`

---

## Step 2 — Install dependencies

```python
!pip install transformers accelerate bitsandbytes scipy statsmodels matplotlib pandas -q
```

---

## Step 3 — Log into Hugging Face (needed for Llama)

```python
from huggingface_hub import login
login()  # paste your HF token when prompted
```

---

## Step 4 — Run generation

```python
!python run_generation_v2.py
```

This will:
- Load each model once in 8-bit
- Generate 10 temps × 5 seeds × 3 tiers × 9 roles = 1,350 stories per model
- Save every story immediately to `joint_v2/outputs/generations_v2.csv`
- Print progress with percentage
- Resume automatically if the session drops (run the same command again)

Estimated time on T4 GPU: ~90 minutes for both models.
If you only have time for one model, change MODELS in run_generation_v2.py to just Llama.

---

## Step 5 — Run analysis

```python
!python analyze_joint_v2.py
```

This will print:
- The interaction term from logistic regression (binary outcome)
- The interaction term from OLS regression (continuous female_ratio)
- Temperature slope per tier (implicit, semi, explicit)
- Role-stratified analysis (strong vs weak stereotypical prior)
- Three figures saved to `joint_v2/outputs/figures/`

---

## Step 6 — Download outputs

```python
from google.colab import files
import shutil
shutil.make_archive('joint_v2_results', 'zip', 'joint_v2/outputs')
files.download('joint_v2_results.zip')
```

---

## What the results mean

| Pattern | Meaning |
|---|---|
| Implicit slope significant, explicit flat | Joint effect confirmed |
| Both slopes non-significant | Effect still undetected — try wider temperature range or more seeds |
| Both slopes significant but same direction | Temperature has a main effect, no interaction |
| Implicit slope p < 0.05, interaction p < 0.05 | Strong evidence for the joint effect |

---

## Total compute

| Component | Count |
|---|---|
| Models | 2 (Llama 3.1 8B, Qwen 2.5 7B) |
| Temperature values | 10 |
| Seeds per condition | 5 |
| Prompt tiers | 3 (implicit, semi, explicit) |
| Roles | 9 |
| **Total stories** | **2,700** |
| Estimated time (T4) | ~90 minutes |

You can reduce to 1 model (1,350 stories, ~45 minutes) if needed.
