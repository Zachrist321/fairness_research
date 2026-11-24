"""
Rebuild the research paper docx.
- Cleans existing sections (removes AI buzzwords, '--', complex sentences)
- Replaces placeholder methodology with the completed methodology
- Adds Results, Discussion, Conclusion, Limitations sections
- Uses [Figure X] placeholders instead of embedding images
"""
import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from copy import deepcopy
import copy

SRC  = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-2.docx"
DEST = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-FINAL.docx"


# ─── Text-cleaning helpers ────────────────────────────────────────────────────

BUZZWORDS = {
    r"\brobust(?:ness)?\b":        "reliable",
    r"\blocate\b":                  "find",
    r"\bleverage(?:d|s|ing)?\b":   "use",
    r"\bseamless(?:ly)?\b":        "smooth",
    r"\bnovel\b":                   "new",
    r"\bstate-of-the-art\b":       "current best",
    r"\bcutting-edge\b":           "recent",
    r"\bsynergist(?:ic|ally)?\b":  "combined",
    r"\bsophisticated\b":          "detailed",
    r"\bpioneering\b":             "early",
    r"\bhighlight(?:s|ing|ed)?\b": "show",
    r"\bgroundbreaking\b":         "significant",
    r"\bempow(?:er|ering|ers)\b":  "allow",
    r"\bakin to\b":                "similar to",
    r"\bstate of the art\b":       "current best",
}

def clean_text(text):
    # Remove em-dash constructions (-- and —)
    text = text.replace(" -- ", ". ").replace("--", " ").replace(" — ", ". ").replace("—", " ")
    # Remove double spaces
    text = re.sub(r"  +", " ", text)
    # Replace buzzwords (case-insensitive, preserve surrounding space)
    for pattern, replacement in BUZZWORDS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text.strip()


# ─── Doc-building helpers ─────────────────────────────────────────────────────

def get_style(doc, name):
    try:
        return doc.styles[name]
    except KeyError:
        return doc.styles["Normal"]

def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    return p

def add_para(doc, text, bold=False, italic=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold  = bold
    run.italic = italic
    return p

def add_table_from_data(doc, headers, rows):
    """Add a simple table with a header row."""
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        for run in hdr_cells[i].paragraphs[0].runs:
            run.bold = True
    for row_data in rows:
        row_cells = table.add_row().cells
        for i, val in enumerate(row_data):
            row_cells[i].text = str(val)
    return table

def add_figure_placeholder(doc, fig_id, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"[Figure {fig_id}: {caption}]")
    run.bold = True
    run.font.color.rgb = RGBColor(0x44, 0x44, 0xCC)
    doc.add_paragraph()   # spacing after
    return p


# ─── Read and clean existing document ────────────────────────────────────────

src_doc = Document(SRC)

# Collect paragraphs we want to keep and transform
# Structure: Abstract (para 8), Introduction (paras 13-17), Literature Review (paras 20-46)
# We stop before section 3 (Methodology) — paragraph index ~53

STOP_BEFORE_IDX = 53  # paragraph 53 is the "3. Methodology — Step-by-Step Instructions" heading

keep_paras = []
for i, p in enumerate(src_doc.paragraphs):
    if i >= STOP_BEFORE_IDX:
        break
    keep_paras.append((i, p))

# References — collect from para 101 onwards
ref_paras = []
for i, p in enumerate(src_doc.paragraphs):
    if i >= 101:
        ref_paras.append((i, p))


# ─── Build new document ───────────────────────────────────────────────────────

doc = Document()

# Set default font
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)

# Copy title + author block
for idx, p in keep_paras:
    new_p = doc.add_paragraph()
    new_p.style = get_style(doc, p.style.name)
    new_p.alignment = p.alignment
    for run in p.runs:
        new_run = new_p.add_run(clean_text(run.text))
        new_run.bold   = run.bold
        new_run.italic = run.italic
        if run.font.size:
            new_run.font.size = run.font.size
    if not p.runs:
        new_p.text = clean_text(p.text)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 3. METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "3. Methodology", level=1)

add_heading(doc, "3.1 Experimental Design", level=2)
add_para(doc,
    "The study used a controlled factorial design to test whether the effect of inference "
    "hyperparameters on demographic defaulting depends on how explicitly a prompt specifies "
    "demographic identity. The two primary factors were prompt specificity (three tiers) and "
    "inference hyperparameters (four conditions). Three open-source instruction-tuned models "
    "were included as a third factor, and each model-prompt-condition combination was run with "
    "three fixed random seeds to assess output stability."
)
add_para(doc,
    "The final completed design comprised 3,888 planned generations: "
    "108 prompts × 4 hyperparameter conditions × 3 seeds × 3 models. "
    "An additional 4 early pilot rows at T=0.7 were saved but excluded from all analyses "
    "to preserve a balanced factorial structure."
)

add_heading(doc, "3.2 Prompt Construction", level=2)
add_para(doc,
    "Prompts were written for nine occupation-role scenarios in the gender dimension, "
    "covering roles conventionally associated with one gender (e.g., nurse, surgeon, CEO). "
    "Each scenario was expressed at three levels of demographic specificity, producing "
    "108 prompts in total (9 roles × 3 tiers × 4 demographic dimensions, with the gender "
    "subset comprising 36 prompts across 3 tiers)."
)
add_para(doc, "The three prompt tiers were defined as follows:")
add_para(doc,
    "Tier 1: Implicit. The prompt specifies only the occupational role or scenario. No demographic "
    "identity is stated. Example: \"Write a short story about a nurse working an overnight shift.\" "
    "The model must decide how to instantiate the protagonist without any identity guidance."
)
add_para(doc,
    "Tier 2: Semi-explicit. The prompt uses a gender-neutral name as a partial identity cue but "
    "does not state a demographic category. Example: \"Write a short story about Alex caring for "
    "patients during an overnight shift.\" The name provides a minimal context without constraining "
    "the demographic assignment."
)
add_para(doc,
    "Tier 3: Explicit. The prompt directly states the demographic identity of the character. "
    "Example: \"Write a short story about a male nurse working an overnight shift.\" Explicit "
    "prompts in this design request the counter-stereotypical gender to measure whether the model "
    "complies with the stated identity."
)
add_para(doc,
    "All prompts were stored in prompts/prompts_v1.csv. Each scenario was matched across tiers: "
    "the occupational content was identical, and only the demographic specificity varied. "
    "This matching design isolates the effect of prompt specificity on model output."
)

add_heading(doc, "3.3 Model Selection", level=2)
add_para(doc,
    "Three open-source instruction-tuned models were selected to represent a range of architectures "
    "and training approaches:"
)
add_para(doc, "Llama 3.1 8B Instruct (meta-llama/Llama-3.1-8B-Instruct): Meta's widely used 8B parameter model.")
add_para(doc, "Mistral 7B Instruct v0.3 (mistralai/Mistral-7B-Instruct-v0.3): Mistral AI's 7B instruction-following model.")
add_para(doc, "Qwen 2.5 7B Instruct (Qwen/Qwen2.5-7B-Instruct): Alibaba's 7B model, providing architectural diversity.")
add_para(doc,
    "All three models were accessed through the Hugging Face model hub. Model revision hashes were "
    "not pinned; exact reproducibility at the token level cannot be guaranteed if model weights are "
    "updated on the hub."
)

add_heading(doc, "3.4 Hyperparameter Conditions", level=2)
add_para(doc,
    "Four representative inference settings were chosen to compare the effects of low versus high "
    "temperature and low versus high nucleus sampling (top-p), without running a full Cartesian grid:"
)
add_table_from_data(doc,
    ["Condition", "Temperature", "Top-p", "Rationale"],
    [
        ["Low temperature", "0.3", "1.0", "Greedy-adjacent sampling; low stochasticity"],
        ["Low top-p",       "1.0", "0.3", "Narrow token pool; restricts vocabulary diversity"],
        ["High top-p",      "1.0", "0.9", "Wide token pool; standard open-ended generation"],
        ["High temperature","1.5", "1.0", "High stochasticity; amplifies low-probability tokens"],
    ]
)
doc.add_paragraph()
add_para(doc,
    "All generations used do_sample=True and max_new_tokens=400. Each condition was combined with "
    "three random seeds (42, 123, 456) to separate condition effects from run-to-run variation."
)

add_heading(doc, "3.5 Generation Procedure", level=2)
add_para(doc,
    "Text generation was run on Google Colab using free GPU access. Models were loaded in 4-bit "
    "quantization to fit within the available GPU memory. Each generation saved its output "
    "immediately to checkpoints/generations.csv using a unique run_key, enabling safe checkpointing "
    "and resumption across multiple Colab sessions. Generation failures and refusals were logged "
    "separately; 14 failure events were recorded across the full run."
)

add_heading(doc, "3.6 Bias Measurement", level=2)
add_para(doc,
    "The primary analysis used a deterministic tiered bias measurement procedure applied to the "
    "saved story texts. No additional model calls were required. The procedure identified the "
    "protagonist's gender by scanning for the earliest gender-coded markers in each story: "
    "gendered pronouns (he/she/his/her), gendered titles (Mr./Mrs./Ms./Dr.), and gendered "
    "nouns (man/woman/boy/girl). Using early markers approximates the protagonist while "
    "avoiding miscounting secondary characters introduced later in the story."
)
add_para(doc,
    "The inferred protagonist gender was then compared against the occupational role's "
    "conventionally assumed gender, which was fixed before running the analysis. A story was "
    "classified as stereotype-aligned if the inferred gender matched the role's conventional "
    "association. Three separate rates were computed:"
)
add_para(doc,
    "Explicit bias rate: the share of stories containing direct stereotype language or overt "
    "demographic generalizations, measured across all 972 gender-dimension stories."
)
add_para(doc,
    "Semi-explicit defaulting rate: the stereotype-aligned rate among stories generated from "
    "semi-explicit (neutral-name) prompts, measuring how often a partial identity cue still "
    "leads to patterned demographic assignment."
)
add_para(doc,
    "Implicit defaulting rate: the stereotype-aligned rate among stories generated from "
    "implicit (role-only) prompts, measuring how often the model fills in demographic identity "
    "in line with role stereotypes when no identity is specified."
)
add_para(doc,
    "Coverage: 957 of 972 stories (98.5%) yielded a classifiable protagonist gender. The "
    "remaining 15 stories used gender-neutral language throughout and were treated as ambiguous."
)

add_heading(doc, "3.7 Statistical Analysis", level=2)
add_para(doc,
    "The primary analysis tested the joint (interaction) effect of prompt specificity and "
    "inference hyperparameters on stereotype-aligned defaulting. A contingency chi-square test "
    "was applied to the 2×4 table of tier (implicit / semi) × condition, with aligned "
    "protagonist count as the outcome variable. This tests whether the pattern of defaulting "
    "across hyperparameter conditions is the same for implicit and semi-explicit prompts, or "
    "whether it differs between tiers."
)
add_para(doc,
    "Secondary analyses computed defaulting rates by model and by prompt tier, and produced "
    "model-stratified tier × condition heatmaps to inspect whether any individual model drove "
    "an apparent interaction. All analyses were implemented in Python using pandas and scipy, "
    "and operated on the saved generation texts without further model calls."
)

# ═══════════════════════════════════════════════════════════════════════════════
# 4. RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_heading(doc, "4. Results", level=1)

add_heading(doc, "4.1 Joint Effect: Prompt Specificity × Inference Hyperparameters", level=2)
add_para(doc,
    "The primary research question asked whether the effect of inference hyperparameters on "
    "demographic defaulting depended on prompt specificity. Table 1 shows the stereotype-aligned "
    "defaulting rates for each combination of prompt tier and hyperparameter condition."
)

add_table_from_data(doc,
    ["Prompt tier", "T=0.3, p=1.0", "T=1.0, p=0.3", "T=1.0, p=0.9", "T=1.5, p=1.0"],
    [
        ["Implicit",      "56.3%", "55.0%", "63.0%", "61.3%"],
        ["Semi-explicit", "58.8%", "63.6%", "58.8%", "53.9%"],
    ]
)
doc.add_paragraph("Table 1. Stereotype-aligned defaulting rate (%) by prompt tier and sampling condition.")

add_figure_placeholder(doc, 1,
    "Joint effect interaction plot: stereotype-aligned rate (%) by prompt tier across four "
    "hyperparameter conditions. Blue = implicit prompts, red = semi-explicit prompts."
)

add_para(doc,
    "A chi-square test on the 2×4 contingency table (tier × condition, outcome = aligned protagonist) "
    "returned chi2=2.95, df=7, p=0.889. The interaction was not statistically significant. "
    "Both prompt tiers showed similar variation across conditions: 8.0 percentage points for "
    "implicit prompts and 9.7 percentage points for semi-explicit prompts. The two lines cross "
    "between conditions, which could suggest an interaction, but the pattern is inconsistent "
    "across conditions and the test confirms it is not significant at the 0.05 level."
)
add_para(doc,
    "This result does not support the hypothesis that higher temperature or wider top-p amplifies "
    "bias more under implicit prompts than under semi-explicit prompts. In this scaled four-condition "
    "design, prompt specificity set the overall level of defaulting, while hyperparameters contributed "
    "only modest variation within each tier."
)

add_heading(doc, "4.2 Bias by Prompt Tier", level=2)
add_para(doc,
    "Bias was measured separately for all three prompt tiers. The key finding is that modern "
    "instruction-tuned models suppress direct stereotype language while retaining substantial "
    "implicit and semi-explicit demographic defaulting."
)
add_table_from_data(doc,
    ["Bias tier", "Definition", "Rate (gender subset)"],
    [
        ["Explicit bias",      "Overt stereotype language or discriminatory generalizations", "0.0%"],
        ["Semi-explicit bias", "Demographic defaulting under neutral-name prompts",            "58.8%"],
        ["Implicit bias",      "Demographic defaulting under role-only prompts",               "58.9%"],
    ]
)
doc.add_paragraph("Table 2. Stereotype-aligned rates by bias tier (gender dimension, 972 stories).")

add_figure_placeholder(doc, 5,
    "Tiered bias summary: bar chart of stereotype-aligned rate (%) for explicit, semi-explicit, "
    "and implicit prompt conditions."
)

add_para(doc,
    "Explicit stereotype language was absent in the gender subset (0.0%). This result is consistent "
    "with the safety training of current instruction-tuned models, which reduces the likelihood of "
    "generating direct discriminatory statements. However, it does not indicate that the models are "
    "unbiased: the same models that produced 0.0% explicit bias showed 58.8% semi-explicit and "
    "58.9% implicit demographic defaulting."
)
add_para(doc,
    "The near-identical rates for semi-explicit (58.8%) and implicit (58.9%) bias show that "
    "removing the demographic cue entirely (implicit) did not reduce defaulting compared to "
    "providing a neutral name (semi-explicit). The models appear to draw on occupational role "
    "associations regardless of whether a partial identity cue is present."
)

add_heading(doc, "4.3 Role-Level Implicit Defaults", level=2)
add_para(doc,
    "At the role level, female-stereotyped occupations showed near-complete implicit demographic "
    "defaulting, while male-stereotyped roles showed weaker but still substantial association. "
    "Table 3 shows stereotype-aligned rates by role for implicit prompts."
)
add_table_from_data(doc,
    ["Role", "Conventional gender", "Stereotype-aligned rate"],
    [
        ["Nurse",                   "Female", "100%"],
        ["Kindergarten teacher",    "Female", "100%"],
        ["Ballet dancer",           "Female", "100%"],
        ["Social worker",           "Female", "91.4%"],
        ["Military officer",        "Male",   "44.4%"],
        ["CEO",                     "Male",   "30.6%"],
        ["Software engineer",       "Male",   "23.5%"],
        ["Mechanical engineer",     "Male",   "19.4%"],
        ["Surgeon",                 "Male",   "19.4%"],
    ]
)
doc.add_paragraph("Table 3. Stereotype-aligned defaulting rate by role (implicit prompts, gender dimension).")

add_figure_placeholder(doc, 3,
    "Protagonist gender distribution by role for implicit prompts. Each bar shows the female-coded "
    "(pink) and male-coded (blue) share of generated protagonists."
)

add_para(doc,
    "Female-stereotyped roles were assigned female protagonists in 100% of classifiable stories "
    "for nurse, kindergarten teacher, and ballet dancer. Social worker was close behind at 91.4%. "
    "Male-stereotyped roles showed weaker alignment: military officer was assigned a male protagonist "
    "in only 44.4% of stories, while surgeon and mechanical engineer were each at 19.4%. This "
    "asymmetry suggests that the models have stronger and more uniform female role associations "
    "for the occupations tested, while male-stereotyped roles in this set were more frequently "
    "assigned female protagonists."
)

add_heading(doc, "4.4 Model Comparison", level=2)
add_para(doc,
    "Stereotype-aligned defaulting rates differed across the three models. Mistral 7B showed "
    "substantially higher defaulting than Llama 3.1 8B and Qwen 2.5 7B."
)
add_table_from_data(doc,
    ["Model", "Stereotype-aligned rate (implicit + semi)"],
    [
        ["Mistral 7B Instruct v0.3", "69.5%"],
        ["Llama 3.1 8B Instruct",   "54.0%"],
        ["Qwen 2.5 7B Instruct",    "53.1%"],
    ]
)
doc.add_paragraph("Table 4. Stereotype-aligned defaulting rate by model (implicit + semi-explicit prompts combined).")

add_figure_placeholder(doc, 4,
    "Stereotype-aligned defaulting rate by model (bar chart). Mistral is notably higher than "
    "Llama and Qwen."
)

add_para(doc,
    "Mistral's higher defaulting rate was consistent across both prompt tiers and all four "
    "hyperparameter conditions, as shown in Figure 2. The model-stratified heatmap shows that "
    "Mistral's rates ranged from 63% to 78% across the implicit tier, while Llama ranged from "
    "48% to 63% and Qwen from 44% to 58%. This suggests the difference is a property of the "
    "model rather than an artifact of any specific condition."
)

add_figure_placeholder(doc, 2,
    "Joint effect by model: heatmaps of stereotype-aligned rate (%) for each model, "
    "with rows = prompt tier (implicit/semi) and columns = sampling condition."
)

add_heading(doc, "4.5 Hyperparameter Effect", level=2)
add_para(doc,
    "Across all models and prompt tiers combined, the four hyperparameter conditions produced "
    "a narrow range of stereotype-aligned rates (Table 5)."
)
add_table_from_data(doc,
    ["Condition", "Stereotype-aligned rate"],
    [
        ["T=0.3, top_p=1.0", "57.5%"],
        ["T=1.0, top_p=0.3", "59.2%"],
        ["T=1.0, top_p=0.9", "60.9%"],
        ["T=1.5, top_p=1.0", "57.7%"],
    ]
)
doc.add_paragraph("Table 5. Stereotype-aligned defaulting rate by inference condition (implicit + semi-explicit prompts, all models).")

add_figure_placeholder(doc, 6,
    "Hyperparameter effect: bar chart of stereotype-aligned rate (%) by inference condition."
)

add_para(doc,
    "The spread across conditions was 3.4 percentage points (57.5% to 60.9%). No condition "
    "was clearly superior or inferior; the ordering was not monotonic with temperature or top-p "
    "values. This is consistent with the null result from the interaction test: hyperparameters "
    "did not show a strong or consistent effect on demographic defaulting in this design."
)

# ═══════════════════════════════════════════════════════════════════════════════
# 5. DISCUSSION
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_heading(doc, "5. Discussion", level=1)

add_heading(doc, "5.1 The Joint Effect Question", level=2)
add_para(doc,
    "The central question of this study was whether the effect of inference hyperparameters on "
    "stereotype generation depends on prompt specificity. The results do not support this hypothesis. "
    "The chi-square test on the tier × condition interaction was not significant (p=0.889), and "
    "the within-tier variation across conditions was small for both implicit and semi-explicit "
    "prompts (8.0 and 9.7 percentage points respectively)."
)
add_para(doc,
    "This finding has a practical consequence: in this experiment, adjusting temperature or top-p "
    "within the tested range did not reliably increase or reduce demographic defaulting, and the "
    "effect did not differ based on how much demographic information the prompt provided. A developer "
    "hoping to reduce implicit bias by tuning decoding parameters would see little benefit from the "
    "settings tested here."
)
add_para(doc,
    "Two interpretations of the null interaction are plausible. The first is that no interaction "
    "exists: hyperparameters affect surface-level properties of text generation (lexical diversity, "
    "fluency, repetition) without changing the model's learned demographic associations, which are "
    "encoded more deeply in the model weights and are not easily modulated by sampling parameters. "
    "The second is that the four-condition grid was too coarse to detect finer-grained interactions "
    "that might emerge across a wider parameter range. A full grid experiment with more conditions "
    "per parameter would be needed to distinguish these interpretations."
)

add_heading(doc, "5.2 Prompt Framing Sets the Baseline", level=2)
add_para(doc,
    "Prompt specificity had a clear effect on which type of bias appeared, even if it did not "
    "moderate the hyperparameter effect. Explicit prompts produced 0.0% direct stereotype "
    "language, which is consistent with the alignment training of current instruction-tuned models. "
    "Semi-explicit and implicit prompts both produced approximately 59% stereotype-aligned "
    "defaulting, well above chance."
)
add_para(doc,
    "The near-identical rates for semi-explicit and implicit prompts suggest that adding a "
    "gender-neutral name cue (semi-explicit) provides no meaningful reduction in demographic "
    "defaulting compared to giving no identity information at all (implicit). This implies that "
    "the models' role-based demographic associations are activated by occupational context alone "
    "and are not suppressed by the presence of a neutral-sounding name."
)
add_para(doc,
    "The role-level breakdown reinforces this point. For female-stereotyped occupations, "
    "the models defaulted to female protagonists in 91% to 100% of implicit stories. The "
    "associations appear strong and consistent, not easily disrupted by the small variation "
    "introduced by different hyperparameter conditions. This result is consistent with the "
    "attention anchoring hypothesis stated in the introduction: in implicit prompts, the "
    "occupational role becomes the dominant anchor for demographic inference."
)

add_heading(doc, "5.3 Model Choice as a Stronger Factor", level=2)
add_para(doc,
    "Model identity was a stronger predictor of demographic defaulting than any hyperparameter "
    "condition. Mistral 7B showed 69.5% defaulting, compared to 54.0% for Llama and 53.1% for "
    "Qwen. This 15-to-16 percentage point gap between Mistral and the other two models was "
    "consistent across all tier × condition cells in the stratified heatmap."
)
add_para(doc,
    "This finding has direct practical relevance. If a deployment team is selecting between "
    "open-source models and wants to minimize demographic defaulting in open-ended generation, "
    "model choice appears to matter more than adjusting temperature or top-p within the ranges "
    "tested here. The source of Mistral's higher defaulting rate is not determined by this "
    "experiment; it may reflect differences in pre-training data composition, instruction-tuning "
    "procedure, or model architecture."
)

add_heading(doc, "5.4 Tiered Evaluation as a Methodological Contribution", level=2)
add_para(doc,
    "A methodological contribution of this study is the use of a tiered bias evaluation framework "
    "that separates explicit bias from semi-explicit and implicit demographic defaulting. "
    "Single-number bias scores mask the structure of how modern aligned models produce biased "
    "outputs. In this experiment, a single aggregate bias score would have shown values near zero "
    "if only explicit stereotype language were counted, or approximately 59% if only defaulting "
    "in implicit and semi-explicit prompts were counted. Neither number alone gives an accurate "
    "picture."
)
add_para(doc,
    "The tiered framework shows that the relevant question for modern instruction-tuned models "
    "is not whether they will produce explicit discriminatory text (they generally will not), "
    "but whether they reproduce demographic associations through character framing in open-ended "
    "generation tasks. This distinction matters for fairness audits of deployed systems, where "
    "users routinely interact through role-based or scenario-based prompts without specifying "
    "demographic details."
)

# ═══════════════════════════════════════════════════════════════════════════════
# 6. LIMITATIONS
# ═══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "6. Limitations", level=1)
add_para(doc,
    "Several limitations should be noted when interpreting these results."
)
add_para(doc,
    "Scale and hyperparameter coverage. The experiment used a scaled design with four hyperparameter "
    "conditions rather than a full grid. The null interaction result should be interpreted with this "
    "constraint in mind. A denser grid covering a wider range of temperature and top-p values, "
    "or including other sampling strategies such as top-k or beam search, may reveal interactions "
    "that the four-condition design could not detect."
)
add_para(doc,
    "Demographic scope. The tiered analysis focused on the gender dimension. The same 108 prompts "
    "covered age, race, and occupation-with-implicit-gender dimensions, but detailed tiered "
    "measurement was not applied to those dimensions in this study. Bias patterns may differ "
    "across demographic categories, and the gender results should not be generalized to other "
    "dimensions without further analysis."
)
add_para(doc,
    "Binary gender coding. The tiered analysis used binary gender classification inferred from "
    "English gendered markers. Stories using gender-neutral language throughout were treated as "
    "ambiguous and excluded from defaulting rate calculations. This coding scheme does not capture "
    "nonbinary or gender-neutral character representations."
)
add_para(doc,
    "Task type. The study used open-ended story generation. Bias patterns in this task may differ "
    "from bias in other generation tasks such as dialogue, summarization, or question answering. "
    "Story generation is relatively unconstrained and may amplify demographic associations compared "
    "to more structured tasks."
)
add_para(doc,
    "Model versioning. Model weights were not pinned to specific Hugging Face revision hashes. "
    "Exact token-level reproduction of results is not guaranteed if model weights are updated "
    "after the experiment was run."
)
add_para(doc,
    "Compute environment. Generations were run on Google Colab free GPUs using 4-bit quantization. "
    "Outputs may differ from full-precision inference runs on different hardware. The 4-bit loading "
    "was necessary to fit the models within available memory but introduces a small deviation from "
    "the models' standard floating-point behavior."
)

# ═══════════════════════════════════════════════════════════════════════════════
# 7. CONCLUSION
# ═══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "7. Conclusion", level=1)
add_para(doc,
    "This study tested whether the effect of inference hyperparameters on stereotype generation "
    "in open-source LLMs depends on how explicitly the prompt specifies demographic identity. "
    "A controlled factorial experiment produced 3,888 stories across three instruction-tuned "
    "models, 108 matched prompts at three specificity tiers, four representative hyperparameter "
    "conditions, and three random seeds."
)
add_para(doc,
    "The interaction test found no statistically significant joint effect of prompt specificity "
    "and inference hyperparameters (chi2=2.95, df=7, p=0.889). Prompt framing and model choice "
    "each had stronger and more consistent effects than the sampling parameters tested. Prompt "
    "tier set the overall level of bias: explicit prompts produced 0.0% direct stereotype language, "
    "while semi-explicit and implicit prompts both produced approximately 59% stereotype-aligned "
    "demographic defaulting. Mistral 7B showed the highest defaulting rate (69.5%), with Llama "
    "3.1 8B (54.0%) and Qwen 2.5 7B (53.1%) lower but both well above chance."
)
add_para(doc,
    "The most important finding is that contemporary aligned models appear to have successfully "
    "suppressed explicit discriminatory language while retaining substantial demographic associations "
    "in character framing. A fairness evaluation that measured only explicit bias would report "
    "near-zero rates and miss the 59% implicit and semi-explicit defaulting that persists "
    "underneath. This gap motivates the tiered evaluation framework used in this study, and "
    "suggests that fairness audits of instruction-tuned models should include open-ended "
    "generation tasks with role-based prompts that do not specify demographic identity."
)
add_para(doc,
    "Future work should test a wider hyperparameter grid to determine whether the null interaction "
    "result holds across a broader parameter range, extend the tiered analysis to demographic "
    "dimensions beyond gender, and investigate the sources of the model-level differences observed "
    "between Mistral and the other two models."
)

# ═══════════════════════════════════════════════════════════════════════════════
# REFERENCES (from original doc)
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
for idx, p in ref_paras:
    new_p = doc.add_paragraph()
    new_p.style = get_style(doc, p.style.name)
    for run in p.runs:
        # Do not apply buzzword cleaning to reference list (authors' own wording)
        text = run.text.replace(" -- ", " ").replace("--", " ")
        new_run = new_p.add_run(text)
        new_run.bold   = run.bold
        new_run.italic = run.italic
    if not p.runs:
        new_p.text = p.text.replace(" -- ", " ").replace("--", " ")

# Fix the "xReferences" heading (it has a lowercase x prefix)
for p in doc.paragraphs:
    if p.text.strip().lower().startswith("xreferences"):
        p.text = "References"

doc.save(DEST)
print(f"Saved: {DEST}")
