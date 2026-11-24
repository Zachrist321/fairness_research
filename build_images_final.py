"""Copy publication figures to images_final and insert into the paper."""
from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.shared import Inches

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "images_final"
PAPER = ROOT / "Stereotype_Joint_Effect_Research_Paper-FINAL.docx"

# Final figure set aligned with paper sections
FIGURES: list[tuple[str, Path, str]] = [
    (
        "fig1_joint_effect_embedding.png",
        ROOT / "outputs/unified_joint/figures/fig_joint_embedding.png",
        "Figure 1. Joint effect on embedding stereotype similarity (all dimensions, implicit and semi-explicit prompts).",
    ),
    (
        "fig2_joint_effect_gender_occupation.png",
        ROOT / "outputs/unified_joint/figures/fig_joint_gender_occupation.png",
        "Figure 2. Joint effect on deterministic stereotype-aligned defaulting (gender and occupation pooled).",
    ),
    (
        "fig3_tier_rates_gender.png",
        ROOT / "outputs/deterministic_bias/figures/fig4_gender_share_by_tier.png",
        "Figure 3. Protagonist gender share by prompt tier (gender dimension).",
    ),
    (
        "fig4_role_defaults_implicit.png",
        ROOT / "outputs/deterministic_bias/figures/fig1_implicit_defaults_by_role.png",
        "Figure 4. Protagonist gender by role for implicit prompts.",
    ),
    (
        "fig5_model_comparison.png",
        ROOT / "outputs/deterministic_bias/figures/fig3_stereotype_aligned_by_model.png",
        "Figure 5. Stereotype-aligned defaulting rate by model (gender, implicit and semi-explicit).",
    ),
    (
        "fig6_joint_effect_by_model.png",
        ROOT / "outputs/deterministic_bias/figures/fig8_joint_effect_by_model.png",
        "Figure 6. Stereotype-aligned rate by tier and condition for each model (gender).",
    ),
    (
        "fig7_supplement_temperature_sweep.png",
        ROOT / "figures/merged/fig_temp_sweep_stereotype_aligned.png",
        "Figure 7. Gender supplement. Stereotype-aligned rate across six temperatures by prompt tier.",
    ),
    (
        "fig8_supplement_female_markers.png",
        ROOT / "figures/merged/fig_supplement_temp_sweep_x_tier.png",
        "Figure 8. Gender supplement. Female marker proportion across six temperatures by prompt tier.",
    ),
]

# Map old placeholder substrings to new figure filename
PLACEHOLDER_MAP = {
    "fig_joint_embedding.png": "fig1_joint_effect_embedding.png",
    "fig1_implicit_defaults_by_role.png": "fig4_role_defaults_implicit.png",
    "fig3_stereotype_aligned_by_model.png": "fig5_model_comparison.png",
    "fig8_joint_effect_by_model.png": "fig6_joint_effect_by_model.png",
    "fig_temp_sweep_stereotype_aligned.png": "fig7_supplement_temperature_sweep.png",
}


def copy_figures() -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    saved = []
    for name, src, _ in FIGURES:
        if not src.exists():
            raise FileNotFoundError(f"Missing source figure: {src}")
        dest = OUT / name
        shutil.copy2(src, dest)
        saved.append(dest)
    readme = OUT / "README.txt"
    readme.write_text(
        "Publication figures for Stereotype_Joint_Effect_Research_Paper-FINAL.docx\n\n"
        + "\n".join(f"  {name}  <-  {src.relative_to(ROOT)}" for name, src, _ in FIGURES)
        + "\n"
    )
    return saved


from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph


def insert_paragraph_after(paragraph) -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    return Paragraph(new_p, paragraph._parent)


def insert_image_below(paragraph, image_path: Path, width_in: float = 5.5) -> None:
    img_p = insert_paragraph_after(paragraph)
    img_p.add_run().add_picture(str(image_path), width=Inches(width_in))


def update_paper() -> None:
    doc = Document(str(PAPER))
    caption_by_file = {name: caption for name, _, caption in FIGURES}

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text.startswith("[Figure"):
            continue
        for old_key, new_name in PLACEHOLDER_MAP.items():
            if old_key in text:
                p.text = caption_by_file[new_name] + f" (images_final/{new_name})"
                img = OUT / new_name
                if img.exists():
                    insert_image_below(p, img)
                break

    doc.save(str(PAPER))


def main() -> None:
    paths = copy_figures()
    print(f"Saved {len(paths)} figures to {OUT}")
    for p in paths:
        print(" ", p.name)
    update_paper()
    print("Updated paper with embedded images:", PAPER)


if __name__ == "__main__":
    main()
