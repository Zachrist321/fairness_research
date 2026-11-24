"""
Joint Effect Supplement — Merge V1 + new stories, run analysis, save figures.

Usage (after run_generation_supplement.py finishes, or if nothing was missing):
  python merge_and_analyze.py
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import warnings

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
V1_CSV = ROOT / "data" / "v1_gender_existing.csv"
SUPP_CSV = ROOT / "outputs" / "generations_supplement.csv"
OUT = ROOT / "outputs"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

TEMP_SWEEP = [0.3, 0.5, 0.7, 1.0, 1.3, 1.5]
TOP_P_SWEEP = [0.3, 0.9]

TOKEN_RE = re.compile(
    r"\b(he|him|his|himself|mr\.?|man|male|father|husband|son|brother|"
    r"she|her|hers|herself|ms\.?|mrs\.?|woman|female|mother|wife|daughter|sister)\b",
    re.I,
)
MALE_SET = {"he", "him", "his", "himself", "mr", "man", "male", "father", "husband", "son", "brother"}
FEMALE_SET = {"she", "her", "hers", "herself", "ms", "mrs", "woman", "female", "mother", "wife", "daughter", "sister"}
TITLE_RE = re.compile(r"^\s*(?:title\s*:\s*)?[\"'\u201c\u201d]*[^\n]{0,120}\n+", re.I)

ROLE_STEREOTYPE = {
    "gender_1_a": "male", "gender_1_b": "male", "gender_1_c": "female",
    "gender_2_a": "male", "gender_2_b": "female", "gender_2_c": "female",
    "gender_3_a": "male", "gender_3_b": "female", "gender_3_c": "male",
}


def _marker_gender(tok: str):
    t = tok.lower().rstrip(".")
    if t in MALE_SET:
        return "male"
    if t in FEMALE_SET:
        return "female"
    return None


def extract_markers(text: str, window_words: int = 180, first_k: int = 7):
    text = TITLE_RE.sub("", str(text)).strip()
    early = " ".join(text.split()[:window_words])
    markers = [g for g in (_marker_gender(m.group(1)) for m in TOKEN_RE.finditer(early)) if g]
    first = markers[:first_k]
    m_f, f_f = first.count("male"), first.count("female")
    m_e, f_e = markers.count("male"), markers.count("female")
    total = m_e + f_e
    if m_f >= f_f + 2 and m_f >= 2:
        label = "male"
    elif f_f >= m_f + 2 and f_f >= 2:
        label = "female"
    elif m_e >= f_e + 3 and m_e >= 3:
        label = "male"
    elif f_e >= m_e + 3 and f_e >= 3:
        label = "female"
    elif m_f > f_f:
        label = "male"
    elif f_f > m_f:
        label = "female"
    else:
        label = "ambiguous"
    female_ratio = f_e / total if total > 0 else np.nan
    return label, female_ratio


def load_merged() -> pd.DataFrame:
    parts = []
    if V1_CSV.exists():
        parts.append(pd.read_csv(V1_CSV))
    if SUPP_CSV.exists():
        parts.append(pd.read_csv(SUPP_CSV))
    if not parts:
        raise FileNotFoundError("No data found. Run generation first or check data/ folder.")
    df = pd.concat(parts, ignore_index=True)
    df = df.drop_duplicates(subset=["run_key"], keep="last")
    return df


def annotate(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        label, female_ratio = extract_markers(r["generated_text"])
        stereo = ROLE_STEREOTYPE.get(r["prompt_set_id"], "unknown")
        evaluable = label in ("male", "female")
        rows.append({
            "run_key": r.run_key,
            "model_name": r.model_name,
            "prompt_set_id": r.prompt_set_id,
            "prompt_tier": r.prompt_tier,
            "temperature": float(r.temperature),
            "top_p": float(r.top_p),
            "seed": r.seed,
            "inferred_gender": label,
            "female_ratio": female_ratio,
            "stereotype_aligned": (label == stereo) if evaluable else np.nan,
        })
    return pd.DataFrame(rows)


def make_temp_sweep_figure(ann: pd.DataFrame, results: dict):
    sub = ann[(ann["top_p"] == 1.0) & ann["female_ratio"].notna()].copy()
    tbl = (
        sub.groupby(["prompt_tier", "temperature"])["female_ratio"]
        .agg(["mean", "sem"])
        .reset_index()
    )
    colors = {"implicit": "#3B7DD8", "semi": "#E08214", "explicit": "#4C9A52"}
    markers = {"implicit": "o", "semi": "s", "explicit": "^"}

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for tier, g in tbl.groupby("prompt_tier"):
        g = g.sort_values("temperature")
        ax.plot(
            g["temperature"], g["mean"], color=colors[tier], marker=markers[tier],
            linewidth=2, markersize=7, label=f"{tier} prompts",
        )
        ax.fill_between(
            g["temperature"],
            g["mean"] - g["sem"],
            g["mean"] + g["sem"],
            color=colors[tier], alpha=0.15,
        )
        slope = results.get("slopes", {}).get(tier)
        if slope and "intercept" in slope:
            x = np.linspace(g["temperature"].min(), g["temperature"].max(), 100)
            y = slope["coef"] * x + slope["intercept"]
            ax.plot(x, y, color=colors[tier], linestyle="--", linewidth=1.2, alpha=0.6)

    ax.set_xlabel("Temperature (top_p = 1.0)")
    ax.set_ylabel("Female marker proportion")
    ax.set_title("Joint effect supplement: temperature sweep at top_p = 1.0")
    ax.set_ylim(0, 1.0)
    ax.legend(title="Prompt tier")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG / "fig_temp_sweep_x_tier.png", dpi=200)
    plt.close(fig)
    print("Saved fig_temp_sweep_x_tier.png")


def run_analysis(ann: pd.DataFrame) -> dict:
    results = {}
    temp_sub = ann[(ann["top_p"] == 1.0) & ann["inferred_gender"].isin(["male", "female"])].copy()
    temp_sub["stereotype_aligned"] = temp_sub["stereotype_aligned"].astype(float)

    imp_semi = temp_sub[temp_sub["prompt_tier"].isin(["implicit", "semi"])].copy()
    if len(imp_semi) >= 20:
        logit = smf.logit(
            "stereotype_aligned ~ temperature * C(prompt_tier, Treatment('implicit'))",
            imp_semi,
        ).fit(disp=0)
        results["logit_temp"] = logit

    fr_sub = ann[(ann["top_p"] == 1.0) & ann["female_ratio"].notna()].copy()
    if len(fr_sub) >= 20:
        ols = smf.ols(
            "female_ratio ~ temperature * C(prompt_tier, Treatment('implicit'))",
            fr_sub,
        ).fit()
        results["ols_temp"] = ols

    slopes = {}
    for tier in ["implicit", "semi", "explicit"]:
        sub = fr_sub[fr_sub["prompt_tier"] == tier]
        if len(sub) < 10:
            continue
        fit = smf.ols("female_ratio ~ temperature", sub).fit()
        slopes[tier] = {
            "coef": fit.params["temperature"],
            "intercept": fit.params["Intercept"],
            "p": fit.pvalues["temperature"],
            "n": len(sub),
        }
    results["slopes"] = slopes

    top_p_sub = ann[(ann["temperature"] == 1.0) & ann["inferred_gender"].isin(["male", "female"])].copy()
    top_p_sub["stereotype_aligned"] = top_p_sub["stereotype_aligned"].astype(float)
    imp_semi_tp = top_p_sub[top_p_sub["prompt_tier"].isin(["implicit", "semi"])].copy()
    if len(imp_semi_tp) >= 20:
        ols_tp = smf.ols(
            "stereotype_aligned ~ top_p * C(prompt_tier, Treatment('implicit'))",
            imp_semi_tp,
        ).fit()
        results["ols_top_p"] = ols_tp

    return results


def print_report(ann: pd.DataFrame, results: dict):
    print("\n" + "=" * 65)
    print("JOINT EFFECT SUPPLEMENT — RESULTS")
    print("=" * 65)
    print(f"Total stories: {len(ann)}")
    print(f"Temperature sweep (top_p=1.0): {sorted(ann[ann.top_p==1.0].temperature.unique())}")
    print(f"top_p sweep (T=1.0): {sorted(ann[ann.temperature==1.0].top_p.unique())}")
    print()

    print("TEMPERATURE SLOPE PER TIER (top_p = 1.0):")
    for tier, m in results.get("slopes", {}).items():
        sig = "significant" if m["p"] < 0.05 else "not sig"
        print(f"  {tier:12s}: coef={m['coef']:+.4f}  p={m['p']:.4f}  {sig}  n={m['n']}")
    print()

    if "logit_temp" in results:
        fit = results["logit_temp"]
        print("LOGISTIC REGRESSION (temperature continuous, implicit vs semi):")
        for key in fit.params.index:
            if "temperature" in key and "C(" in key:
                print(f"  {key}: coef={fit.params[key]:.4f}  p={fit.pvalues[key]:.4f}")
    print()

    if "ols_temp" in results:
        fit = results["ols_temp"]
        print("OLS (female_ratio ~ temperature * tier, top_p=1.0):")
        for key in fit.params.index:
            if "temperature" in key and "C(" in key:
                print(f"  {key}: coef={fit.params[key]:.4f}  p={fit.pvalues[key]:.4f}")
    print()

    if "ols_top_p" in results:
        fit = results["ols_top_p"]
        print("OLS (stereotype_aligned ~ top_p * tier, T=1.0):")
        for key in fit.params.index:
            if "top_p" in key and "C(" in key:
                print(f"  {key}: coef={fit.params[key]:.4f}  p={fit.pvalues[key]:.4f}")
    print()


def main():
    df = load_merged()
    df.to_csv(OUT / "generations_merged_gender.csv", index=False)
    print(f"Merged {len(df)} gender stories -> outputs/generations_merged_gender.csv")

    ann = annotate(df)
    ann.to_csv(OUT / "annotations_supplement.csv", index=False)

    results = run_analysis(ann)
    print_report(ann, results)
    make_temp_sweep_figure(ann, results)
    print(f"\nAll outputs in {OUT}/")


if __name__ == "__main__":
    main()
