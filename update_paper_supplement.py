"""Update FINAL docx with supplement experiment results only."""
from docx import Document

PATH = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-FINAL.docx"


def set_para(doc, idx, text):
    doc.paragraphs[idx].text = text


def main():
    doc = Document(PATH)

    set_para(
        doc,
        8,
        "Most fairness evaluations of large language models test models under a single fixed condition: one prompt style and default inference settings. Yet real deployments combine prompts of varying specificity with customized sampling configurations. This study examined whether the effect of inference temperature on stereotype generation in open-ended story prompts depends on prompt specificity. Three instruction-tuned open-source models were tested across three prompt tiers: implicit (role only), semi-explicit (gender-neutral name), and explicit (counter-stereotypical gender stated). The primary V1 run compared T=0.3 and T=1.5 at top_p=1.0. A supplement run added six temperature values at top_p=1.0 (0.3, 0.5, 0.7, 1.0, 1.3, 1.5) and two top_p values at T=1.0 (0.3, 0.9). Gender defaulting was measured using a deterministic pronoun-based method applied to the first 180 words of each story. The merged gender dataset comprised 1,828 stories (974 from V1 and 854 from the supplement). With six temperature points, female marker proportion declined significantly as temperature increased for implicit prompts (OLS slope b=-0.105, p=0.008) but not for semi-explicit or explicit prompts. The logistic interaction between continuous temperature and prompt tier remained non-significant (implicit vs semi-explicit interaction b=-0.39, p=0.22). Explicit counter-stereotypical prompts reduced stereotype alignment to about 16%, confirming that prompt framing remains the stronger lever. These results support a tiered evaluation approach and show that a wider temperature grid can detect tier-specific hyperparameter effects that a two-point comparison cannot.",
    )

    set_para(
        doc,
        58,
        "The final completed design comprised 3,888 planned generations: 108 prompts × 4 hyperparameter conditions × 3 seeds × 3 models. An additional 4 early pilot rows at T=0.7 were saved but excluded from all analyses to preserve a balanced factorial structure. A supplement run later filled missing points in the gender grid. It added 854 new gender stories (94% of the targeted supplement grid) at six temperatures with top_p=1.0 and two top_p values at T=1.0. Merged with 974 V1 gender stories, the analysis dataset contained 1,828 gender stories.",
    )

    set_para(
        doc,
        75,
        "All generations used do_sample=True and max_new_tokens=400. Each condition was combined with three random seeds (42, 123, 456) to separate condition effects from run-to-run variation. The supplement run used the same settings and added temperature values 0.5, 0.7, 1.0, and 1.3 at top_p=1.0, plus top_p values 0.3 and 0.9 at T=1.0, while reusing existing V1 stories for overlapping cells.",
    )

    set_para(
        doc,
        84,
        "Coverage: 957 of 972 V1 gender stories (98.5%) yielded a classifiable protagonist gender. "
        "The remaining 15 stories used gender-neutral language throughout and were treated as ambiguous. "
        "In the merged gender dataset used for joint-effect analyses (Section 4.1), 1,804 of 1,828 stories (98.7%) were classifiable.",
    )

    set_para(
        doc,
        86,
        "The primary analysis tested the joint effect of prompt specificity and inference temperature on stereotype-aligned defaulting. The V1 analysis compared T=0.3 and T=1.5 with top_p fixed at 1.0 using a binary temperature factor. The supplement analysis treated temperature as a continuous predictor across six values (0.3, 0.5, 0.7, 1.0, 1.3, 1.5) at top_p=1.0. Logistic regression was fitted with stereotype-aligned defaulting as the outcome. OLS regression used female marker proportion in the first 180 words as a continuous outcome. Per-tier temperature slopes were estimated separately for implicit, semi-explicit, and explicit prompts. A supplementary OLS model tested top_p effects at T=1.0.",
    )

    set_para(
        doc,
        91,
        "The primary research question asked whether the effect of inference temperature on demographic defaulting depended on prompt specificity. "
        "Sections 4.2 through 4.4 report the original V1 gender subset (N=972). "
        "This section and Section 4.5 use the merged gender dataset (1,828 stories: 974 V1 plus 854 supplement). "
        "For the six-point temperature sweep at top_p=1.0, 1,330 merged stories had evaluable gender classifications. "
        "Table 1 summarizes stereotype-aligned rates at T=0.3 and T=1.5. Table 1b summarizes rates at all six temperature values for implicit and semi-explicit prompts.",
    )

    set_para(
        doc,
        92,
        "Table 1. Stereotype-aligned defaulting rate (%) by prompt tier at T=0.3 and T=1.5 (top_p=1.0, merged dataset, N=1,828).",
    )

    set_para(
        doc,
        93,
        "[Figure 1: Stereotype-aligned defaulting rate (%) by prompt tier at T=0.3 and T=1.5 (top_p=1.0). Blue bars = T=0.3, red bars = T=1.5. File: figures/fig_joint_stereotype_rate.png]",
    )

    set_para(
        doc,
        94,
        "[Figure 1b: Female marker proportion by prompt tier across six temperature values at top_p=1.0. Implicit prompts show a downward slope. File: figures/fig_supplement_temp_sweep_x_tier.png]",
    )

    set_para(
        doc,
        96,
        "Logistic regression with continuous temperature and prompt tier as predictors (top_p=1.0, evaluable stories only) showed a non-significant interaction between temperature and tier. The implicit versus semi-explicit interaction was b=-0.39 (p=0.22). The main effect of temperature was b=0.33 (p=0.15). OLS regression on female marker proportion showed a significant negative main effect of temperature (b=-0.105, p=0.020). Per-tier slopes were significant for implicit prompts (b=-0.105, p=0.008, n=448) but not for semi-explicit (b=+0.016, p=0.73, n=440) or explicit prompts (b=-0.022, p=0.65, n=442). The OLS interaction between temperature and semi-explicit tier relative to implicit was b=+0.121 (p=0.060).",
    )

    set_para(
        doc,
        97,
        "Implicit prompts showed stereotype alignment of 56.2% at T=0.3 and 61.3% at T=1.5. The path across six temperatures was not strictly monotonic (peak 70.8% at T=1.3). Explicit prompts stayed near 16% at both endpoints (16.0% at T=0.3, 16.2% at T=1.5). Female marker proportion for implicit prompts fell from 81.8% at T=0.3 to 72.5% at T=1.5. Semi-explicit and explicit tiers showed smaller shifts. The six-point sweep detected a significant implicit-tier temperature slope on female marker proportion that the two-point V1 comparison could not confirm. The logistic interaction on binary stereotype alignment remained non-significant.",
    )

    set_para(
        doc,
        120,
        "The supplement run extended hyperparameter coverage beyond the original four conditions. Table 5 summarizes stereotype-aligned rates for implicit and semi-explicit prompts at six temperature values (top_p=1.0). Table 5b summarizes top_p effects at T=1.0.",
    )

    set_para(
        doc,
        122,
        "[Figure 6: Stereotype-aligned rate (%) across six temperature values at top_p=1.0, by prompt tier. File: figures/fig_supplement_temp_sweep_x_tier.png]",
    )

    set_para(
        doc,
        124,
        "At top_p=1.0, implicit stereotype-aligned rates ranged from 56.2% (T=0.3) to 70.8% (T=1.3) before falling to 61.3% at T=1.5. Semi-explicit rates stayed between 53.9% and 63.9%. Explicit rates stayed near 14-16% across all six temperatures. Collapsing tiers masked the implicit-tier slope. At T=1.0, varying top_p from 0.3 to 0.9 produced small shifts (implicit: 55.0% at top_p=0.3 vs 63.0% at top_p=0.9). The top_p by tier interaction in OLS was not significant (p=0.34).",
    )

    set_para(
        doc,
        144,
        "The central question was whether the effect of inference temperature on stereotype generation depends on prompt specificity. With six temperature points at top_p=1.0, female marker proportion declined significantly for implicit prompts (p=0.008) but not for semi-explicit or explicit prompts. The logistic interaction on binary stereotype alignment remained non-significant (p=0.22 for implicit vs semi-explicit). The wider grid therefore detected a tier-specific hyperparameter effect on one outcome measure but not on the other.",
    )

    set_para(
        doc,
        145,
        "The OLS result and the non-significant logistic interaction can coexist. Female marker proportion captures gradual shifts in pronoun usage. Stereotype alignment is a coarser binary threshold. "
        "Implicit prompts showed a steady drop in female marker share as temperature rose in the merged dataset, even when binary alignment did not show a clean monotonic pattern. "
        "In the original two-point V1 comparison, Llama 3.1 8B and Mistral 7B both increased in implicit stereotype alignment by 11.1 percentage points at high temperature, while Qwen 2.5 7B moved in the opposite direction.",
    )

    set_para(
        doc,
        146,
        "Two interpretations remain. First, temperature may shift surface-level gendered wording without changing binary stereotype alignment enough to reach significance in logistic models. Second, the implicit-tier OLS slope may reflect real tier-specific sensitivity that logistic models with a single alignment threshold underpower. The supplement reduced the pure power problem of the two-point design but did not fully resolve the interaction question.",
    )

    set_para(
        doc,
        158,
        "Scale and hyperparameter coverage. The original V1 design used four hyperparameter conditions. The supplement added six temperature values at top_p=1.0 and two top_p values at T=1.0 for the gender dimension only. "
        "That supplement grid was 94% complete (854 of 910 targeted new gender stories). Joint-effect results in Sections 4.1 and 4.5 use the merged gender dataset. "
        "Tier, role, and model summaries in Sections 4.2-4.4 remain on the V1 gender subset unless noted. "
        "Non-monotonic implicit alignment rates at intermediate temperatures suggest that binary outcomes may need still wider sweeps.",
    )

    set_para(
        doc,
        165,
        "This paper asked whether the relationship between inference temperature and stereotype generation changes with prompt specificity. The supplement run with six temperature points showed a significant negative slope of female marker proportion for implicit prompts (p=0.008). The logistic interaction on binary stereotype alignment remained non-significant. Explicit prompts stayed near 16% alignment across conditions. Prompt framing remains the strongest lever. Temperature effects appear tier-specific and outcome-specific.",
    )

    set_para(
        doc,
        168,
        "Three directions remain for future work. First, complete the remaining 6% of the supplement grid and test nonlinear temperature terms. Second, extend the tiered framework to the race, age, and occupation dimensions collected in V1. Third, compare model families on why Mistral defaulting rates exceed Llama and Qwen in the merged dataset.",
    )

    set_para(
        doc,
        100,
        "Table 2. Stereotype-aligned rates by bias tier (gender dimension, V1 subset, 972 stories).",
    )

    set_para(
        doc,
        101,
        "[Figure 5: Tiered bias summary: bar chart of stereotype-aligned rate (%) for explicit, semi-explicit, and implicit prompt conditions. File: figures/fig5_tiered_bias_summary.png]",
    )

    set_para(
        doc,
        104,
        "The near-identical rates for semi-explicit (58.8%) and implicit (58.9%) showed that removing the demographic cue entirely did not reduce defaulting compared with adding a neutral name. Explicit counter-stereotypical prompts reduced stereotype alignment to 16.0% in the V1 subset.",
    )

    set_para(
        doc,
        108,
        "[Figure 3: Protagonist gender distribution by role for implicit prompts. File: figures/fig3_role_defaults.png]",
    )

    set_para(
        doc,
        112,
        "Stereotype-aligned defaulting rates differed substantially across the three models. Mistral 7B showed the highest defaulting rate, 15 to 16 percentage points above Llama 3.1 8B and Qwen 2.5 7B on implicit and semi-explicit prompts in the V1 subset.",
    )

    set_para(
        doc,
        114,
        "[Figure 4: Stereotype-aligned defaulting rate by model (bar chart). File: figures/fig4_model_comparison.png]",
    )

    set_para(
        doc,
        166,
        "What the experiment did reveal alongside the joint-effect analyses was important. Three models that passed an explicit-bias test at 16% stereotype alignment (near-chance for a binary outcome against a counter-stereotypical prompt) all produced implicit and semi-explicit defaulting near 57-61% in the V1 subset. The role of nurse was assigned a female protagonist in over 90% of implicit stories. The role of surgeon was assigned a female protagonist in roughly 80% of cases despite being a male-stereotyped role, showing that the female-defaulting tendency extended beyond female-stereotyped occupations. These associations persisted across all three models and all four V1 hyperparameter conditions.",
    )

    set_para(
        doc,
        167,
        "The most important finding is that instruction-tuned models suppressed explicit discriminatory language while retaining substantial demographic associations in character framing. A fairness audit that only scans for explicit bias would report near-zero rates for all three models and conclude they are unbiased. The tiered framework used in this study showed that this conclusion was wrong. Within the four V1 inference conditions tested, adjusting temperature or top-p did not substantially change the 59% implicit defaulting rate. The supplement run additionally showed that female marker proportion for implicit prompts shifts across a wider temperature range.",
    )

    set_para(
        doc,
        117,
        "[Figure 2: Stereotype-aligned defaulting rate by tier and temperature per model (Llama, Mistral, Qwen). File: figures/fig_joint_per_model.png]",
    )

    doc.save(PATH)
    print(f"Updated {PATH}")


if __name__ == "__main__":
    main()
