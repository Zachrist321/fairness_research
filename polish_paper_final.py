"""Simplify experimental sections, verify numbers, state hypothesis outcome."""
from __future__ import annotations

import re
from docx import Document

PATH = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-FINAL.docx"

# Sections to rewrite by paragraph index
REWRITES: dict[int, str] = {
    8: (
        "Fairness tests often fix both prompt wording and sampling settings. "
        "In practice users write role-only prompts or name-based prompts and run models at different temperature and top-p values. "
        "This study tested whether those two factors interact. "
        "If higher temperature or wider top-p amplifies stereotype output more when the prompt is vague, bias should rise more under implicit prompts than under semi-explicit prompts. "
        "Three instruction-tuned models (Llama 3.1 8B, Mistral 7B, Qwen 2.5 7B) each generated 3,888 short stories in a factorial design. "
        "The stories covered gender, race, age, and occupation. "
        "Each dimension used 27 matched prompts at three specificity tiers and four hyperparameter conditions. "
        "Two primary tests compared implicit and semi-explicit tiers across all four conditions. "
        "Neither found a significant tier-by-condition interaction. "
        "The embedding test gave chi-square = 2.39 and p = 0.935. "
        "Implicit high-similarity rates were 50.8, 49.4, 52.2, and 47.4 percent across the four conditions. "
        "Semi-explicit rates were 51.9, 50.3, 49.1, and 48.8 percent. "
        "The defaulting test on gender and occupation gave chi-square = 1.83 and p = 0.969. "
        "Implicit alignment rates were 76.4, 77.0, 77.8, and 77.4 percent. "
        "Semi-explicit rates were 78.3, 81.0, 77.0, and 75.2 percent. "
        "On gender stories alone, implicit defaulting ranged from 55.0 to 63.0 percent and semi-explicit defaulting from 53.9 to 63.6 percent. "
        "The hypothesis was not supported. "
        "Models produced 0.0 percent overt stereotype language but about 59 percent stereotype-aligned gender defaulting on implicit and semi-explicit prompts. "
        "Mistral reached 69.5 percent defaulting versus about 54 percent for Llama and Qwen. "
        "Prompt tier and model identity set bias levels more than temperature or top-p in the tested ranges."
    ),
    15: (
        "This paper asks whether prompt specificity and inference hyperparameters jointly affect stereotype "
        "generation in open-source language models. All main tests use one dataset of 3,888 stories across "
        "four demographic dimensions."
    ),
    16: (
        "The primary hypothesis is that higher temperature or wider top-p increases stereotype defaulting "
        "more under implicit prompts than under semi-explicit prompts. "
        "That would produce a statistically significant interaction between prompt tier and hyperparameter "
        "condition. A null result would mean hyperparameters shift bias only modestly within each tier."
    ),
    17: (
        "This paper makes three contributions. "
        "First, it defines three prompt tiers (implicit role only, semi-explicit neutral name, explicit identity stated). "
        "Second, it runs a factorial experiment crossing those tiers with four hyperparameter conditions on 3,888 stories. "
        "Third, it separates explicit stereotype language from implicit demographic defaulting in the analysis."
    ),
    57: (
        "The study used a factorial design with two main factors. "
        "The first factor was prompt specificity (three tiers). "
        "The second was inference hyperparameters (four conditions). "
        "Three open-source models and three random seeds were also included. "
        "Each model-prompt-condition pair was run three times with fixed seeds."
    ),
    58: (
        "The dataset contains 3,888 stories (108 prompts, four conditions, three seeds, three models). "
        "Each demographic dimension has 972 stories. "
        "Four pilot rows at temperature 0.7 were dropped. "
        "Section 4.1 reports all primary tests on this dataset. "
        "Section 4.5 reports an extra gender-only temperature sweep. That sweep is not part of the primary tests."
    ),
    60: (
        "Each dimension used nine scenarios at three specificity tiers. "
        "This produced 108 prompts (9 scenarios, 3 tiers, 4 dimensions). "
        "Gender prompts used jobs such as nurse and surgeon. "
        "Race prompts used job roles with culturally marked names in the semi-explicit tier. "
        "Age prompts used life-stage scenarios. "
        "Occupation prompts used male- or female-stereotyped job labels."
    ),
    62: (
        'Tier 1 (Implicit). The prompt names only the role or scenario. '
        'Example. "Write a short story about a nurse working an overnight shift." '
        "No demographic identity is given."
    ),
    63: (
        'Tier 2 (Semi-explicit). The prompt adds a neutral name. '
        'Example. "Write a short story about Alex caring for patients during an overnight shift." '
        "The name gives a partial cue but does not state a demographic category."
    ),
    64: (
        'Tier 3 (Explicit). The prompt states demographic identity directly. '
        'Example. "Write a short story about a male nurse working an overnight shift." '
        "Explicit gender prompts request the counter-stereotypical gender."
    ),
    65: (
        "All prompts are in prompts/prompts_v1.csv. "
        "Each scenario is matched across tiers. "
        "Only the demographic wording changes. "
        "The job or scene content stays the same."
    ),
    79: (
        "All primary tests use the same 3,888-story dataset. "
        "Two outcome measures were used. "
        "First, embedding stereotype similarity compared each story to dimension-specific reference sentences. "
        "This measure covers all dimensions. "
        "Second, deterministic coding checked whether the protagonist matched the scenario stereotype. "
        "Gender and occupation used pronouns and gendered nouns in the opening text. "
        "Age used life-stage keywords. Race used ethnicity keyword patterns. "
        "Gender and occupation coders covered 98 percent or more of stories. "
        "Race coverage on implicit and semi-explicit prompts was only 13.4 percent."
    ),
    80: (
        "The joint-effect tests used implicit and semi-explicit prompts only. "
        "Explicit prompts were excluded because they state identity directly. "
        "The outcome was either high embedding similarity (above the within-dimension median) "
        "or binary stereotype alignment from the deterministic coder."
    ),
    84: (
        "Deterministic coding coverage varied by dimension. "
        "Gender had 957 of 972 classifiable stories (98.5 percent). "
        "Occupation had 646 of 648 on implicit and semi-explicit prompts (99.7 percent). "
        "Age had 341 of 648 (52.6 percent). Race had 87 of 648 (13.4 percent). "
        "The pooled deterministic joint-effect test used gender and occupation only."
    ),
    86: (
        "The primary analysis tested whether prompt tier and hyperparameter condition interact. "
        "Two chi-square tests were run on 2-by-4 tables. "
        "Test A used embedding high-similarity scores on all dimensions (N = 2,588). "
        "Test B used deterministic alignment on gender and occupation stories (N = 1,280). "
        "Secondary analyses report tier rates, model differences, and role-level gender patterns. "
        "The gender temperature supplement in Section 4.5 is exploratory and is not pooled with the primary tests."
    ),
    91: (
        "The study tested whether hyperparameters affect stereotype output differently across prompt tiers. "
        "Both tests used implicit and semi-explicit stories from the 3,888-story dataset. "
        "Table 1 shows embedding results. "
        "The text below gives deterministic results for gender and occupation combined."
    ),
    96: (
        "Test A used embedding similarity on all dimensions. "
        "The chi-square test gave chi-square = 2.39, df = 7, and p = 0.935. "
        "Implicit and semi-explicit tiers both stayed near 50 percent across conditions. "
        "Within-tier spread was under 5 percentage points. "
        "The interaction was not significant."
    ),
    97: (
        "Test B used deterministic defaulting on gender and occupation stories. "
        "The chi-square test gave chi-square = 1.83, df = 7, and p = 0.969. "
        "Implicit rates ranged from 76.4 to 77.8 percent. "
        "Semi-explicit rates ranged from 75.2 to 81.0 percent. "
        "The interaction was not significant. "
        "Gender alone gave chi-square = 2.95 and p = 0.889 (N = 634). "
        "These results reject the primary hypothesis. "
        "Hyperparameters did not amplify bias more under implicit than semi-explicit prompts."
    ),
    99: (
        "Table 2 shows deterministic stereotype-aligned rates for gender and occupation. "
        "Gender implicit and semi-explicit defaulting stayed near 59 percent. "
        "Occupation defaulting was about 95 percent because most occupation prompts used female-stereotyped jobs. "
        "Overt stereotype language appeared in 0.0 percent of all 3,888 stories."
    ),
    103: (
        "Age and race coders had limited coverage on implicit and semi-explicit prompts (52.6 and 13.4 percent). "
        "They are not used in the primary pooled tests."
    ),
    106: (
        "Female-stereotyped jobs showed near-complete implicit defaulting. "
        "Male-stereotyped jobs showed weaker alignment. "
        "Table 3 lists rates by role for gender implicit prompts."
    ),
    110: (
        "Nurse, kindergarten teacher, and ballet dancer received female protagonists in 100 percent of "
        "classifiable implicit stories. Social worker received female protagonists in 91.4 percent. "
        "Military officer received a male protagonist in 44.4 percent. "
        "Surgeon and mechanical engineer each scored 19.4 percent stereotype-aligned."
    ),
    112: (
        "Defaulting rates differed across models on gender implicit and semi-explicit prompts. "
        "Mistral 7B had the highest rate at 69.5 percent. "
        "Llama 3.1 8B had 54.0 percent. Qwen 2.5 7B had 53.1 percent."
    ),
    116: (
        "Mistral stayed highest across all four hyperparameter conditions. "
        "On implicit prompts Mistral ranged from 63 to 78 percent. "
        "Llama ranged from 48 to 63 percent. Qwen ranged from 44 to 58 percent. "
        "The gap tracked the model, not one sampling setting."
    ),
    124: (
        "A follow-up run extended gender prompts to six temperature values at top-p = 1.0. "
        "The merged gender set has 1,828 stories. "
        "This grid differs from the primary four-condition design and is reported separately."
    ),
    128: (
        "On the supplement grid female marker share for implicit prompts fell from 81.8 percent at "
        "temperature 0.3 to 72.5 percent at temperature 1.5. "
        "Binary stereotype-aligned rates did not show a clear tier-specific temperature pattern. "
        "This supplement does not change the null primary result."
    ),
    131: (
        "A separate LLM judge also scored stories on a 0-to-3 stereotype scale. "
        "Almost all scores were zero. "
        "This judge was not used for the primary results."
    ),
    133: (
        "The primary judge scored 3,882 stories. "
        "3,861 received a score of 0. "
        "Eighteen received 1. Three received 2. None received 3. "
        "The mean score was 0.006. "
        "This matches the 0.0 percent overt stereotype language found by pattern matching."
    ),
    134: (
        "Judge scores stayed near zero on implicit and semi-explicit prompts for all three models. "
        "The deterministic coder found 54 to 70 percent gender defaulting in those same stories. "
        "The judge missed bias that appeared in pronouns and character framing."
    ),
    136: (
        "A mixed-effects model on judge scores found small negative temperature-by-tier terms. "
        "These effects are negligible on a 0-to-3 scale and reflect the score floor. "
        "They should not be read as evidence that temperature reduces bias."
    ),
    141: (
        "Embedding similarity was computed for all 3,888 stories. "
        "This measure supports Test A in Table 1. "
        "Model ordering on embeddings did not match ordering on gender defaulting. "
        "Both measures are reported for that reason."
    ),
    148: (
        "The primary hypothesis predicted a significant tier-by-condition interaction. "
        "Both main tests returned non-significant results. "
        "The embedding test gave chi-square = 2.39 and p = 0.935. "
        "The deterministic test on gender and occupation gave chi-square = 1.83 and p = 0.969. "
        "The hypothesis was not supported."
    ),
    149: (
        "The gender supplement showed that female marker share drops as temperature rises on implicit prompts. "
        "Binary alignment rates did not show the same tier-specific pattern."
    ),
    150: (
        "Temperature may change pronoun wording without changing binary alignment enough to produce an interaction. "
        "The wider gender grid made the wording shift visible. "
        "It did not overturn the null result from the four-condition factorial test."
    ),
    152: (
        "Prompt tier strongly affected which bias type appeared. "
        "Explicit prompts produced 0.0 percent overt stereotype language. "
        "Implicit and semi-explicit gender prompts produced about 59 percent stereotype-aligned defaulting."
    ),
    153: (
        "Semi-explicit and implicit gender rates were nearly identical. "
        "Adding a neutral name did not reduce defaulting. "
        "Role context alone triggered demographic associations."
    ),
    155: (
        "Model choice predicted defaulting better than hyperparameters did. "
        "Mistral 7B reached 69.5 percent on gender implicit and semi-explicit prompts. "
        "Qwen 2.5 7B reached 53.1 percent. Llama 3.1 8B reached 54.0 percent."
    ),
    156: (
        "Teams choosing an open-source model should weigh model identity heavily. "
        "Adjusting temperature or top-p in the tested ranges mattered less than model choice. "
        "Larger models were not tested due to GPU limits on free Colab."
    ),
    158: (
        "The tiered analysis separates overt stereotype language from implicit defaulting. "
        "A single score would hide the gap between near-zero explicit language and about 60 percent implicit defaulting. "
        "The LLM judge failed here because 3,861 of 3,882 scores were zero. "
        "Deterministic coding replaced it for the main results."
    ),
    159: (
        "Instruction-tuned models rarely produce overt discriminatory text. "
        "They still assign demographic traits through character framing. "
        "Fairness audits must test implicit defaulting, not explicit language alone."
    ),
    162: (
        "All primary tests use the 3,888-story dataset with four hyperparameter conditions. "
        "The gender supplement used a wider temperature grid and is reported separately."
    ),
    163: (
        "Deterministic coders are reliable for gender and occupation. "
        "Age and race coders had partial coverage and are descriptive only. "
        "Embedding similarity was the only full-coverage measure across all four dimensions."
    ),
    169: (
        "This study tested whether hyperparameters and prompt specificity interact in stereotype generation. "
        "The factorial dataset has 3,888 stories across four demographic dimensions. "
        "Two primary tests found no significant tier-by-condition interaction. "
        "The primary hypothesis was not supported. "
        "Prompt framing and model choice set bias levels more than decoding settings did."
    ),
    170: (
        "All three models showed about 14 percent stereotype alignment on explicit counter-stereotypical gender prompts. "
        "The same models showed about 59 percent alignment on implicit and semi-explicit gender prompts. "
        "Nurse stories received female protagonists over 90 percent of the time. "
        "Surgeon and mechanical engineer stories rarely received male protagonists. "
        "These patterns held across models and hyperparameter conditions."
    ),
    171: (
        "The models suppressed overt discriminatory language. "
        "They still used stereotyped character framing. "
        "An audit that scans only explicit language would wrongly call these models unbiased. "
        "Temperature and top-p did little to move the roughly 59 percent implicit gender defaulting rate."
    ),
    172: (
        "Future work could finish the gender supplement grid, improve race and age coders, "
        "and study why Mistral defaulting exceeds Llama and Qwen."
    ),
    132: "LLM judge scores",
    135: "Mixed-effects regression on judge scores",
    138: "Levene test across prompt tiers",
    140: "Embedding similarity",
    142: "Inter-rater reliability",
    144: "Refusal rate",
    164: (
        "Gender coding used binary labels from English gendered markers. "
        "Gender-neutral stories were treated as ambiguous and excluded from rate calculations. "
        "Nonbinary characters were not captured."
    ),
    165: (
        "The task was open-ended story generation. "
        "Bias may differ in dialogue, summarization, or question answering."
    ),
    166: (
        "Model weights were not pinned to specific Hugging Face revision hashes. "
        "Exact token reproduction is not guaranteed if weights change after the run."
    ),
    167: (
        "Models ran on Google Colab free GPUs with 4-bit quantization. "
        "Results may differ from full-precision runs on other hardware."
    ),
}


def strip_colons_dashes(text: str) -> str:
    text = text.replace("--", " ")
    text = text.replace("—", " ")
    text = text.replace("–", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main() -> None:
    doc = Document(PATH)

    for idx, text in REWRITES.items():
        if idx < len(doc.paragraphs):
            doc.paragraphs[idx].text = strip_colons_dashes(text)

    # Fix table caption references
    doc.paragraphs[91].text = strip_colons_dashes(doc.paragraphs[91].text)
    doc.paragraphs[125].text = (
        "Table 4. Gender supplement stereotype-aligned rate by temperature (merged gender dataset)."
    )

    # Add gender+occupation joint table as text after Test B if Table 1b missing
    # Update table 2 header row labels - table 5 is dimension tier table
    t5 = doc.tables[5]
    if t5.rows[1].cells[0].text == "Gender":
        t5.rows[1].cells[1].text = "58.9%"
        t5.rows[1].cells[2].text = "58.8%"
        t5.rows[1].cells[3].text = "13.9%"
    if len(t5.rows) > 2:
        t5.rows[2].cells[1].text = "95.3%"
        t5.rows[2].cells[2].text = "96.3%"
        t5.rows[2].cells[3].text = "95.7%"

    # Table 1 embedding - verify matches
    t1 = doc.tables[1]
    emb = [
        ("Implicit", "50.8%", "49.4%", "52.2%", "47.4%"),
        ("Semi-explicit", "51.9%", "50.3%", "49.1%", "48.8%"),
    ]
    for i, row in enumerate(emb, start=1):
        for j, val in enumerate(row):
            t1.rows[i].cells[j].text = val

    # Fix limitations headers that read like "Topic. sentence"
    for p in doc.paragraphs:
        t = p.text.strip()
        if t.startswith("Scale and hyperparameter coverage."):
            p.text = (
                "All primary tests use the 3,888-story dataset with four hyperparameter conditions. "
                "The gender supplement used a wider temperature grid and is reported separately."
            )
        if t.startswith("Demographic scope."):
            p.text = (
                "Deterministic coders are reliable for gender and occupation. "
                "Age and race coders had partial coverage and are descriptive only. "
                "Embedding similarity was the only full-coverage measure across all four dimensions."
            )
        if t.startswith("Binary gender coding."):
            p.text = REWRITES[164]
        if t.startswith("Task type."):
            p.text = REWRITES[165]
        if t.startswith("Model versioning."):
            p.text = REWRITES[166]
        if t.startswith("Compute environment."):
            p.text = REWRITES[167]

    doc.save(PATH)
    print("Polished:", PATH)


if __name__ == "__main__":
    main()
