"""Final-stage fixes: military officer rate, minor style."""
from docx import Document

PATH = "/Users/zach/python/fairness_research/research_experiment/Stereotype_Joint_Effect_Research_Paper-FINAL.docx"


def main():
    doc = Document(PATH)

    doc.paragraphs[110].text = (
        "Female-stereotyped roles were assigned female protagonists in 100 percent of classifiable "
        "stories for nurse, kindergarten teacher, and ballet dancer. "
        "Social worker followed at 91.5 percent. "
        "Male-stereotyped roles showed weaker alignment. "
        "Military officer received a male protagonist in 51.7 percent of stories. "
        "Surgeon scored 16.7 percent stereotype-aligned. "
        "Mechanical engineer scored 25.0 percent stereotype-aligned."
    )

    doc.paragraphs[84].text = (
        "Of 1,828 gender stories, 1,804 (98.7 percent) yielded a classifiable protagonist gender. "
        "The remaining 24 stories used gender-neutral language throughout and were treated as ambiguous."
    )

    doc.paragraphs[155].text = (
        "The tiered framework showed that the relevant question for instruction-tuned models is not "
        "whether they produce explicit discriminatory text. They generally do not. "
        "The question is whether they reproduce demographic associations through character framing. "
        "This distinction matters for fairness audits of deployed systems. "
        "Users commonly write role-based prompts without specifying demographic identity."
    )

    doc.save(PATH)
    print("Final fixes applied.")


if __name__ == "__main__":
    main()
