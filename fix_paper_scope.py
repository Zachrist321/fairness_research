"""Revert over-broad paper edits; keep supplement changes only where appropriate."""
from docx import Document

PATH = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-FINAL.docx"


def set_para(doc, idx, text):
    doc.paragraphs[idx].text = text


def main():
    doc = Document(PATH)

    # 3.6: V1 coverage stays for tier-rate definitions; merged noted for joint-effect only
    set_para(
        doc,
        84,
        "Coverage: 957 of 972 V1 gender stories (98.5%) yielded a classifiable protagonist gender. "
        "The remaining 15 stories used gender-neutral language throughout and were treated as ambiguous. "
        "In the merged gender dataset used for joint-effect analyses (Section 4.1), 1,804 of 1,828 stories (98.7%) were classifiable.",
    )

    # 4.2: restore V1 N and rates (not re-run on merged for this section)
    set_para(
        doc,
        100,
        "Table 2. Stereotype-aligned rates by bias tier (gender dimension, V1 subset, 972 stories).",
    )

    set_para(
        doc,
        104,
        "The near-identical rates for semi-explicit (58.8%) and implicit (58.9%) showed that removing the demographic cue entirely did not reduce defaulting compared with adding a neutral name. Explicit counter-stereotypical prompts reduced stereotype alignment to 16.0% in the V1 subset.",
    )

    # 4.4: restore V1 model comparison wording
    set_para(
        doc,
        112,
        "Stereotype-aligned defaulting rates differed substantially across the three models. Mistral 7B showed the highest defaulting rate, 15 to 16 percentage points above Llama 3.1 8B and Qwen 2.5 7B on implicit and semi-explicit prompts in the V1 subset.",
    )

    # 4.1: clarify scope vs sections 4.2-4.4
    set_para(
        doc,
        91,
        "The primary research question asked whether the effect of inference temperature on demographic defaulting depended on prompt specificity. "
        "Sections 4.2 through 4.4 report the original V1 gender subset (N=972). "
        "This section and Section 4.5 use the merged gender dataset (1,828 stories: 974 V1 plus 854 supplement). "
        "For the six-point temperature sweep at top_p=1.0, 1,330 merged stories had evaluable gender classifications. "
        "Table 1 summarizes stereotype-aligned rates at T=0.3 and T=1.5. Table 1b summarizes rates at all six temperature values for implicit and semi-explicit prompts.",
    )

    # 5.1: restore V1 caution paragraph; keep supplement first paragraph
    set_para(
        doc,
        145,
        "The OLS result and the non-significant logistic interaction can coexist. Female marker proportion captures gradual shifts in pronoun usage. Stereotype alignment is a coarser binary threshold. "
        "Implicit prompts showed a steady drop in female marker share as temperature rose in the merged dataset, even when binary alignment did not show a clean monotonic pattern. "
        "In the original two-point V1 comparison, Llama 3.1 8B and Mistral 7B both increased in implicit stereotype alignment by 11.1 percentage points at high temperature, while Qwen 2.5 7B moved in the opposite direction.",
    )

    # 5.3: untouched V1 model rates (do not use merged numbers here)
    set_para(
        doc,
        151,
        "Model identity was a stronger predictor of demographic defaulting than any hyperparameter condition in the V1 subset. Mistral 7B showed 69.5% defaulting, compared to 54.0% for Llama and 53.1% for Qwen. This 15-to-16 percentage point gap between Mistral and the other two models was consistent across all tier × condition cells in the stratified heatmap.",
    )

    # 7: restore V1 descriptive conclusion paragraph; keep joint-effect sentence in 165/167
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

  # 6 limitations: clarify V1 vs supplement scope
    set_para(
        doc,
        158,
        "Scale and hyperparameter coverage. The original V1 design used four hyperparameter conditions. The supplement added six temperature values at top_p=1.0 and two top_p values at T=1.0 for the gender dimension only. That supplement grid was 94% complete (854 of 910 targeted new gender stories). Joint-effect results in Sections 4.1 and 4.5 use the merged gender dataset. Tier, role, and model summaries in Sections 4.2-4.4 remain on the V1 gender subset unless noted. Non-monotonic implicit alignment rates at intermediate temperatures suggest that binary outcomes may need still wider sweeps.",
    )

    doc.save(PATH)
    print("Fixed scope:", PATH)


if __name__ == "__main__":
    main()
