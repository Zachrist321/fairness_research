"""Audit fixes: merged numbers, figure paths, short sentences, no dashes in body."""
from docx import Document

PATH = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-FINAL.docx"


def set_para(doc, idx, text):
    doc.paragraphs[idx].text = text


def main():
    doc = Document(PATH)

    set_para(
        doc,
        58,
        "The full run comprised 3,888 planned generations across all demographic dimensions. "
        "Four early pilot rows at temperature 0.7 were excluded. "
        "For gender, the grid was extended to six temperature values at nucleus sampling probability 1.0 "
        "and two nucleus sampling values at temperature 1.0. "
        "The completed gender dataset comprised 1,828 stories. "
        "The grid was 94 percent complete.",
    )

    set_para(
        doc,
        79,
        "The primary analysis used a deterministic tiered bias measurement procedure on the saved story texts. "
        "No additional model calls were required. "
        "A deterministic approach was preferred over LLM-as-judge scoring. "
        "Demchak et al. (2024) showed that classifier models used in bias benchmarks carry their own biases. "
        "Judge-based scores in this experiment also showed a strong floor effect (Section 4.6). "
        "The procedure identified the protagonist gender from early gender-coded markers in each story. "
        "These included gendered pronouns, titles, and nouns. "
        "Using early markers approximates the protagonist and avoids miscounting secondary characters.",
    )

    set_para(
        doc,
        81,
        "Explicit bias rate measured direct stereotype language across all 1,828 gender stories.",
    )

    set_para(
        doc,
        82,
        "Semi-explicit defaulting rate measured stereotype alignment on neutral-name prompts.",
    )

    set_para(
        doc,
        83,
        "Implicit defaulting rate measured stereotype alignment on role-only prompts.",
    )

    set_para(
        doc,
        92,
        "Table 1. Stereotype-aligned defaulting rate (percent) by prompt tier at temperature 0.3 "
        "and temperature 1.5 (nucleus sampling probability 1.0, 1,828 stories).",
    )

    set_para(
        doc,
        93,
        "[Figure 1: Stereotype-aligned rate by prompt tier at temperature 0.3 and 1.5. "
        "File: figures/merged/fig_joint_stereotype_rate.png]",
    )

    set_para(
        doc,
        94,
        "[Figure 1b: Female marker proportion across six temperature values. "
        "File: figures/merged/fig_supplement_temp_sweep_x_tier.png]",
    )

    set_para(
        doc,
        96,
        "At nucleus sampling probability 1.0, explicit prompts stayed near 14 to 16 percent across "
        "all six temperatures. Semi-explicit rates stayed between 54 and 64 percent. "
        "Implicit rates ranged from 56.2 percent at temperature 0.3 to 70.8 percent at temperature 1.3. "
        "They then fell to 61.3 percent at temperature 1.5. "
        "The three tiers did not move in parallel. "
        "Female marker proportion fell for implicit prompts as temperature rose. "
        "Semi-explicit and explicit prompts showed little change on that measure.",
    )

    set_para(
        doc,
        101,
        "[Figure 5: Stereotype-aligned rate by bias tier. "
        "File: figures/merged/fig5_tiered_bias_summary.png]",
    )

    set_para(
        doc,
        103,
        "Explicit stereotype language was absent in the gender subset (0.0 percent). "
        "This matched the safety training that instruction-tuned models receive. "
        "The same models showed 60.4 percent semi-explicit and 60.7 percent implicit defaulting. "
        "A chi-square test compared explicit and implicit tiers. "
        "It used 86 aligned of 602 explicit stories and 369 aligned of 608 implicit stories. "
        "The result was significant (p less than 0.001).",
    )

    set_para(
        doc,
        108,
        "[Figure 3: Protagonist gender by role for implicit prompts. "
        "File: figures/merged/fig3_role_defaults.png]",
    )

    set_para(
        doc,
        110,
        "Female-stereotyped roles were assigned female protagonists in 100 percent of classifiable "
        "stories for nurse, kindergarten teacher, and ballet dancer. "
        "Social worker followed at 91.5 percent. "
        "Male-stereotyped roles showed weaker alignment. "
        "Military officer received a male protagonist in 48.3 percent of stories. "
        "Surgeon scored 16.7 percent stereotype-aligned. "
        "Mechanical engineer scored 25.0 percent stereotype-aligned.",
    )

    set_para(
        doc,
        114,
        "[Figure 4: Stereotype-aligned rate by model. "
        "File: figures/merged/fig4_model_comparison.png]",
    )

    set_para(
        doc,
        116,
        "Mistral's higher defaulting rate held across both prompt tiers and all four initial "
        "hyperparameter conditions. "
        "On the implicit tier, Mistral ranged from 63 to 78 percent. "
        "Llama ranged from 48 to 63 percent. "
        "Qwen ranged from 44 to 58 percent. "
        "The gap was stable across conditions. "
        "It reflected the model, not one hyperparameter setting.",
    )

    set_para(
        doc,
        117,
        "[Figure 2: Stereotype-aligned rate by tier and condition per model. "
        "File: figures/merged/fig_joint_per_model.png]",
    )

    set_para(
        doc,
        122,
        "[Figure 6: Stereotype-aligned rate across six temperatures by prompt tier. "
        "File: figures/merged/fig_temp_sweep_stereotype_aligned.png]",
    )

    set_para(
        doc,
        149,
        "Semi-explicit and implicit rates were nearly identical. "
        "Adding a gender-neutral name did not reduce defaulting. "
        "Giving no identity information produced the same result. "
        "Role context alone triggered the models' demographic associations.",
    )

    set_para(
        doc,
        152,
        "Model choice matters for teams picking an open-source model. "
        "It mattered more than adjusting temperature or nucleus sampling in the ranges tested here. "
        "Larger 13B and 70B models were not tested due to GPU limits on free Colab. "
        "Closed-source models such as GPT-4 were excluded because sampling settings cannot be controlled fully. "
        "The three 7 to 8 billion parameter models represent the most accessible deployable tier. "
        "This experiment did not determine why Mistral defaulting was higher.",
    )

    set_para(
        doc,
        154,
        "This study contributes a tiered bias evaluation framework. "
        "It separates explicit bias from semi-explicit and implicit defaulting. "
        "A single aggregate score would have shown near zero for explicit language alone. "
        "It would have shown about 60 percent for implicit and semi-explicit defaulting alone. "
        "Neither number alone is accurate. "
        "LLM-as-judge scoring failed here due to a floor effect. "
        "The judge was the intended primary method. "
        "When 3,861 of 3,882 outputs scored zero, the deterministic tiered analysis replaced it.",
    )

    set_para(
        doc,
        158,
        "Scale and hyperparameter coverage. "
        "The gender grid used six temperature values at nucleus sampling probability 1.0 "
        "and two nucleus sampling values at temperature 1.0. "
        "The grid was 94 percent complete. "
        "Implicit alignment rates at intermediate temperatures were not strictly monotonic.",
    )

    set_para(
        doc,
        167,
        "Instruction-tuned models suppressed explicit discriminatory language. "
        "They still retained demographic associations in character framing. "
        "A fairness audit that only scans for explicit bias would report near-zero rates. "
        "It would wrongly conclude the models are unbiased. "
        "The tiered framework showed that conclusion was wrong. "
        "Temperature and nucleus sampling did little to move the roughly 60 percent implicit defaulting rate. "
        "The extended grid showed that implicit prompts still shift in gendered wording across temperature.",
    )

    doc.save(PATH)
    print("Audit fixes applied:", PATH)


if __name__ == "__main__":
    main()
