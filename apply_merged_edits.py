"""Apply merged-result edits to the paper. Simple language. No logistic regression."""
from docx import Document

PATH = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-FINAL.docx"


def set_para(doc, idx, text):
    doc.paragraphs[idx].text = text


def main():
    doc = Document(PATH)

    set_para(
        doc,
        8,
        "Most fairness evaluations of large language models test models under one prompt style "
        "and default inference settings. Real use often mixes prompts of different specificity with "
        "different sampling settings. This study asked whether inference temperature affects "
        "stereotype generation in open-ended story prompts and whether that effect depends on how "
        "specific the prompt is. Three instruction-tuned open-source models were tested on three "
        "prompt tiers. Implicit prompts named only the role. Semi-explicit prompts added a "
        "gender-neutral name. Explicit prompts stated a counter-stereotypical gender. The gender "
        "dataset comprised 1,828 stories across six temperature values at nucleus sampling "
        "probability 1.0 and two nucleus sampling values at temperature 1.0. Gender defaulting "
        "was measured with a deterministic pronoun-based method on the first 180 words of each story. "
        "Semi-explicit and implicit prompts produced about 60 percent stereotype-aligned defaulting. "
        "Explicit prompts produced about 14 percent. For implicit prompts, female marker proportion "
        "fell as temperature rose. Semi-explicit and explicit prompts showed little change on that "
        "measure. Stereotype-aligned rates did not shift cleanly by tier as temperature changed. "
        "Prompt framing remained the stronger factor. A wider temperature grid showed tier differences "
        "in gendered wording that a two-point comparison could not.",
    )

    set_para(
        doc,
        58,
        "The study used a controlled factorial design across three models, three prompt tiers, and "
        "four initial hyperparameter conditions. The full run comprised 3,888 planned generations. "
        "Four early pilot rows at temperature 0.7 were excluded. For the gender dimension, the grid "
        "was later extended to six temperature values at nucleus sampling probability 1.0 and two "
        "nucleus sampling values at temperature 1.0. The completed gender dataset comprised 1,828 "
        "stories. The grid was 94 percent complete.",
    )

    set_para(
        doc,
        75,
        "All generations used sampling with temperature and nucleus sampling enabled and a limit of "
        "400 new tokens. Each condition used three random seeds (42, 123, 456). The extended gender "
        "grid added temperature values 0.5, 0.7, 1.0, and 1.3 at nucleus sampling probability 1.0, "
        "plus nucleus sampling values 0.3 and 0.9 at temperature 1.0.",
    )

    set_para(
        doc,
        81,
        "Explicit bias rate: the share of stories containing direct stereotype language or overt "
        "demographic generalizations, measured across all 1,828 gender-dimension stories.",
    )

    set_para(
        doc,
        84,
        "Coverage: 1,804 of 1,828 gender stories (98.7 percent) yielded a classifiable protagonist "
        "gender. The remaining 24 stories used gender-neutral language throughout and were treated "
        "as ambiguous.",
    )

    set_para(
        doc,
        86,
        "The primary analysis tested whether temperature and prompt tier jointly affected stereotype "
        "output. Stereotype-aligned rates were computed at each temperature and tier. Female marker "
        "proportion in the first 180 words was tracked as a continuous measure. Per-tier temperature "
        "slopes were estimated for implicit, semi-explicit, and explicit prompts at nucleus sampling "
        "probability 1.0. Nucleus sampling effects were checked at temperature 1.0.",
    )

    set_para(
        doc,
        91,
        "The main question was whether temperature affects demographic defaulting differently across "
        "prompt tiers. The analysis used all 1,828 gender stories. At nucleus sampling probability "
        "1.0, 1,330 stories had evaluable gender classifications across the six temperature values. "
        "Table 1 shows stereotype-aligned rates at temperature 0.3 and temperature 1.5. Table 1b "
        "shows rates at all six temperatures for implicit and semi-explicit prompts.",
    )

    set_para(
        doc,
        96,
        "At nucleus sampling probability 1.0, explicit prompts stayed near 14 to 16 percent "
        "stereotype-aligned across all six temperatures. Semi-explicit rates stayed between 54 and "
        "64 percent. Implicit rates ranged from 56.2 percent at temperature 0.3 to 70.8 percent at "
        "temperature 1.3, then fell to 61.3 percent at temperature 1.5. The three tiers did not move "
        "in parallel. Female marker proportion fell for implicit prompts as temperature rose. The drop "
        "was significant for implicit prompts. Semi-explicit and explicit prompts showed no significant "
        "slope on that measure.",
    )

    set_para(
        doc,
        97,
        "At the endpoints, implicit stereotype alignment was 56.2 percent at temperature 0.3 and "
        "61.3 percent at temperature 1.5. Semi-explicit alignment was 58.8 percent at temperature 0.3 "
        "and 53.9 percent at temperature 1.5. Explicit alignment was 16.0 percent and 16.2 percent at "
        "those endpoints. Female marker proportion for implicit prompts fell from 81.8 percent at "
        "temperature 0.3 to 72.5 percent at temperature 1.5.",
    )

    set_para(
        doc,
        100,
        "Table 2. Stereotype-aligned rates by bias tier (gender dimension, 1,828 stories).",
    )

    set_para(
        doc,
        103,
        "Explicit stereotype language was absent in the gender subset (0.0 percent). This matched the "
        "safety training that current instruction-tuned models receive. The same models that produced "
        "0.0 percent explicit stereotype language showed 60.4 percent semi-explicit and 60.7 percent "
        "implicit demographic defaulting. A chi-square comparison of explicit versus implicit defaulting "
        "rates (86 aligned out of 602 explicit stories versus 369 aligned out of 608 implicit stories) "
        "was significant (p less than 0.001).",
    )

    set_para(
        doc,
        104,
        "Semi-explicit (60.4 percent) and implicit (60.7 percent) rates were nearly identical. "
        "Removing the demographic cue did not reduce defaulting compared with adding a neutral name. "
        "Explicit counter-stereotypical prompts reduced stereotype alignment to 14.3 percent.",
    )

    set_para(
        doc,
        110,
        "Female-stereotyped roles were assigned female protagonists in 100 percent of classifiable "
        "stories for nurse, kindergarten teacher, and ballet dancer. Social worker followed at 91.5 "
        "percent. Male-stereotyped roles showed weaker alignment. Military officer received a male "
        "protagonist in 48.3 percent of stories. Surgeon and mechanical engineer each scored 16.7 and "
        "25.0 percent stereotype-aligned.",
    )

    set_para(
        doc,
        112,
        "Stereotype-aligned defaulting rates differed across the three models on implicit and "
        "semi-explicit prompts combined. Mistral 7B showed the highest rate at 68.3 percent. Qwen 2.5 "
        "7B showed 58.6 percent. Llama 3.1 8B showed 54.5 percent.",
    )

    set_para(
        doc,
        120,
        "The extended temperature grid covered six values at nucleus sampling probability 1.0. "
        "Table 5 summarizes stereotype-aligned rates for implicit and semi-explicit prompts at each "
        "temperature. Table 5b summarizes nucleus sampling effects at temperature 1.0.",
    )

    set_para(
        doc,
        124,
        "At nucleus sampling probability 1.0, implicit stereotype-aligned rates ranged from 56.2 "
        "percent at temperature 0.3 to 70.8 percent at temperature 1.3, then 61.3 percent at "
        "temperature 1.5. Semi-explicit rates stayed between 53.9 and 63.9 percent. Explicit rates "
        "stayed near 14 to 16 percent. At temperature 1.0, varying nucleus sampling from 0.3 to 0.9 "
        "produced small shifts for implicit prompts (55.0 percent versus 63.0 percent).",
    )

    set_para(
        doc,
        144,
        "The main question was whether temperature affects stereotype generation differently across "
        "prompt tiers. With six temperature points at nucleus sampling probability 1.0, female marker "
        "proportion declined for implicit prompts but not for semi-explicit or explicit prompts. "
        "Stereotype-aligned rates did not shift in a clean tier-specific pattern. Explicit prompts "
        "stayed flat near 14 to 16 percent across temperatures.",
    )

    set_para(
        doc,
        145,
        "Female marker proportion tracks gradual shifts in pronoun usage. Stereotype alignment is a "
        "simpler yes-or-no measure. Implicit prompts showed a steady drop in female marker share as "
        "temperature rose, even when binary alignment did not follow a clean line. Different models "
        "also moved in different directions at the two original endpoints. Llama and Mistral both "
        "rose on implicit alignment from low to high temperature. Qwen fell.",
    )

    set_para(
        doc,
        146,
        "Temperature may shift gendered wording without changing stereotype-aligned rates enough to "
        "show a clear tier interaction. The wider grid made the implicit wording shift visible. It "
        "did not settle whether prompt tier moderates temperature on binary alignment.",
    )

    set_para(
        doc,
        148,
        "Prompt specificity had a clear effect on which type of bias appeared. As shown in Figure 5, "
        "explicit prompts produced 0.0 percent direct stereotype language. Semi-explicit and implicit "
        "prompts both produced about 60 percent stereotype-aligned defaulting, well above chance.",
    )

    set_para(
        doc,
        151,
        "Model identity was a stronger predictor of demographic defaulting than hyperparameter "
        "settings. Mistral 7B showed 68.3 percent defaulting on implicit and semi-explicit prompts "
        "combined. Qwen 2.5 7B showed 58.6 percent. Llama 3.1 8B showed 54.5 percent.",
    )

    set_para(
        doc,
        158,
        "Scale and hyperparameter coverage. The gender grid was extended to six temperature values at "
        "nucleus sampling probability 1.0 and two nucleus sampling values at temperature 1.0. The "
        "grid was 94 percent complete (854 of 910 targeted new gender stories). Implicit alignment "
        "rates at intermediate temperatures were not strictly monotonic. A still wider sweep may be "
        "needed for binary outcomes.",
    )

    set_para(
        doc,
        165,
        "This paper asked whether temperature and stereotype generation interact with prompt specificity. "
        "The gender dataset used six temperature values. Female marker proportion fell with temperature "
        "for implicit prompts. Stereotype-aligned rates did not show a clean tier-specific temperature "
        "pattern. Explicit prompts stayed near 14 percent across conditions. Prompt framing remains "
        "the strongest factor.",
    )

    set_para(
        doc,
        166,
        "Three models that passed an explicit-bias test at about 14 percent stereotype alignment all "
        "produced implicit and semi-explicit defaulting near 60 percent. The role of nurse was assigned "
        "a female protagonist in 100 percent of classifiable implicit stories. Surgeon and mechanical "
        "engineer showed low stereotype alignment despite male-stereotyped roles. These patterns held "
        "across all three models.",
    )

    set_para(
        doc,
        167,
        "Instruction-tuned models suppressed explicit discriminatory language while retaining demographic "
        "associations in character framing. A fairness audit that only scans for explicit bias would "
        "report near-zero rates and conclude the models are unbiased. The tiered framework showed that "
        "conclusion was wrong. Temperature and nucleus sampling did little to move the roughly 60 percent "
        "implicit defaulting rate. The extended grid showed that implicit prompts still shift in gendered "
        "wording across temperature.",
    )

    set_para(
        doc,
        168,
        "Three directions remain for future work. First, complete the remaining gender grid cells. "
        "Second, extend the tiered framework to the race, age, and occupation dimensions. Third, "
        "compare model families on why Mistral defaulting rates exceed Llama and Qwen.",
    )

    doc.save(PATH)
    print("Saved", PATH)


if __name__ == "__main__":
    main()
