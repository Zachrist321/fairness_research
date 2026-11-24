"""Rewrite paper around unified 3,888-story joint-effect methodology."""
from __future__ import annotations

from docx import Document

PATH = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-FINAL.docx"


def set_para(doc: Document, idx: int, text: str) -> None:
    doc.paragraphs[idx].text = text


def replace_in_paragraphs(doc: Document, old_start: str, new_text: str) -> bool:
    for p in doc.paragraphs:
        if p.text.strip().startswith(old_start):
            p.text = new_text
            return True
    return False


def main() -> None:
    doc = Document(PATH)

    set_para(
        doc,
        8,
        "Most fairness evaluations of large language models test models under one prompt style and "
        "default inference settings. Real use mixes prompts of different specificity with different "
        "sampling settings. This study tested whether inference hyperparameters and prompt specificity "
        "jointly affect stereotype generation. Three instruction-tuned open-source models generated "
        "3,888 stories in a single factorial design (108 prompts × 4 hyperparameter conditions × 3 seeds "
        "× 3 models) across gender, race, age, and occupation. The primary joint-effect tests used "
        "the full dataset on implicit and semi-explicit prompts. Embedding-based stereotype similarity "
        "showed no significant tier × condition interaction (chi-square = 2.39, p = 0.935). A "
        "deterministic defaulting analysis on gender and occupation stories, which share a pronoun-based "
        "coder with high coverage, also showed no significant interaction (chi-square = 1.83, "
        "p = 0.969). Explicit stereotype language was absent. Prompt framing and model choice mattered "
        "more than decoding settings. A gender-only supplement with six temperature values provided "
        "additional sensitivity analysis but did not change the primary null result.",
    )

    set_para(
        doc,
        15,
        "This paper tests whether prompt specificity and inference hyperparameters jointly affect "
        "stereotype generation in open-source language models. All analyses use one balanced factorial "
        "dataset of 3,888 generated stories covering four demographic dimensions. The research question "
        "is whether the relationship between hyperparameter settings and stereotyping changes depending "
        "on how explicitly the prompt frames demographic identity.",
    )

    set_para(
        doc,
        58,
        "The study used one controlled factorial dataset. It comprised 3,888 planned generations "
        "(108 prompts × 4 hyperparameter conditions × 3 random seeds × 3 models). Stories were balanced "
        "across four demographic dimensions with 972 stories per dimension. Four early pilot rows at "
        "temperature 0.7 were excluded. All primary joint-effect tests in Section 4.1 use this single "
        "dataset. A later gender-only supplement added extra temperature and nucleus sampling values for "
        "sensitivity analysis only (Section 4.5).",
    )

    set_para(
        doc,
        79,
        "All primary analyses use the same 3,888-story factorial dataset. Two complementary outcome "
        "measures were applied. First, embedding-based stereotype similarity compared each story to "
        "dimension-specific reference stereotypes using a sentence transformer. This measure has full "
        "coverage across all dimensions. Second, deterministic stereotype-aligned defaulting coded "
        "whether the generated protagonist matched the scenario stereotype. Gender and occupation "
        "used pronoun and gendered-noun markers in the opening text. Age used life-stage keywords. "
        "Race used ethnicity keyword patterns. Gender and occupation coders had 98 percent or higher "
        "coverage. Race coverage was low (13 percent) and is reported descriptively only.",
    )

    set_para(
        doc,
        80,
        "For the joint-effect test, implicit and semi-explicit prompts were analyzed. Explicit prompts "
        "were excluded because they state demographic identity directly. The outcome was either "
        "high embedding stereotype similarity (above the within-dimension median) or binary stereotype "
        "alignment from the deterministic coder.",
    )

    set_para(
        doc,
        81,
        "Explicit bias rate measured direct stereotype language across all 3,888 stories.",
    )

    set_para(
        doc,
        84,
        "Coverage for deterministic defaulting varied by dimension. Gender: 957 of 972 evaluable "
        "(98.5 percent). Occupation: 646 of 648 on implicit and semi-explicit prompts (99.7 percent). "
        "Age: 341 of 648 (52.6 percent). Race: 87 of 648 (13.4 percent). Primary deterministic "
        "joint-effect pooling therefore used gender and occupation only.",
    )

    set_para(
        doc,
        86,
        "The primary analysis tested the joint effect of prompt tier (implicit vs semi-explicit) and "
        "hyperparameter condition on stereotype outcomes across the full 3,888-story dataset. Two "
        "complementary chi-square tests were run on 2 × 4 contingency tables. Test A used embedding "
        "high-similarity scores with full coverage (N = 2,588 implicit and semi-explicit stories). "
        "Test B used deterministic stereotype alignment on gender and occupation stories only "
        "(N = 1,280). Secondary analyses reported tier rates by dimension, model comparisons, and "
        "role-level patterns on gender. The gender supplement temperature sweep (Section 4.5) was "
        "an exploratory sensitivity check and was not pooled into the primary factorial tests.",
    )

    set_para(
        doc,
        91,
        "The primary research question was whether inference hyperparameters affect stereotype output "
        "differently across prompt tiers. Both primary tests used the full factorial dataset on implicit "
        "and semi-explicit prompts. Table 1 reports embedding-based high stereotype similarity by tier "
        "and condition. Table 1b reports deterministic stereotype-aligned defaulting for gender and "
        "occupation combined.",
    )

    set_para(
        doc,
        92,
        "Table 1. High embedding stereotype similarity rate (percent) by prompt tier and condition "
        "(all dimensions, N = 2,588 implicit and semi-explicit stories).",
    )

    set_para(
        doc,
        93,
        "[Figure 1. Joint effect on embedding stereotype similarity. "
        "outputs/unified_joint/figures/fig_joint_embedding.png]",
    )

    set_para(
        doc,
        96,
        "Test A (embedding, all dimensions). A chi-square test on the 2 × 4 table returned "
        "chi-square = 2.39, df = 7, p = 0.935. Implicit and semi-explicit tiers both stayed near "
        "50 percent high-similarity across conditions. Within-tier spread was under 5 percentage "
        "points. The interaction was not statistically significant.",
    )

    set_para(
        doc,
        97,
        "Test B (deterministic defaulting, gender and occupation pooled). A chi-square test returned "
        "chi-square = 1.83, df = 7, p = 0.969. Implicit rates ranged from 76.4 to 77.8 percent. "
        "Semi-explicit rates ranged from 75.2 to 81.0 percent. The interaction was not statistically "
        "significant. The gender-only subset alone reproduced the prior result (chi-square = 2.95, "
        "p = 0.889, N = 634). Neither test supports the hypothesis that hyperparameters amplify bias "
        "more under implicit than semi-explicit prompts.",
    )

    replace_in_paragraphs(
        doc,
        "4.5 Cross-Dimension Patterns Across the Full Study",
        "4.2 Stereotype Rates by Dimension and Prompt Tier",
    )

    replace_in_paragraphs(
        doc,
        "The full factorial run collected 972 stories per demographic dimension",
        "Table 2 summarizes deterministic stereotype-aligned rates by demographic dimension and "
        "prompt tier. Gender implicit and semi-explicit defaulting stayed near 59 percent. Occupation "
        "defaulting was higher at 95 percent because female-stereotyped job labels dominated the "
        "occupation scenarios. Explicit stereotype language was 0.0 percent across all 3,888 stories.",
    )

    replace_in_paragraphs(
        doc,
        "On implicit and semi-explicit prompts, occupation-dimension stories showed the highest",
        "Age and race deterministic rates are reported for completeness but had limited coder coverage "
        "(52.6 percent and 13.4 percent on implicit and semi-explicit prompts). Those dimension-specific "
        "coders need refinement before they can support pooled hypothesis tests.",
    )

    replace_in_paragraphs(
        doc,
        "Table 5. Mean embedding stereotype similarity by demographic dimension and prompt tier",
        "Table 2. Stereotype-aligned defaulting rate (percent) by demographic dimension and prompt tier "
        "(deterministic coder).",
    )

    replace_in_paragraphs(
        doc,
        "4.6 Extended Gender Temperature Grid",
        "4.5 Gender Temperature Supplement (Sensitivity Analysis)",
    )

    replace_in_paragraphs(
        doc,
        "4.7 Supplementary Analyses",
        "4.6 Supplementary Analyses",
    )

    replace_in_paragraphs(
        doc,
        "The gender-only supplement extended the original four-condition design",
        "As a sensitivity check, the gender dimension was extended to six temperature values at "
        "nucleus sampling probability 1.0 (1,828 merged stories including supplement runs). This "
        "extension was not merged into the primary 3,888-story factorial tests because it uses a "
        "different hyperparameter grid.",
    )

    replace_in_paragraphs(
        doc,
        "Table 6. Stereotype-aligned defaulting rate by inference condition",
        "Table 3. Gender supplement: stereotype-aligned rate by temperature (merged gender dataset).",
    )

    replace_in_paragraphs(
        doc,
        "At nucleus sampling probability 1.0 on the merged gender dataset",
        "On the supplement grid, female marker proportion for implicit prompts fell from 81.8 percent "
        "at temperature 0.3 to 72.5 percent at temperature 1.5. Stereotype-aligned binary rates did "
        "not show a clean tier-specific temperature pattern. This supplement adds descriptive resolution "
        "but does not overturn the null primary joint-effect result on the factorial dataset.",
    )

    # Discussion
    replace_in_paragraphs(
        doc,
        "The main question was whether inference hyperparameters affect stereotype generation differently",
        "The main question was whether inference hyperparameters affect stereotype generation differently "
        "across prompt tiers. Two primary tests on the full factorial dataset both returned non-significant "
        "interactions: embedding across all dimensions (chi-square = 2.39, p = 0.935) and deterministic "
        "defaulting on gender and occupation (chi-square = 1.83, p = 0.969).",
    )

    replace_in_paragraphs(
        doc,
        "The gender supplement added a six-point temperature sweep",
        "The gender temperature supplement showed that female marker proportion shifts with temperature "
        "on implicit prompts. Binary stereotype-aligned rates did not show a parallel tier-specific pattern.",
    )

    replace_in_paragraphs(
        doc,
        "Scale and hyperparameter coverage. The original factorial design used four",
        "Scale and hyperparameter coverage. All primary tests use one 3,888-story factorial dataset with "
        "four hyperparameter conditions. The gender supplement used a wider temperature grid and is "
        "reported separately as sensitivity analysis.",
    )

    replace_in_paragraphs(
        doc,
        "Demographic scope. Deterministic tiered defaulting was applied in detail to the",
        "Demographic scope. Deterministic defaulting coders are reliable for gender and occupation. "
        "Age and race coders had partial coverage and are descriptive only. Embedding similarity "
        "provided the only full-coverage cross-dimensional measure in the primary joint-effect test.",
    )

    replace_in_paragraphs(
        doc,
        "This paper asked whether inference hyperparameters and stereotype generation interact",
        "This paper tested whether inference hyperparameters and stereotype generation interact with "
        "prompt specificity using one 3,888-story factorial experiment. Two primary tests found no "
        "significant tier × condition interaction. Prompt framing and model choice set the observable "
        "bias level more than decoding settings in the ranges tested.",
    )

  # Update tables
    # Table 1 -> embedding joint effect
    t1 = doc.tables[1]
    emb = [
        ("Implicit", "50.8%", "49.4%", "52.2%", "47.4%"),
        ("Semi-explicit", "51.9%", "50.3%", "49.1%", "48.8%"),
    ]
    for i, row in enumerate(emb, start=1):
        for j, val in enumerate(row):
            t1.rows[i].cells[j].text = val

    # Table 5 -> tier by dimension (was embedding similarity table)
    t5 = doc.tables[5]
    tier_data = [
        ("Gender", "58.9%", "58.8%", "13.9%"),
        ("Occupation", "95.3%", "96.3%", "95.7%"),
    ]
    # shrink table to 3 rows (header + 2 data)
    while len(t5.rows) > 3:
        t5._tbl.remove(t5.rows[-1]._tr)
    hdr = ["Dimension", "Implicit", "Semi-explicit", "Explicit"]
    for j, h in enumerate(hdr):
        t5.rows[0].cells[j].text = h
    for i, row in enumerate(tier_data, start=1):
        for j, val in enumerate(row):
            t5.rows[i].cells[j].text = val

    doc.save(PATH)
    print("Unified paper update saved:", PATH)


if __name__ == "__main__":
    main()
