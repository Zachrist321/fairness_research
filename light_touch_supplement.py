"""Light edits to abstract, discussion 5.1, 5.2, and conclusion."""
from docx import Document

PATH = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-FINAL.docx"


def set_para(doc, idx, text):
    doc.paragraphs[idx].text = text


def main():
    doc = Document(PATH)

    set_para(
        doc,
        8,
        "Most fairness evaluations of large language models test models under a single fixed condition, "
        "with one prompt style and default inference settings. Yet real deployments combine prompts of "
        "varying specificity with customized sampling configurations. This study examined whether inference "
        "temperature affects stereotype generation in open-ended story prompts and whether that effect "
        "depends on prompt specificity. Three instruction-tuned open-source models were tested across three "
        "prompt tiers (implicit, semi-explicit, and explicit). The primary V1 run compared T=0.3 and T=1.5 "
        "at top_p=1.0. A supplement run added six temperature values at top_p=1.0 (0.3, 0.5, 0.7, 1.0, 1.3, 1.5) "
        "and two top_p values at T=1.0 (0.3, 0.9). Gender defaulting was measured with a deterministic "
        "pronoun-based method applied to the first 180 words of each story. The merged gender dataset "
        "comprised 1,828 stories (974 from V1 and 854 from the supplement). With six temperature points, "
        "female marker proportion declined as temperature increased for implicit prompts (OLS slope b=-0.105, "
        "p=0.008) but not for semi-explicit or explicit prompts. The logistic interaction between continuous "
        "temperature and prompt tier remained non-significant (implicit vs semi-explicit interaction b=-0.39, "
        "p=0.22). Explicit counter-stereotypical prompts reduced stereotype alignment to about 16%. Prompt "
        "framing remained the stronger lever. These results support a tiered evaluation approach. A wider "
        "temperature grid picked up shifts in gendered wording for implicit prompts that the two-point "
        "comparison could not.",
    )

    set_para(
        doc,
        144,
        "The central question was whether inference temperature affects stereotype generation differently "
        "across prompt tiers. With six temperature points at top_p=1.0, female marker proportion declined "
        "for implicit prompts (p=0.008) but not for semi-explicit or explicit prompts. The logistic "
        "interaction on binary stereotype alignment remained non-significant (p=0.22 for implicit vs "
        "semi-explicit). The wider grid showed a temperature effect on gendered wording for implicit prompts, "
        "but not on binary stereotype alignment.",
    )

    set_para(
        doc,
        145,
        "The OLS result and the non-significant logistic interaction can coexist. Female marker proportion "
        "tracks gradual shifts in pronoun usage. Stereotype alignment is a simpler binary measure. Implicit "
        "prompts showed a steady drop in female marker share as temperature rose in the merged dataset, even "
        "when binary alignment did not follow a clean pattern. In the original two-point V1 comparison, Llama "
        "3.1 8B and Mistral 7B both increased in implicit stereotype alignment by 11.1 percentage points at "
        "high temperature, while Qwen 2.5 7B moved in the opposite direction.",
    )

    set_para(
        doc,
        146,
        "Two interpretations remain. Temperature may shift gendered wording without changing binary stereotype "
        "alignment enough to reach significance in logistic models. Or the implicit-tier OLS slope may reflect "
        "real tier-specific sensitivity that logistic models with one alignment threshold cannot detect well. "
        "The supplement helped with the limited two-point design but did not settle the interaction question.",
    )

    set_para(
        doc,
        148,
        "Prompt specificity had a clear effect on which type of bias appeared, even if it did not moderate "
        "the hyperparameter effect. As shown in Figure 5, explicit prompts produced 0.0% direct stereotype "
        "language, consistent with the safety training these models receive. Semi-explicit and implicit prompts "
        "both produced approximately 59% stereotype-aligned defaulting, well above chance. These tier baselines "
        "came from the V1 factorial and were not changed by the supplement run.",
    )

    set_para(
        doc,
        165,
        "This paper asked whether inference temperature and stereotype generation interact with prompt specificity. "
        "The supplement used six temperature points. Female marker proportion fell with temperature for implicit "
        "prompts (p=0.008). The logistic interaction on binary stereotype alignment remained non-significant. "
        "Explicit prompts stayed near 16% alignment across conditions. Prompt framing remains the strongest lever. "
        "Temperature mattered more for implicit prompts and for how gender was worded than for binary alignment.",
    )

    set_para(
        doc,
        167,
        "The most important finding is that instruction-tuned models suppressed explicit discriminatory language "
        "while retaining substantial demographic associations in character framing. A fairness audit that only "
        "scans for explicit bias would report near-zero rates for all three models and conclude they are unbiased. "
        "The tiered framework used in this study showed that this conclusion was wrong. Within the four V1 inference "
        "conditions tested, adjusting temperature or top-p did not substantially change the 59% implicit defaulting "
        "rate. The supplement showed that implicit prompts shift in gendered wording across a wider temperature range.",
    )

    doc.save(PATH)
    print("Light touch applied:", PATH)


if __name__ == "__main__":
    main()
