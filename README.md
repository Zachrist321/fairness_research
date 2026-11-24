# Fairness Research — Completed Experiment

**The Joint Effect of Prompt Specificity and Inference Hyperparameters on Stereotype Generation in Open-Source LLMs**

## Start here (for graders)

| File | What it is |
|------|------------|
| **`SUBMISSION_FOR_TEACHERS.md`** | Full project write-up: abstract, methods, results, discussion |
| **`outputs/RESULTS_SUMMARY.json`** | Main results in one file |
| **`outputs/figures/`** | All presentation figures |
| **`outputs/stats/tiered_*.csv`** | Results tables by tier, model, condition |
| **`experiment_config.json`** | Final scaled design (3,888 generations) |
| **`prompts/prompts_v1.csv`** | 108 prompts (explicit / semi-explicit / implicit) |

## Final design

Scaled factorial experiment completed on Google Colab:

- **3,888** planned generations (108 prompts × 4 conditions × 3 seeds × 3 models)
- **3 models:** Llama 3.1 8B, Mistral 7B, Qwen 2.5 7B
- **3 prompt tiers:** explicit, semi-explicit, implicit
- **4 sampling conditions:** T=0.3, T=1.5, top_p=0.3, top_p=0.9

## Main results

**Primary — joint effect (prompt tier × hyperparameters):**

| Test | Result |
|------|--------|
| Interaction (χ², df=7) | **p = 0.889** (not significant) |
| Within-tier spread | implicit 8.0 pp, semi 9.7 pp |

See `outputs/deterministic_bias/JOINT_EFFECT.txt` and `fig7_joint_effect_interaction.png`.

**Secondary — tiered bias rates:**

| Bias tier | Result |
|-----------|--------:|
| Explicit bias | 0.0% |
| Semi-explicit bias | 58.8% |
| Implicit bias | 58.9% |

Mistral showed the highest bias-aligned rate (69.5%), followed by Llama (54.0%) and Qwen (53.1%).

## Repository layout

```
research_experiment/
├── SUBMISSION_FOR_TEACHERS.md     ← read this first
├── experiment_config.json         ← design specification
├── prompts/prompts_v1.csv         ← all prompts
├── checkpoints/
│   ├── generations.csv            ← 3,892 generated stories
│   ├── scores_primary.csv         ← supplementary judge scores
│   ├── scores_secondary.csv       ← secondary judge subsample
│   └── embeddings.csv             ← semantic distance scores
├── outputs/
│   ├── RESULTS_SUMMARY.json       ← headline results
│   ├── figures/                   ← fig1–fig6 (presentation plots)
│   └── stats/
│       ├── tiered_bias_summary.csv
│       ├── tiered_summary_by_tier.csv
│       ├── tiered_summary_by_model.csv
│       └── mixed_effects.txt      ← supplementary regression
├── colab/fairness_experiment.ipynb
├── run_generation.py
├── run_judge.py
├── run_embed.py
├── run_analyze.py
└── analyze_deterministic.py
```

## How the experiment was run

1. **Generation** (`run_generation.py`) — 3,892 stories saved to `checkpoints/generations.csv`
2. **Judging** (`run_judge.py`) — supplementary LLM-as-judge scores
3. **Embeddings** (`run_embed.py`) — semantic distance to stereotype references
4. **Analysis** (`run_analyze.py` + `analyze_deterministic.py`) — tiered bias results and figures

All phases checkpoint to Google Drive; resume-safe via `run_key`.

## Reproducing analysis

```bash
cd research_experiment
python analyze_deterministic.py
python run_analyze.py
```

Outputs are written to `outputs/`.
# fairness_research
