# Presentation Results Summary

Use these numbers in your slides. They come directly from `analyze_deterministic.py` on your completed experiment (3,888 generations; gender-dimension analysis = 972 stories).

---

## One-sentence finding

> Open-source LLMs show **very low explicit stereotype language** but **high implicit occupation–gender defaulting**, especially for female-stereotyped roles — consistent with the literature's explicit vs. implicit bias distinction.

---

## Results mapped to bias tiers (literature framework)

| Bias tier | What we measured | Your result | Literature range |
|-----------|------------------|-------------|------------------|
| **Explicit** | Overt stereotype phrases in generated text | **0.0%** (0 / 972) | ~1–3% in aligned models |
| **Implicit (occupation–gender)** | Protagonist gender matches role stereotype (implicit prompts) | **58.9%** overall; **97.2%** for female-stereotyped roles | Implicit bias often much higher than explicit; domain-specific peaks >45% reported |
| **Counter-stereotype compliance** | Model honors explicit counter-stereotypical gender request | **97.8%** compliance (**2.2%** failure) | Evaluative / instruction-following dimension |

**Key asymmetry:** Female-stereotyped roles → female protagonist **97.2%** of the time. Male-stereotyped roles → male protagonist only **27.2%** — models default to **female protagonists** even for surgeon, CEO, and engineer prompts.

---

## Headline numbers for slides

| Stat | Value |
|------|-------|
| Total generations | 3,888 |
| Gender stories analyzed | 972 |
| Classifiable protagonist gender | 98.5% |
| Explicit stereotype language | **0.0%** |
| Implicit stereotype alignment (overall) | **58.9%** |
| Female-role stereotype alignment | **97.2%** |
| Protagonists female-coded (implicit + semi) | **76%** |
| Mistral stereotype-aligned rate | **69.5%** (highest) |
| Llama stereotype-aligned rate | **54.0%** |
| Qwen stereotype-aligned rate | **53.1%** (lowest) |

---

## Slide-by-slide guide

### Slide 1 — Title
*The Joint Effect of Prompt Specificity and Inference Hyperparameters on Demographic Defaulting in Open-Source LLMs*

### Slide 2 — Problem
- LLMs are deployed widely; fairness depends on prompts and settings, not just training.
- Bias appears at multiple levels: explicit statements vs. implicit demographic defaults.
- Prior work often measures one or the other; this study measures both in a controlled factorial design.

### Slide 3 — Design
- 3,888 generations: 3 models × 108 prompts × 4 conditions × 3 seeds
- 3 prompt tiers: implicit / semi / explicit
- 4 hyperparameter conditions: T=0.3, T=1.5, top_p=0.3, top_p=0.9

### Slide 4 — Method (use `METHODOLOGY.md`)
- **Generation:** HF models on Colab, chat template, seeded sampling
- **Measurement:** Tiered deterministic analysis (no LLM judge for primary results)
  - Tier 1: explicit phrase detection
  - Tier 2: protagonist gender inference from early pronouns/terms
  - Tier 3: embedding proximity to stereotype references

### Slide 5 — Explicit bias (Tier 1)
- **0.0%** of gender-dimension stories contained overt stereotype language
- Consistent with safety-aligned models suppressing explicit discrimination
- Figure: none needed; single stat is enough

### Slide 6 — Implicit bias (Tier 2) — MAIN RESULT
- **Figure:** `fig1_implicit_defaults_by_role.png`
- Nurse, kindergarten teacher, ballet dancer: **100%** female-coded protagonists
- Surgeon, mechanical engineer: **~81%** female-coded despite male-stereotyped roles
- Overall implicit alignment: **58.9%**

### Slide 7 — Model comparison
- **Figure:** `fig3_stereotype_aligned_by_model.png`
- Mistral **69.5%** > Llama **54.0%** ≈ Qwen **53.1%**
- All three show strong female-protagonist defaulting (Llama **88%** female-coded)

### Slide 8 — Prompt specificity
- **Figure:** `fig4_gender_share_by_tier.png`
- Implicit vs semi: similar stereotype alignment (~59%)
- Explicit counter-stereotypical requests: **97.8%** honored
- Weakest compliance: male social worker (**77.8%**), male nurse (**97.1%**)
- **Figure:** `fig5_explicit_compliance_by_role.png`

### Slide 9 — Hyperparameters
- **Figure:** `fig2_stereotype_aligned_by_condition.png`
- Stereotype alignment stable across conditions (**57–61%**)
- Temperature/top_p had **little effect** on gender defaulting in this task
- Honest framing: hyperparameters matter less than role and model choice here

### Slide 10 — Model × condition
- **Figure:** `fig6_model_condition_heatmap.png`
- Mistral consistently highest across all four conditions

### Slide 11 — Contribution
1. Factorial experiment at scale (3,888) across three open-source models
2. Tiered bias measurement separating explicit (near-zero) from implicit (substantial)
3. Evidence that implicit bias manifests as **occupation–gender defaulting**, not overt language
4. Actionable: prompt explicitness can override defaults (97.8% compliance)

### Slide 12 — Limitations
- Binary gender coding; English pronouns only
- Story-generation task may underestimate chat-style bias
- Gender dimension analyzed in detail; age/race/occupation dimensions pending
- Model revisions not pinned

---

## 30-second verbal summary

> "I ran 3,888 controlled generations across Llama, Mistral, and Qwen, varying prompt specificity and sampling settings. Using a reproducible tiered framework, explicit stereotype language was essentially absent — zero percent. But implicit occupation–gender defaulting was substantial: female-stereotyped roles produced female protagonists 97% of the time, and even male-stereotyped roles like surgeon and engineer defaulted female over 80% of the time. Mistral showed the highest stereotype alignment at 70%. Explicit counter-stereotypical prompts were mostly honored. The main takeaway is that bias in these models appears as demographic defaulting in generated narratives, not as overt discriminatory statements."

---

## Files to attach / show supervisor

| File | Purpose |
|------|---------|
| `METHODOLOGY.md` | Methods section |
| `RESULTS.md` | Full results with tables |
| `figures/fig1` – `fig6` | All plots |
| `gender_default_annotations.csv` | Per-story evidence (auditable) |
| `analyze_deterministic.py` | Reproducible analysis script |
