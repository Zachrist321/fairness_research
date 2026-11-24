"""Generate publication figures from merged gender dataset (1,828 stories)."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "joint_supplement_colab"))
from merge_and_analyze import annotate, load_merged  # noqa: E402

OUT = ROOT / "figures" / "merged"
OUT.mkdir(parents=True, exist_ok=True)

PALETTE = {
    "implicit": "#2E86AB",
    "semi": "#E84855",
    "explicit": "#4C9A52",
    "llama": "#4C72B0",
    "mistral": "#DD4444",
    "qwen": "#2CA02C",
    "female": "#C2185B",
    "male": "#1565C0",
    "low_temp": "#2E86AB",
    "high_temp": "#E84855",
}

ROLE_LABELS = {
    "gender_2_b": "Nurse\n(female-stereotyped)",
    "gender_1_c": "Kindergarten teacher\n(female-stereotyped)",
    "gender_2_c": "Ballet dancer\n(female-stereotyped)",
    "gender_3_b": "Social worker\n(female-stereotyped)",
    "gender_1_a": "Surgeon\n(male-stereotyped)",
    "gender_3_a": "Mech. engineer\n(male-stereotyped)",
    "gender_1_b": "Software engineer\n(male-stereotyped)",
    "gender_2_a": "CEO\n(male-stereotyped)",
    "gender_3_c": "Military officer\n(male-stereotyped)",
}

ROLE_ORDER = list(ROLE_LABELS.keys())

MODEL_SHORT = {
    "meta-llama/Llama-3.1-8B-Instruct": "Llama 3.1 8B",
    "mistralai/Mistral-7B-Instruct-v0.3": "Mistral 7B",
    "Qwen/Qwen2.5-7B-Instruct": "Qwen 2.5 7B",
}

MODEL_COLORS = {
    "meta-llama/Llama-3.1-8B-Instruct": PALETTE["llama"],
    "mistralai/Mistral-7B-Instruct-v0.3": PALETTE["mistral"],
    "Qwen/Qwen2.5-7B-Instruct": PALETTE["qwen"],
}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 150,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    }
)


def evaluable(ann: pd.DataFrame) -> pd.DataFrame:
    return ann[ann["inferred_gender"].isin(["male", "female"])].copy()


def pct_mean(series: pd.Series) -> float:
    return 100.0 * series.mean() if len(series) else float("nan")


def save(fig, name: str):
    path = OUT / name
    fig.savefig(path)
    plt.close(fig)
    print(f"Saved {path}")


def fig_joint_stereotype_rate(ann: pd.DataFrame):
    sub = evaluable(ann[(ann["top_p"] == 1.0) & ann["temperature"].isin([0.3, 1.5])])
    tiers = ["implicit", "semi", "explicit"]
    labels = ["Implicit", "Semi-explicit", "Explicit"]
    low, high = [], []
    for tier in tiers:
        low.append(pct_mean(sub[(sub["prompt_tier"] == tier) & (sub["temperature"] == 0.3)]["stereotype_aligned"]))
        high.append(pct_mean(sub[(sub["prompt_tier"] == tier) & (sub["temperature"] == 1.5)]["stereotype_aligned"]))

    x = np.arange(len(tiers))
    width = 0.34
    fig, ax = plt.subplots(figsize=(8, 5))
    b1 = ax.bar(x - width / 2, low, width, label="Temperature 0.3", color=PALETTE["low_temp"])
    b2 = ax.bar(x + width / 2, high, width, label="Temperature 1.5", color=PALETTE["high_temp"])

    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 1.0, f"{h:.1f}%", ha="center", fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Stereotype-aligned rate (%)")
    ax.set_ylim(0, 85)
    ax.set_title("Stereotype-aligned rate by prompt tier\n(nucleus sampling probability 1.0, merged N=1,828)")
    ax.legend(frameon=True)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%g%%"))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save(fig, "fig_joint_stereotype_rate.png")


def _temp_slopes(ann: pd.DataFrame) -> dict:
    fr = ann[(ann["top_p"] == 1.0) & ann["female_ratio"].notna()]
    slopes = {}
    for tier in ["implicit", "semi", "explicit"]:
        sub = fr[fr["prompt_tier"] == tier]
        if len(sub) < 10:
            continue
        fit = smf.ols("female_ratio ~ temperature", sub).fit()
        slopes[tier] = (fit.params["temperature"], fit.params["Intercept"])
    return slopes


def fig_temp_sweep_female_marker(ann: pd.DataFrame):
    sub = ann[(ann["top_p"] == 1.0) & ann["female_ratio"].notna()]
    tbl = sub.groupby(["prompt_tier", "temperature"])["female_ratio"].agg(["mean", "sem"]).reset_index()
    markers = {"implicit": "o", "semi": "s", "explicit": "^"}
    slopes = _temp_slopes(ann)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for tier, g in tbl.groupby("prompt_tier"):
        g = g.sort_values("temperature")
        ax.plot(
            g["temperature"],
            g["mean"],
            color=PALETTE[tier],
            marker=markers[tier],
            linewidth=2,
            markersize=7,
            label=f"{tier} prompts",
        )
        ax.fill_between(
            g["temperature"],
            g["mean"] - g["sem"],
            g["mean"] + g["sem"],
            color=PALETTE[tier],
            alpha=0.15,
        )
        if tier in slopes:
            coef, intercept = slopes[tier]
            xs = np.linspace(g["temperature"].min(), g["temperature"].max(), 100)
            ax.plot(xs, coef * xs + intercept, color=PALETTE[tier], linestyle="--", linewidth=1.1, alpha=0.55)

    ax.set_xlabel("Temperature (nucleus sampling probability = 1.0)")
    ax.set_ylabel("Female marker proportion")
    ax.set_title("Female marker proportion by prompt tier across temperature\n(merged gender dataset, N=1,828)")
    ax.set_ylim(0, 1.0)
    ax.legend(title="Prompt tier")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    save(fig, "fig_supplement_temp_sweep_x_tier.png")


def fig_temp_sweep_stereotype_aligned(ann: pd.DataFrame):
    sub = evaluable(ann[ann["top_p"] == 1.0])
    tbl = sub.groupby(["prompt_tier", "temperature"])["stereotype_aligned"].mean().reset_index()
    markers = {"implicit": "o", "semi": "s", "explicit": "^"}

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for tier, g in tbl.groupby("prompt_tier"):
        g = g.sort_values("temperature")
        ax.plot(
            g["temperature"],
            100 * g["stereotype_aligned"],
            color=PALETTE[tier],
            marker=markers[tier],
            linewidth=2,
            markersize=7,
            label=f"{tier} prompts",
        )

    ax.set_xlabel("Temperature (nucleus sampling probability = 1.0)")
    ax.set_ylabel("Stereotype-aligned rate (%)")
    ax.set_title("Stereotype-aligned rate by prompt tier across temperature\n(merged gender dataset, N=1,828)")
    ax.set_ylim(0, 85)
    ax.legend(title="Prompt tier")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    save(fig, "fig_temp_sweep_stereotype_aligned.png")


def fig_tiered_bias_summary(ann: pd.DataFrame):
    sub = evaluable(ann)
    semi = pct_mean(sub[sub["prompt_tier"] == "semi"]["stereotype_aligned"])
    implicit = pct_mean(sub[sub["prompt_tier"] == "implicit"]["stereotype_aligned"])
    tiers = [
        "Explicit bias\n(overt stereotype\nlanguage)",
        "Semi-explicit bias\n(neutral-name\nprompts)",
        "Implicit bias\n(role-only\nprompts)",
    ]
    rates = [0.0, semi, implicit]
    colors = ["#2ECC71", PALETTE["semi"], PALETTE["implicit"]]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(tiers, rates, color=colors, width=0.5, edgecolor="white", linewidth=1.5)
    for bar, rate in zip(bars, rates):
        ypos = rate + 1.5 if rate < 80 else rate - 6
        ax.text(bar.get_x() + bar.get_width() / 2, ypos, f"{rate:.1f}%", ha="center", fontsize=12, fontweight="bold")

    ax.axhline(50, color="gray", linestyle="--", linewidth=1.0, alpha=0.6)
    ax.set_ylim(0, 80)
    ax.set_ylabel("Bias-aligned rate (%)")
    ax.set_title("Stereotype-aligned rates by bias tier\n(gender dimension, 1,828 stories)")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%g%%"))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save(fig, "fig5_tiered_bias_summary.png")


def fig_role_defaults(ann: pd.DataFrame):
    sub = evaluable(ann[ann["prompt_tier"] == "implicit"])
    female, male = [], []
    for pid in ROLE_ORDER:
        g = sub[sub["prompt_set_id"] == pid]
        female.append(100.0 * (g["inferred_gender"] == "female").mean() if len(g) else 0)
        male.append(100.0 - female[-1])

    y = np.arange(len(ROLE_ORDER))
    labels = [ROLE_LABELS[p] for p in ROLE_ORDER]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(y, female, color=PALETTE["female"], label="Female-coded", alpha=0.9)
    ax.barh(y, male, left=female, color=PALETTE["male"], label="Male-coded", alpha=0.9)

    for i, (f, m) in enumerate(zip(female, male)):
        if f > 8:
            ax.text(f / 2, i, f"{f:.0f}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        if m > 8:
            ax.text(f + m / 2, i, f"{m:.0f}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

    ax.axvline(50, color="black", linestyle="--", linewidth=1, alpha=0.45)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of generated protagonists (%)")
    ax.set_title("Protagonist gender in implicit role prompts\n(merged gender dataset)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    save(fig, "fig3_role_defaults.png")


def fig_model_comparison(ann: pd.DataFrame):
    sub = evaluable(ann[ann["prompt_tier"].isin(["implicit", "semi"])])
    rows = []
    for model, g in sub.groupby("model_name"):
        rows.append((MODEL_SHORT[model], pct_mean(g["stereotype_aligned"]), MODEL_COLORS[model]))
    rows.sort(key=lambda x: x[1], reverse=True)
    names, rates, colors = zip(*rows)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(names, rates, color=colors, width=0.5, edgecolor="white", linewidth=1.5)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8, f"{rate:.1f}%", ha="center", fontsize=11, fontweight="bold")

    ax.axhline(50, color="gray", linestyle="--", linewidth=1.0, alpha=0.6)
    ax.set_ylim(0, 85)
    ax.set_ylabel("Stereotype-aligned rate (%)")
    ax.set_title("Stereotype-aligned defaulting by model\n(implicit + semi-explicit prompts, merged dataset)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save(fig, "fig4_model_comparison.png")


def fig_joint_per_model(ann: pd.DataFrame):
    conds = [(0.3, 1.0), (1.0, 0.3), (1.0, 0.9), (1.5, 1.0)]
    cond_labels = ["T=0.3\np=1.0", "T=1.0\np=0.3", "T=1.0\np=0.9", "T=1.5\np=1.0"]
    tiers = ["implicit", "semi"]
    tier_labels = ["Implicit", "Semi"]
    models = list(MODEL_SHORT.keys())

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    fig.suptitle("Stereotype-aligned rate by model, tier, and condition (%)", fontsize=13, fontweight="bold", y=1.02)
    im = None
    for ax, model in zip(axes, models):
        mat = np.zeros((2, 4))
        for ri, tier in enumerate(tiers):
            for ci, (temp, tp) in enumerate(conds):
                c = evaluable(
                    ann[
                        (ann["model_name"] == model)
                        & (ann["prompt_tier"] == tier)
                        & (ann["temperature"] == temp)
                        & (ann["top_p"] == tp)
                    ]
                )
                mat[ri, ci] = pct_mean(c["stereotype_aligned"]) if len(c) else np.nan
        im = ax.imshow(mat, cmap="YlOrRd", vmin=40, vmax=85, aspect="auto")
        ax.set_xticks(range(4))
        ax.set_xticklabels(cond_labels, fontsize=8)
        ax.set_yticks(range(2))
        ax.set_yticklabels(tier_labels, fontsize=10)
        ax.set_title(MODEL_SHORT[model], fontsize=11, fontweight="bold")
        for r in range(2):
            for c in range(4):
                val = mat[r, c]
                if np.isnan(val):
                    continue
                color = "white" if val > 65 else "black"
                ax.text(c, r, f"{val:.0f}%", ha="center", va="center", fontsize=9, fontweight="bold", color=color)

    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.85, label="Stereotype-aligned (%)")
    fig.tight_layout()
    save(fig, "fig_joint_per_model.png")


def main():
    ann = annotate(load_merged())
    print(f"Merged stories: {len(ann)}")
    fig_joint_stereotype_rate(ann)
    fig_temp_sweep_female_marker(ann)
    fig_temp_sweep_stereotype_aligned(ann)
    fig_tiered_bias_summary(ann)
    fig_role_defaults(ann)
    fig_model_comparison(ann)
    fig_joint_per_model(ann)
    print(f"\nAll merged figures saved to {OUT}/")


if __name__ == "__main__":
    main()
