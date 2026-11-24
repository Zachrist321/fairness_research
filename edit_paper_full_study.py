"""Reframe paper on full 3,888-story four-dimension study (not gender-only)."""
from __future__ import annotations

from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

PATH = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-FINAL.docx"


def set_para(doc: Document, idx: int, text: str) -> None:
    doc.paragraphs[idx].text = text


def insert_before(paragraph, text: str) -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addprevious(new_p)
    new_para = Paragraph(new_p, paragraph._parent)
    new_para.text = text
    return new_para


def main() -> None:
    doc = Document(PATH)

    set_para(
        doc,
        8,
        "Most fairness evaluations of large language models test models under one prompt style and "
        "default inference settings. Real use often mixes prompts of different specificity with "
        "different sampling settings. This study asked whether inference hyperparameters affect "
        "stereotype generation in open-ended story prompts and whether that effect depends on how "
        "specific the prompt is. Three instruction-tuned open-source models generated 3,888 stories "
        "in a factorial design across four demographic dimensions (gender, race, age, and "
        "occupation). Each dimension used 108 matched prompts at three specificity tiers and four "
        "hyperparameter conditions. The primary joint-effect test used deterministic gender "
        "defaulting on the original 972 gender stories. The tier by condition interaction was not "
        "statistically significant (chi-square = 2.95, p = 0.889). Gender defaulting on implicit "
        "and semi-explicit prompts stayed near 59 percent. Explicit stereotype language was absent. "
        "A gender-only supplement extended temperature to six values (1,828 merged stories). That "
        "supplement showed a temperature-linked drop in female marker proportion for implicit "
        "prompts. Stereotype-aligned rates did not shift cleanly by tier. Embedding-based analysis "
        "across all 3,888 stories showed dimension-specific stereotype similarity patterns. "
        "Prompt framing and model choice mattered more than decoding settings in the ranges tested.",
    )

    set_para(
        doc,
        15,
        "This paper tests whether prompt specificity and inference hyperparameters jointly affect "
        "stereotype generation in open-source language models. The experiment crossed both factors "
        "across a full 3,888-story factorial run covering gender, race, age, and occupation prompts. "
        "The question is whether the relationship between hyperparameter settings and demographic "
        "stereotyping changes depending on how explicitly the prompt frames demographic identity.",
    )

    set_para(
        doc,
        17,
        "This paper makes three contributions. First, it defines a three-tier prompt specificity "
        "taxonomy (implicit role only, semi-explicit neutral name, fully explicit demographic "
        "identity stated) and applies it across four demographic dimensions in open-ended story "
        "generation. Second, it reports a controlled factorial experiment that crosses this taxonomy "
        "with four hyperparameter conditions across three open-source models on 3,888 stories. "
        "Third, it introduces a tiered bias evaluation framework. It separates explicit stereotype "
        "language from implicit demographic defaulting. It shows that this distinction is needed to "
        "detect the bias that instruction-tuned models actually produce.",
    )

    set_para(
        doc,
        58,
        "The full run comprised 3,888 planned generations (108 prompts × 4 hyperparameter conditions "
        "× 3 random seeds × 3 models). Stories were balanced across four demographic dimensions with "
        "972 stories per dimension. Four early pilot rows at temperature 0.7 were excluded from "
        "analysis. For gender only, the grid was later extended to six temperature values at nucleus "
        "sampling probability 1.0 and two nucleus sampling values at temperature 1.0. The completed "
        "merged gender dataset comprised 1,828 stories (94 percent of the targeted supplement grid).",
    )

    set_para(
        doc,
        60,
        "Each demographic dimension used nine scenario variants expressed at three specificity tiers. "
        "This produced 108 prompts in total (9 scenarios × 3 tiers × 4 dimensions). Gender prompts "
        "used occupation-linked scenarios such as nurse and surgeon. Race prompts used professional "
        "roles with culturally associated name cues in the semi-explicit tier. Age prompts used "
        "life-stage scenarios. Occupation prompts tested male- versus female-stereotyped job labels "
        "directly.",
    )

    set_para(
        doc,
        81,
        "Explicit bias rate measured direct stereotype language across all 972 V1 gender stories.",
    )

    set_para(
        doc,
        84,
        "Coverage on the V1 gender subset: 957 of 972 stories (98.5 percent) yielded a classifiable "
        "protagonist gender. The remaining 15 stories used gender-neutral language throughout and "
        "were treated as ambiguous. In the merged gender supplement dataset used in Section 4.6, "
        "1,804 of 1,828 stories (98.7 percent) were classifiable.",
    )

    set_para(
        doc,
        86,
        "The primary analysis tested the joint effect of prompt specificity and inference "
        "hyperparameters on stereotype-aligned gender defaulting in the original four-condition "
        "factorial design (N = 972 gender stories). A contingency chi-square test was applied to "
        "the 2 × 4 table of tier (implicit / semi) × condition, with aligned protagonist count as "
        "the outcome variable. Secondary analyses computed defaulting rates by model and by prompt "
        "tier on the same V1 subset. A gender-only supplement run added a six-point temperature "
        "sweep and nucleus sampling checks at temperature 1.0. Female marker proportion in the "
        "first 180 words was tracked on that merged gender dataset. Embedding-based stereotype "
        "similarity was summarized across all 3,888 stories and all four demographic dimensions. "
        "All analyses were implemented in Python using pandas and scipy.",
    )

    set_para(
        doc,
        91,
        "The primary research question asked whether the effect of inference hyperparameters on "
        "demographic defaulting depended on prompt specificity. This test used the original "
        "factorial gender subset (N = 972 stories, four hyperparameter conditions). Table 1 shows "
        "stereotype-aligned defaulting rates for implicit and semi-explicit prompts at each "
        "condition.",
    )

    set_para(
        doc,
        93,
        "[Figure 1. Joint effect interaction plot for the V1 gender subset. "
        "outputs/deterministic_bias/figures/fig7_joint_effect_interaction.png]",
    )

    set_para(
        doc,
        94,
        "",
    )

    set_para(
        doc,
        96,
        "A chi-square test on the 2 × 4 contingency table (tier × condition, outcome = aligned "
        "protagonist) returned chi-square = 2.95, df = 7, p = 0.889. The interaction was not "
        "statistically significant. Both prompt tiers showed similar variation across conditions: "
        "8.0 percentage points for implicit prompts and 9.7 percentage points for semi-explicit "
        "prompts. The two lines cross between conditions, but the pattern is inconsistent and the "
        "test confirms no significant interaction at the 0.05 level.",
    )

    set_para(
        doc,
        97,
        "This result does not support the hypothesis that higher temperature or wider nucleus "
        "sampling amplifies bias more under implicit prompts than under semi-explicit prompts. In "
        "this scaled four-condition design, prompt specificity set the overall level of defaulting, "
        "while hyperparameters contributed only modest variation within each tier. Section 4.6 "
        "reports an extended gender temperature grid that adds finer resolution but does not change "
        "this primary conclusion.",
    )

    set_para(
        doc,
        100,
        "Table 2. Stereotype-aligned rates by bias tier (gender dimension, V1 subset, 972 stories).",
    )

    set_para(
        doc,
        101,
        "[Figure 5. Stereotype-aligned rate by bias tier. "
        "outputs/deterministic_bias/figures/fig4_gender_share_by_tier.png]",
    )

    set_para(
        doc,
        103,
        "Explicit stereotype language was absent in the gender subset (0.0 percent). This matched "
        "the safety training that instruction-tuned models receive. The same models showed 58.8 "
        "percent semi-explicit and 58.9 percent implicit defaulting. A chi-square test compared "
        "explicit and implicit tiers using 45 aligned of 323 explicit stories and 189 aligned of "
        "321 implicit stories. The result was significant (p less than 0.001).",
    )

    set_para(
        doc,
        104,
        "Semi-explicit (58.8 percent) and implicit (58.9 percent) rates were nearly identical. "
        "Removing the demographic cue did not reduce defaulting compared with adding a neutral "
        "name. Explicit counter-stereotypical prompts reduced stereotype alignment to 13.9 percent.",
    )

    set_para(
        doc,
        108,
        "[Figure 3. Protagonist gender by role for implicit prompts. "
        "outputs/deterministic_bias/figures/fig1_implicit_defaults_by_role.png]",
    )

    set_para(
        doc,
        110,
        "Female-stereotyped roles were assigned female protagonists in 100 percent of classifiable "
        "implicit stories for nurse, kindergarten teacher, and ballet dancer. Social worker followed "
        "at 91.4 percent. Male-stereotyped roles showed weaker alignment. Military officer received "
        "a male protagonist in 44.4 percent of stories. Surgeon scored 19.4 percent "
        "stereotype-aligned. Mechanical engineer scored 19.4 percent stereotype-aligned.",
    )

    set_para(
        doc,
        112,
        "Stereotype-aligned defaulting rates differed across the three models on implicit and "
        "semi-explicit prompts combined in the V1 subset. Mistral 7B showed the highest rate at "
        "69.5 percent. Llama 3.1 8B showed 54.0 percent. Qwen 2.5 7B showed 53.1 percent.",
    )

    set_para(
        doc,
        114,
        "[Figure 4. Stereotype-aligned rate by model. "
        "outputs/deterministic_bias/figures/fig3_stereotype_aligned_by_model.png]",
    )

    set_para(
        doc,
        117,
        "[Figure 2. Stereotype-aligned rate by tier and condition per model. "
        "outputs/deterministic_bias/figures/fig8_joint_effect_by_model.png]",
    )

    # Insert cross-dimension section before old 4.5
    anchor = doc.paragraphs[119]
    p1 = insert_before(anchor, "4.5 Cross-Dimension Patterns Across the Full Study")
    p2 = insert_before(
        anchor,
        "The full factorial run collected 972 stories per demographic dimension (3,888 total). "
        "Deterministic defaulting was applied in detail to gender. For all four dimensions, "
        "embedding-based stereotype similarity measured cosine similarity between each generated "
        "story and dimension-specific stereotype reference sentences.",
    )
    p3 = insert_before(
        anchor,
        "On implicit and semi-explicit prompts, occupation-dimension stories showed the highest "
        "mean stereotype similarity (0.30 to 0.33). Age stories followed (0.19 to 0.20). Gender and "
        "race stories were lower (0.12 to 0.16). Explicit-tier prompts did not uniformly reduce "
        "similarity. Race explicit-tier stories averaged 0.18 similarity compared with 0.12 on "
        "implicit prompts. Age explicit-tier stories averaged 0.21 compared with 0.19 on implicit "
        "prompts. These embedding patterns are exploratory. They show that bias signals differ by "
        "demographic category and are not interchangeable with gender defaulting rates.",
    )
    caption = insert_before(
        anchor,
        "Table 5. Mean embedding stereotype similarity by demographic dimension and prompt tier "
        "(V1 subset, 3,888 stories).",
    )
    tbl = doc.add_table(rows=5, cols=4)
    tbl.style = "Table Grid"
    hdr = ["Dimension", "Implicit", "Semi-explicit", "Explicit"]
    for j, h in enumerate(hdr):
        tbl.rows[0].cells[j].text = h
    data = [
        ("Gender", "0.159", "0.145", "0.158"),
        ("Race", "0.123", "0.142", "0.179"),
        ("Age", "0.188", "0.198", "0.212"),
        ("Occupation", "0.323", "0.305", "0.328"),
    ]
    for ri, row in enumerate(data, start=1):
        for j, val in enumerate(row):
            tbl.rows[ri].cells[j].text = val
    caption._p.addnext(tbl._tbl)

    # Renumber following sections (indices shifted by 4)
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t == "4.5 Hyperparameter Effect":
            p.text = "4.6 Extended Gender Temperature Grid"
        elif t.startswith("4.6 Supplementary Analyses"):
            p.text = "4.7 Supplementary Analyses"

    # Update extended grid section text (find by content after insertions)
    for i, p in enumerate(doc.paragraphs):
        t = p.text
        if t.startswith("The extended temperature grid covered six values"):
            p.text = (
                "The gender-only supplement extended the original four-condition design. It covered "
                "six temperature values at nucleus sampling probability 1.0 on the merged gender "
                "dataset (1,828 stories). Table 6 summarizes stereotype-aligned rates for implicit "
                "and semi-explicit prompts at each temperature. Table 6b summarizes nucleus sampling "
                "effects at temperature 1.0."
            )
        elif t.startswith("Table 5. Stereotype-aligned defaulting rate by inference condition"):
            p.text = (
                "Table 6. Stereotype-aligned defaulting rate by inference condition "
                "(implicit + semi-explicit prompts, merged gender dataset, all models)."
            )
        elif "fig_temp_sweep_stereotype_aligned" in t:
            p.text = (
                "[Figure 6. Stereotype-aligned rate across six temperatures by prompt tier. "
                "figures/merged/fig_temp_sweep_stereotype_aligned.png]"
            )
        elif t.startswith("At nucleus sampling probability 1.0, implicit stereotype-aligned rates ranged"):
            p.text = (
                "At nucleus sampling probability 1.0 on the merged gender dataset, implicit "
                "stereotype-aligned rates ranged from 56.2 percent at temperature 0.3 to 70.8 percent "
                "at temperature 1.3, then 61.3 percent at temperature 1.5. Semi-explicit rates "
                "stayed between 53.9 and 63.9 percent. Explicit rates stayed near 14 to 16 percent. "
                "Female marker proportion for implicit prompts fell from 81.8 percent at "
                "temperature 0.3 to 72.5 percent at temperature 1.5. At temperature 1.0, varying "
                "nucleus sampling from 0.3 to 0.9 produced small shifts for implicit prompts "
                "(55.0 percent versus 63.0 percent in the V1 subset)."
            )

    set_para(
        doc,
        143,
        "5.1 The Joint Effect Question",
    )

    # Discussion - find paragraphs by content
    for p in doc.paragraphs:
        t = p.text
        if t.startswith("The main question was whether temperature affects stereotype generation differently"):
            p.text = (
                "The main question was whether inference hyperparameters affect stereotype generation "
                "differently across prompt tiers. In the primary four-condition factorial test on 972 "
                "gender stories, the tier × condition interaction was not statistically significant "
                "(chi-square = 2.95, p = 0.889). Hyperparameters shifted defaulting only modestly "
                "within each tier."
            )
        elif t.startswith("Female marker proportion tracks gradual shifts"):
            p.text = (
                "The gender supplement added a six-point temperature sweep. Female marker proportion "
                "declined for implicit prompts but not for semi-explicit or explicit prompts. "
                "Stereotype-aligned rates did not shift in a clean tier-specific pattern. Female "
                "marker proportion tracks gradual shifts in pronoun usage. Stereotype alignment is a "
                "simpler yes-or-no measure. Different models also moved in different directions at "
                "the two original V1 endpoints. Llama and Mistral both rose on implicit alignment "
                "from low to high temperature. Qwen fell."
            )
        elif t.startswith("Temperature may shift gendered wording"):
            p.text = (
                "Temperature may shift gendered wording without changing stereotype-aligned rates "
                "enough to show a clear tier interaction in the primary test. The wider gender grid "
                "made the implicit wording shift visible. It did not overturn the non-significant "
                "interaction from the original four-condition design."
            )
        elif t.startswith("Prompt specificity had a clear effect"):
            p.text = (
                "Prompt specificity had a clear effect on which type of bias appeared. As shown in "
                "Figure 5, explicit prompts produced 0.0 percent direct stereotype language. "
                "Semi-explicit and implicit prompts both produced about 59 percent "
                "stereotype-aligned defaulting in the V1 gender subset, well above chance."
            )
        elif t.startswith("Semi-explicit and implicit rates were nearly identical"):
            p.text = (
                "Semi-explicit and implicit rates were nearly identical in the V1 subset. Adding a "
                "gender-neutral name did not reduce defaulting. Giving no identity information "
                "produced the same result. Role context alone triggered the models' demographic "
                "associations."
            )
        elif t.startswith("Model identity was a stronger predictor"):
            p.text = (
                "Model identity was a stronger predictor of demographic defaulting than "
                "hyperparameter settings in the V1 subset. Mistral 7B showed 69.5 percent defaulting "
                "on implicit and semi-explicit prompts combined. Qwen 2.5 7B showed 53.1 percent. "
                "Llama 3.1 8B showed 54.0 percent."
            )

    for p in doc.paragraphs:
        t = p.text
        if t.startswith("Scale and hyperparameter coverage."):
            p.text = (
                "Scale and hyperparameter coverage. The original factorial design used four "
                "hyperparameter conditions across all 3,888 stories. The gender supplement added six "
                "temperature values at nucleus sampling probability 1.0 and two nucleus sampling "
                "values at temperature 1.0 for the gender dimension only. That supplement grid was "
                "94 percent complete (854 of 910 targeted new gender stories). Primary joint-effect "
                "results in Section 4.1 use the V1 four-condition gender subset. Section 4.6 reports "
                "the extended gender grid."
            )
        elif t.startswith("Demographic scope."):
            p.text = (
                "Demographic scope. Deterministic tiered defaulting was applied in detail to the "
                "gender dimension. The same 108-prompt design also generated 972 stories each for "
                "race, age, and occupation. Cross-dimension embedding summaries in Section 4.5 "
                "show that stereotype similarity patterns differ by dimension. Those results should "
                "not be read as equivalent to gender defaulting rates."
            )

    for p in doc.paragraphs:
        t = p.text
        if t.startswith("This paper asked whether temperature and stereotype generation interact"):
            p.text = (
                "This paper asked whether inference hyperparameters and stereotype generation "
                "interact with prompt specificity in a full 3,888-story factorial experiment across "
                "gender, race, age, and occupation prompts. The primary four-condition test on 972 "
                "gender stories found no statistically significant tier × condition interaction "
                "(chi-square = 2.95, p = 0.889). A gender supplement with six temperature values "
                "showed tier differences in gendered wording that a two-point comparison could not."
            )
        elif t.startswith("Three models that passed an explicit-bias test at about 14 percent"):
            p.text = (
                "Three models that passed an explicit-bias test at about 14 percent stereotype "
                "alignment in the V1 subset all produced implicit and semi-explicit defaulting near "
                "59 percent. The role of nurse was assigned a female protagonist in over 90 percent "
                "of implicit stories. Surgeon and mechanical engineer showed low stereotype alignment "
                "despite male-stereotyped roles. These patterns held across all three models and all "
                "four V1 hyperparameter conditions."
            )
        elif t.startswith("Instruction-tuned models suppressed explicit discriminatory language"):
            p.text = (
                "Instruction-tuned models suppressed explicit discriminatory language. They still "
                "retained demographic associations in character framing. A fairness audit that only "
                "scans for explicit bias would report near-zero rates. It would wrongly conclude the "
                "models are unbiased. The tiered framework showed that conclusion was wrong. Within "
                "the four V1 inference conditions tested, adjusting temperature or nucleus sampling "
                "did not substantially change the 59 percent implicit defaulting rate."
            )
        elif t.startswith("Three directions remain for future work."):
            p.text = (
                "Three directions remain for future work. First, complete the remaining gender "
                "supplement grid cells. Second, extend deterministic tiered measurement to race, age, "
                "and occupation with dimension-specific coders. Third, compare model families on why "
                "Mistral defaulting rates exceed Llama and Qwen."
            )

    doc.save(PATH)
    print("Updated:", PATH)


if __name__ == "__main__":
    main()
