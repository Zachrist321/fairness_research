"""Generate cross-dimension figures, save to images_final, embed all in Word."""
from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches
from docx.text.paragraph import Paragraph
from scipy.stats import chi2_contingency

from analyze_deterministic import GEN_CONDS
from analyze_unified_joint import COND_LABELS, COND_ORDER, cond_label

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "images_final"
FIG_SRC = ROOT / "outputs" / "unified_joint" / "figures"
PAPER = ROOT / "Stereotype_Joint_Effect_Research_Paper-FINAL.docx"


def generate_embedding_tier_by_dimension() -> Path:
    rm = pd.read_csv(ROOT / "outputs" / "results_merged.csv")
    rm = rm[rm.apply(lambda r: (float(r.temperature), float(r.top_p)) in GEN_CONDS, axis=1)]
    dims = ["gender", "race", "age", "occupation"]
    tiers = ["implicit", "semi", "explicit"]
    tier_labels = {"implicit": "Implicit", "semi": "Semi-explicit", "explicit": "Explicit"}
    data = []
    for dim in dims:
        for tier in tiers:
            sub = rm[(rm.demographic_dimension == dim) & (rm.prompt_tier == tier)]
            data.append({
                "dimension": dim.title(),
                "tier": tier_labels[tier],
                "similarity": sub["stereotype_similarity"].mean() * 100,
            })
    df = pd.DataFrame(data)
    pivot = df.pivot(index="dimension", columns="tier", values="similarity")
    pivot = pivot[["Implicit", "Semi-explicit", "Explicit"]]

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(pivot.index))
    w = 0.25
    colors = ["#3B7DD8", "#E08214", "#4C9A52"]
    for i, col in enumerate(pivot.columns):
        ax.bar(x + (i - 1) * w, pivot[col].values, width=w, label=col, color=colors[i])
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index)
    ax.set_ylabel("Mean stereotype similarity (%)")
    ax.set_title("Embedding stereotype similarity by dimension and prompt tier (all 3,888 stories)")
    ax.legend()
    ax.set_ylim(0, pivot.values.max() + 5)
    for i, col in enumerate(pivot.columns):
        for j, v in enumerate(pivot[col].values):
            ax.text(x[j] + (i - 1) * w, v + 0.4, f"{v:.1f}", ha="center", fontsize=8, clip_on=False)
    fig.tight_layout()
    path = OUT / "fig9_embedding_similarity_by_dimension.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def embedding_joint_by_dimension(dim: str) -> tuple[pd.DataFrame, dict]:
    rm = pd.read_csv(ROOT / "outputs" / "results_merged.csv")
    rm = rm[rm.apply(lambda r: (float(r.temperature), float(r.top_p)) in GEN_CONDS, axis=1)]
    sub = rm[(rm.demographic_dimension == dim) & rm.prompt_tier.isin(["implicit", "semi"])].copy()
    sub["cond"] = sub.apply(lambda r: cond_label(r.temperature, r.top_p), axis=1)
    sub["high"] = sub.groupby("demographic_dimension")["stereotype_similarity"].transform(
        lambda s: s > s.median()
    )
    pivot = (
        sub.groupby(["prompt_tier", "cond"])["high"]
        .mean()
        .reset_index()
        .pivot(index="prompt_tier", columns="cond", values="high")
    )
    pivot = pivot.reindex(index=["implicit", "semi"])
    pivot = pivot.reindex(columns=[COND_LABELS[c] for c in COND_ORDER])
    counts = (
        sub.assign(a=lambda d: d["high"].astype(int), na=lambda d: (~d["high"]).astype(int))
        .groupby(["prompt_tier", "cond"])
        .agg(aligned=("a", "sum"), not_aligned=("na", "sum"))
        .reset_index()
    )
    chi_table = counts.pivot_table(
        index=["prompt_tier", "cond"], values=["aligned", "not_aligned"]
    ).fillna(0).astype(int)
    chi2, p, dof, _ = chi2_contingency(chi_table.values)
    stats = {"chi2": float(chi2), "p": float(p), "n": len(sub)}
    return pivot, stats


def generate_embedding_joint_panel() -> Path:
    dims = ["gender", "race", "age", "occupation"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    colors = {"implicit": "#3B7DD8", "semi": "#E08214"}
    for ax, dim in zip(axes.flat, dims):
        table, stats = embedding_joint_by_dimension(dim)
        table_pct = table * 100
        x = np.arange(len(table_pct.columns))
        all_vals = [v for tier in ["implicit", "semi"]
                    for v in table_pct.loc[tier].dropna().values if not np.isnan(v)]
        y_max = max(all_vals) if all_vals else 65
        ax.set_ylim(30, y_max + 9)
        for tier in ["implicit", "semi"]:
            y = table_pct.loc[tier].values
            ax.plot(x, y, marker="o", linewidth=2, color=colors[tier], label=f"{tier}")
        ax.set_xticks(x)
        ax.set_xticklabels(table_pct.columns, rotation=20, ha="right", fontsize=7)
        ax.set_title(f"{dim.title()} (chi2={stats['chi2']:.1f}, p={stats['p']:.2f})", fontsize=10)
        ax.grid(axis="y", alpha=0.3)
    axes[0, 0].legend(title="Prompt tier", fontsize=8)
    fig.suptitle(
        "Embedding high-similarity rate by tier and condition (per dimension, implicit + semi)",
        y=1.02,
    )
    fig.tight_layout()
    path = OUT / "fig10_embedding_joint_effect_by_dimension.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_occupation_tier_chart() -> Path:
    from analyze_unified_joint import annotate_all
    gen = pd.read_csv(ROOT / "checkpoints" / "generations.csv")
    gen = gen[gen.apply(lambda r: (float(r.temperature), float(r.top_p)) in GEN_CONDS, axis=1)]
    ann = annotate_all(gen)
    occ = ann[ann.demographic_dimension == "occupation"]
    ev = occ[occ.stereotype_aligned.notna()]
    rates = ev.groupby("prompt_tier")["stereotype_aligned"].mean() * 100
    order = ["implicit", "semi", "explicit"]
    rates = rates.reindex(order)

    tier_labels = {"implicit": "Implicit", "semi": "Semi-explicit", "explicit": "Explicit"}
    fig, ax = plt.subplots(figsize=(7, 4.6))
    bars = ax.bar(
        [tier_labels[t] for t in rates.index],
        rates.values,
        color=["#3B7DD8", "#E08214", "#4C9A52"],
        width=0.6,
    )
    ax.set_ylim(0, max(rates.values) + 12)
    ax.set_ylabel("Stereotype-aligned rate (%)")
    ax.set_title(
        "Occupation dimension\nDeterministic gender defaulting by prompt tier",
        fontsize=11,
    )
    ax.margins(x=0.12)
    for bar, v in zip(bars, rates.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            v + 1.5,
            f"{v:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
            clip_on=False,
        )
    fig.tight_layout()
    path = OUT / "fig11_occupation_tier_rates.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


# All figures for the paper (source path, output name, caption)
FIGURE_SPECS: list[tuple[str, Path, str]] = []


def build_figure_list() -> list[tuple[str, Path, str]]:
    specs = [
        (
            "fig1_joint_effect_embedding.png",
            FIG_SRC / "fig_joint_embedding.png",
            "Figure 1. Joint effect on embedding stereotype similarity (all dimensions pooled, implicit and semi-explicit prompts).",
        ),
        (
            "fig9_embedding_similarity_by_dimension.png",
            OUT / "fig9_embedding_similarity_by_dimension.png",
            "Figure 2. Mean embedding stereotype similarity by demographic dimension and prompt tier (all 3,888 stories).",
        ),
        (
            "fig10_embedding_joint_effect_by_dimension.png",
            OUT / "fig10_embedding_joint_effect_by_dimension.png",
            "Figure 3. Embedding high-similarity rate by tier and hyperparameter condition, stratified by dimension.",
        ),
        (
            "fig2_joint_effect_gender_occupation.png",
            FIG_SRC / "fig_joint_gender_occupation.png",
            "Figure 4. Joint effect on deterministic stereotype-aligned defaulting (gender and occupation pooled).",
        ),
        (
            "fig11_occupation_tier_rates.png",
            OUT / "fig11_occupation_tier_rates.png",
            "Figure 5. Occupation dimension. Stereotype-aligned defaulting by prompt tier (deterministic coder).",
        ),
        (
            "fig3_tier_rates_gender.png",
            ROOT / "outputs/deterministic_bias/figures/fig4_gender_share_by_tier.png",
            "Figure 6. Gender dimension. Protagonist gender share by prompt tier.",
        ),
        (
            "fig4_role_defaults_implicit.png",
            ROOT / "outputs/deterministic_bias/figures/fig1_implicit_defaults_by_role.png",
            "Figure 7. Gender dimension. Protagonist gender by role for implicit prompts.",
        ),
        (
            "fig5_model_comparison.png",
            ROOT / "outputs/deterministic_bias/figures/fig3_stereotype_aligned_by_model.png",
            "Figure 8. Gender dimension. Stereotype-aligned defaulting rate by model.",
        ),
        (
            "fig6_joint_effect_by_model.png",
            ROOT / "outputs/deterministic_bias/figures/fig8_joint_effect_by_model.png",
            "Figure 9. Gender dimension. Stereotype-aligned rate by tier and condition for each model.",
        ),
        (
            "fig7_supplement_temperature_sweep.png",
            ROOT / "figures/merged/fig_temp_sweep_stereotype_aligned.png",
            "Figure 10. Gender supplement. Stereotype-aligned rate across six temperatures by prompt tier.",
        ),
        (
            "fig8_supplement_female_markers.png",
            ROOT / "figures/merged/fig_supplement_temp_sweep_x_tier.png",
            "Figure 11. Gender supplement. Female marker proportion across six temperatures by prompt tier.",
        ),
    ]
    return specs


def copy_all_figures(specs: list[tuple[str, Path, str]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lines = ["Publication figures for Stereotype_Joint_Effect_Research_Paper-FINAL.docx\n"]
    for name, src, _ in specs:
        if not src.exists():
            raise FileNotFoundError(f"Missing: {src}")
        dest = OUT / name
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
        lines.append(f"  {name}")
    (OUT / "README.txt").write_text("\n".join(lines) + "\n")


def remove_inline_shapes(doc: Document) -> None:
    from docx.oxml.ns import qn
    for drawing in list(doc.element.body.iter(qn("w:drawing"))):
        run = drawing.getparent()
        if run is not None:
            para = run.getparent()
            if para is not None:
                para.remove(run)


def insert_paragraph_after(paragraph: Paragraph) -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    return Paragraph(new_p, paragraph._parent)


def results_start_index(doc: Document) -> int:
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == "4. Results":
            return i
    raise ValueError("Could not find '4. Results' section heading")


def find_anchor(doc: Document, anchor_text: str, min_index: int = 0) -> int | None:
    for i, p in enumerate(doc.paragraphs):
        if i >= min_index and anchor_text in p.text:
            return i
    return None


def embed_all_figures(specs: list[tuple[str, Path, str]]) -> None:
    doc = Document(str(PAPER))
    remove_inline_shapes(doc)

    # Clear old figure caption paragraphs
    for p in doc.paragraphs:
        t = p.text.strip()
        if t.startswith("Figure ") or t.startswith("[Figure") or "images_final/" in t:
            p.text = ""

    results_idx = results_start_index(doc)

    # Anchor only inside §4 Results (avoid abstract matches on shared phrases).
    anchors: list[tuple[str, list[tuple[str, Path, str]]]] = [
        (
            "Test B used deterministic defaulting on gender and occupation stories",
            [specs[0], specs[1], specs[2], specs[3]],
        ),
        (
            "Age and race coders had limited coverage on implicit and semi-explicit prompts",
            [specs[4], specs[5]],
        ),
        (
            "Surgeon and mechanical engineer each scored",
            [specs[6]],
        ),
        (
            "Mistral stayed highest across all four hyperparameter conditions",
            [specs[7], specs[8]],
        ),
        (
            "On the supplement grid female marker share for implicit prompts",
            [specs[9], specs[10]],
        ),
    ]

    for anchor_text, fig_group in anchors:
        idx = find_anchor(doc, anchor_text, min_index=results_idx)
        if idx is None:
            print(f"WARNING: anchor not found in Results: {anchor_text[:60]}")
            continue
        insert_at = doc.paragraphs[idx]
        for name, _, caption in fig_group:
            img_path = OUT / name
            cap_p = insert_paragraph_after(insert_at)
            cap_p.text = caption
            img_p = insert_paragraph_after(cap_p)
            img_p.add_run().add_picture(str(img_path), width=Inches(5.8))
            insert_at = img_p

    doc.save(str(PAPER))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("Generating cross-dimension figures...")
    generate_embedding_tier_by_dimension()
    generate_embedding_joint_panel()
    generate_occupation_tier_chart()

    # Regenerate core analysis figures
    import subprocess
    subprocess.run(
        ["python3", "analyze_unified_joint.py"],
        cwd=ROOT,
        check=True,
        env={**__import__("os").environ, "MPLCONFIGDIR": str(ROOT / ".cache/mpl")},
    )
    subprocess.run(
        ["python3", "analyze_deterministic.py"],
        cwd=ROOT,
        check=True,
        env={**__import__("os").environ, "MPLCONFIGDIR": str(ROOT / ".cache/mpl")},
    )
    subprocess.run(
        ["python3", "generate_merged_figures.py"],
        cwd=ROOT,
        check=True,
        env={**__import__("os").environ, "MPLCONFIGDIR": str(ROOT / ".cache/mpl")},
    )

    specs = build_figure_list()
    copy_all_figures(specs)
    print(f"Saved {len(specs)} figures to {OUT}")

    embed_all_figures(specs)
    doc = Document(str(PAPER))
    print(f"Embedded {len(doc.inline_shapes)} images in {PAPER}")


if __name__ == "__main__":
    main()
