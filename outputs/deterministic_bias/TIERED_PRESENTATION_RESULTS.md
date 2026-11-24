# Tiered Bias Results for Presentation

## Main Message

The experiment shows that bias in modern open-source LLMs is not mainly expressed as overt discriminatory text. Instead, bias appears more strongly as **implicit and semi-explicit demographic defaulting**.

In simple terms:

> Explicit bias was very low, but implicit and semi-explicit bias remained substantial.

This matches current findings in LLM bias research: aligned models suppress direct toxic or discriminatory language, but still reproduce demographic associations through character framing, roles, and assumptions.

## Results by Bias Tier

| Bias category | What it means | Result |
|---|---|---:|
| **Explicit bias** | Overt stereotype language or direct discriminatory generalizations | **0.0%** |
| **Semi-explicit bias** | Bias when the prompt gives a neutral name or partial identity cue | **58.8%** |
| **Implicit bias** | Bias when the prompt gives only the role/scenario and no identity | **58.9%** |

## Interpretation

### Explicit Bias: 0.0%

The models did not produce direct stereotype statements in the gender subset.

This is expected for modern instruction-tuned models because they are trained to avoid overtly discriminatory language. A low explicit-bias rate does **not** mean the model is unbiased. It means the model avoids obvious, surface-level biased wording.

Use this phrasing:

> "Explicit bias was near zero, which is consistent with modern alignment. The more important finding is that bias reappeared at the implicit and semi-explicit levels."

### Semi-Explicit Bias: 58.8%

Semi-explicit prompts used neutral names or partially specified identities. Even without explicit demographic instructions, the models still made patterned demographic assignments in the stories.

This shows that partial framing is enough for the model to begin filling in demographic assumptions.

Use this phrasing:

> "When prompts used neutral names or partially specified characters, the model still showed a 58.8% bias-aligned defaulting rate."

### Implicit Bias: 58.9%

Implicit prompts gave only a role or scenario. The model had to decide who the character was.

The implicit-bias rate was **58.9%**, meaning the generated stories frequently reflected demographic role associations even when no demographic identity was specified.

Use this phrasing:

> "The strongest finding is that implicit bias remained high: when identity was not specified, the models filled in demographic assumptions in 58.9% of classifiable cases."

## Strongest Supporting Results

Some role categories showed especially strong implicit associations:

| Role type | Implicit association |
|---|---:|
| Nurse | **100%** |
| Kindergarten teacher | **100%** |
| Professional ballet dancer | **100%** |
| Social worker | **91.4%** |

These results show that the models strongly associate some roles with particular demographic patterns when the prompt does not specify identity.

## Model Comparison

| Model | Bias-aligned rate |
|---|---:|
| Mistral 7B | **69.5%** |
| Llama 3.1 8B | **54.0%** |
| Qwen 2.5 7B | **53.1%** |

Interpretation:

> "Mistral showed the highest demographic defaulting, while Llama and Qwen were lower but still above 50%."

## Hyperparameter Finding

Bias-aligned rates stayed relatively stable across sampling settings:

| Sampling condition | Bias-aligned rate |
|---|---:|
| T=0.3, top_p=1.0 | **57.5%** |
| T=1.0, top_p=0.3 | **59.2%** |
| T=1.0, top_p=0.9 | **60.9%** |
| T=1.5, top_p=1.0 | **57.7%** |

Interpretation:

> "In this experiment, model choice and prompt framing mattered more than sampling hyperparameters. Temperature and top-p changed the rate only slightly."

## Figures to Use

Use these figures from:

`outputs/deterministic_bias/figures/`

| Slide | Figure |
|---|---|
| Bias by role | `fig1_implicit_defaults_by_role.png` |
| Bias by sampling condition | `fig2_stereotype_aligned_by_condition.png` |
| Bias by model | `fig3_stereotype_aligned_by_model.png` |
| Bias by prompt tier | `fig4_gender_share_by_tier.png` |
| Explicit prompt compliance | `fig5_explicit_compliance_by_role.png` |
| Model × condition heatmap | `fig6_model_condition_heatmap.png` |

## Recommended Slide Story

### Slide 1: Research Question

How do prompt specificity and inference settings affect bias in open-source LLM story generation?

### Slide 2: Why Bias Must Be Tiered

Bias is not one number:

- Explicit bias: direct stereotype language
- Semi-explicit bias: demographic assumptions from partial cues
- Implicit bias: demographic assumptions when identity is not specified

### Slide 3: Experimental Design

3,888 generations across:

- 3 models
- 108 prompts
- 3 prompt tiers
- 4 sampling conditions
- 3 seeds

### Slide 4: Main Finding

Explicit bias was **0.0%**, but semi-explicit and implicit bias were both about **59%**.

### Slide 5: Implicit Bias by Role

Use `fig1_implicit_defaults_by_role.png`.

Main point:

> "Some roles triggered near-perfect demographic defaulting."

### Slide 6: Model Differences

Use `fig3_stereotype_aligned_by_model.png`.

Main point:

> "Mistral showed the highest bias-aligned defaulting."

### Slide 7: Hyperparameters

Use `fig2_stereotype_aligned_by_condition.png`.

Main point:

> "Sampling settings had smaller effects than prompt framing and model choice."

### Slide 8: Contribution

This project contributes:

1. A controlled 3,888-generation factorial experiment.
2. A tiered bias framework separating explicit, semi-explicit, and implicit bias.
3. Evidence that modern LLMs suppress explicit bias but retain implicit demographic associations.
4. A reproducible text-based analysis using saved generations.

## 30-Second Defense

> "The key result is that bias is not captured by looking only for explicit discriminatory statements. In my experiment, explicit bias was 0.0%, which is expected for aligned models. But when I measured semi-explicit and implicit demographic defaulting, the rates were about 59%. This shows that open-source LLMs may avoid overtly biased language while still reproducing demographic associations when generating characters. Mistral showed the highest rate, and hyperparameter changes had smaller effects than model choice and prompt framing."

## Important Note

Do not present the result as "the models are fair." The correct interpretation is:

> "The models are aligned against explicit bias, but implicit and semi-explicit bias remain substantial."
