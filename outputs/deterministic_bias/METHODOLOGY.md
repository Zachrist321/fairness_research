# Methodology

## Research question

How do **prompt specificity** (implicit, semi-specific, explicit) and **inference hyperparameters** (temperature, top_p) jointly affect demographic defaulting in open-source large language models?

## Models

Three instruction-tuned open-source generators were used:

| Model | Hugging Face ID |
|-------|-----------------|
| Llama 3.1 8B | `meta-llama/Llama-3.1-8B-Instruct` |
| Mistral 7B | `mistralai/Mistral-7B-Instruct-v0.3` |
| Qwen 2.5 7B | `Qwen/Qwen2.5-7B-Instruct` |

All models were loaded with 4-bit quantization on Colab GPU for memory efficiency.

## Experimental design

A **factorial design** was used:

| Factor | Levels |
|--------|--------|
| Prompts | 108 (4 demographic dimensions × 27 scenarios) |
| Prompt specificity | 3 tiers: implicit, semi, explicit |
| Sampling conditions | 4: T=0.3, T=1.5, top_p=0.3, top_p=0.9 |
| Random seeds | 3 (42, 123, 456) |
| Models | 3 |

**Total generations:** 108 × 4 × 3 × 3 = **3,888**

### Prompt specificity tiers

Each scenario has three matched prompts differing only in how much demographic information is given:

- **Implicit:** role only (e.g. *"Write a short story about a surgeon…"*)
- **Semi:** neutral name (e.g. *"Write a short story about Dr. Morgan…"*)
- **Explicit:** stated gender (e.g. *"Write a short story about a female surgeon…"*)

For the gender dimension, nine occupation scenarios were used (surgeon, software engineer, kindergarten teacher, CEO, nurse, ballet dancer, mechanical engineer, social worker, military officer), each with a commonly assumed gender stereotype defined **before** data collection.

### Sampling hyperparameters

| Condition | Temperature | top_p | Rationale |
|-----------|-------------|-------|-----------|
| Low temperature | 0.3 | 1.0 | Conservative, predictable output |
| High temperature | 1.5 | 1.0 | Creative, high-variance output |
| Low top_p | 1.0 | 0.3 | Restricted vocabulary |
| High top_p | 1.0 | 0.9 | Broad vocabulary |

## Generation procedure

1. Each prompt was formatted as a chat message and passed to the model via `apply_chat_template`.
2. Generation settings: `max_new_tokens=400`, `do_sample=True`, with the condition's temperature and top_p.
3. `torch.manual_seed(seed)` was set before each generation for reproducibility.
4. Each output was saved immediately to `checkpoints/generations.csv` with a unique `run_key` for resume safety.

## Bias measurement: tiered deterministic framework

Following the literature distinction between **explicit** and **implicit** bias in LLMs, outputs were scored using reproducible, rule-based metrics that do not depend on another language model.

### Tier 1 — Explicit stereotype language

**Definition:** Overt generalizations or discriminatory statements in the generated text (e.g. *"women are too emotional to…"*, *"men's work"*).

**Method:** Regex scan of each story for a fixed list of explicit stereotype phrase patterns.

**Interpretation:** Low rates are expected in safety-tuned models and align with published explicit-bias findings (typically 1–3% in aligned models).

### Tier 2 — Implicit occupation–gender association

**Definition:** Whether the protagonist's gender in the generated story matches the commonly assumed gender stereotype for that occupation, when the prompt does not specify gender.

**Method:**

1. Remove the story title line (to avoid spurious gender markers).
2. Scan the first ~180 words for gender-coded markers (pronouns, gendered nouns/titles).
3. Assign protagonist gender from the **earliest ordered markers** (not whole-story totals, which can be inflated by side characters).
4. Compare inferred gender to the pre-defined stereotype for that role.

**Metrics reported:**

- **Stereotype-aligned rate:** share of stories where protagonist gender matches the role stereotype.
- **Female-coded / male-coded rate:** marginal gender assignment per role or condition.
- **Explicit compliance rate:** when the prompt requests a counter-stereotypical gender, whether the model honored it.

**Interpretation:** High rates on female-stereotyped roles (nurse, teacher) indicate strong implicit demographic defaulting. Low male-assignment on male-stereotyped roles (surgeon, engineer) indicates an additional **female-protagonist default** independent of role.

### Tier 3 — Semantic stereotype proximity (embeddings)

**Definition:** Cosine similarity between the generated story embedding and a fixed set of stereotype reference sentences (StereoSet-inspired, per demographic dimension).

**Model:** `sentence-transformers/all-mpnet-base-v2`

**Metric:** `stereotype_similarity` (higher = closer to stereotypical reference language).

## Analysis scope for gender results

The tiered deterministic analysis in `outputs/deterministic_bias/` focuses on the **gender dimension** (972 stories), where occupation–gender association can be measured objectively. Age, race, and occupation dimensions are included in the full generation set and can be analyzed with the same pipeline.

## Statistical analysis

- Descriptive rates (proportions) are reported per tier, model, and sampling condition.
- Mixed-effects models were fit with `prompt_id` as a random intercept where sample size permitted.
- All analysis code is in `analyze_deterministic.py` and is fully reproducible: identical inputs produce identical outputs with no GPU required.

## Limitations

1. **Binary gender coding only** — the metric uses English pronoun/title patterns and does not capture nonbinary representation.
2. **Protagonist inference is approximate** — early-marker heuristics can misclassify stories with multiple gendered characters.
3. **Story-generation task** — models may produce more neutral fiction than they would in open-ended chat; explicit bias rates may be underestimated.
4. **Reproducibility** — model weights were not pinned to a specific Hugging Face revision; 4-bit quantization introduces minor GPU-dependent variance.
5. **Scope** — gender-dimension results are reported in detail; other dimensions require separate analysis.

## Reproducibility

To regenerate all results and figures on Colab or locally:

```bash
cd research_experiment
MPLCONFIGDIR=$PWD/.cache/mpl XDG_CACHE_HOME=$PWD/.cache python3 analyze_deterministic.py
```

Outputs are written to `outputs/deterministic_bias/`.
