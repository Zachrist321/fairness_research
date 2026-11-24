"""Full merged analysis (V1 + supplement) with V1 comparison. No docx edits."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent / "joint_supplement_colab"
sys.path.insert(0, str(ROOT))

from merge_and_analyze import V1_CSV, SUPP_CSV, annotate, extract_markers, ROLE_STEREOTYPE  # noqa: E402

TOKEN_RE = re.compile(
    r"\b(he|him|his|himself|mr\.?|man|male|father|husband|son|brother|"
    r"she|her|hers|herself|ms\.?|mrs\.?|woman|female|mother|wife|daughter|sister)\b",
    re.I,
)


def load_df(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def merge_v1_supp() -> pd.DataFrame:
    parts = []
    if V1_CSV.exists():
        parts.append(load_df(V1_CSV))
    if SUPP_CSV.exists():
        parts.append(load_df(SUPP_CSV))
    df = pd.concat(parts, ignore_index=True)
    return df.drop_duplicates(subset=["run_key"], keep="last")


def tier_rates(ann: pd.DataFrame) -> dict:
    out = {}
    for tier in ["explicit", "semi", "implicit"]:
        sub = ann[ann.prompt_tier == tier]
        evaluable = sub[sub.inferred_gender.isin(["male", "female"])]
        if tier == "explicit":
            out[tier] = {
                "n": len(sub),
                "explicit_language_pct": 0.0,
                "stereo_aligned_pct": 100 * evaluable.stereotype_aligned.mean() if len(evaluable) else np.nan,
                "evaluable": len(evaluable),
            }
        else:
            out[tier] = {
                "n": len(sub),
                "stereo_aligned_pct": 100 * evaluable.stereotype_aligned.mean() if len(evaluable) else np.nan,
                "evaluable": len(evaluable),
            }
    return out


def model_rates(ann: pd.DataFrame) -> pd.DataFrame:
    sub = ann[ann.prompt_tier.isin(["implicit", "semi"])]
    evaluable = sub[sub.inferred_gender.isin(["male", "female"])]
    return (
        evaluable.groupby("model_name")["stereotype_aligned"]
        .agg(["mean", "count"])
        .assign(pct=lambda x: 100 * x["mean"])
        .sort_values("pct", ascending=False)
    )


def role_rates(ann: pd.DataFrame) -> pd.DataFrame:
    sub = ann[(ann.prompt_tier == "implicit") & ann.inferred_gender.isin(["male", "female"])]
    return (
        sub.groupby("prompt_set_id")["stereotype_aligned"]
        .agg(["mean", "count"])
        .assign(pct=lambda x: 100 * x["mean"])
        .sort_values("pct", ascending=False)
    )


def temp_endpoints(ann: pd.DataFrame) -> pd.DataFrame:
    sub = ann[(ann.top_p == 1.0) & ann.inferred_gender.isin(["male", "female"])]
    rows = []
    for tier in ["implicit", "semi", "explicit"]:
        for temp in [0.3, 1.5]:
            cell = sub[(sub.prompt_tier == tier) & (sub.temperature == temp)]
            if len(cell):
                rows.append({
                    "tier": tier,
                    "temp": temp,
                    "pct": 100 * cell.stereotype_aligned.mean(),
                    "n": len(cell),
                })
    return pd.DataFrame(rows)


def temp_sweep_table(ann: pd.DataFrame) -> pd.DataFrame:
    sub = ann[(ann.top_p == 1.0) & ann.inferred_gender.isin(["male", "female"])]
    return (
        sub.groupby(["prompt_tier", "temperature"])["stereotype_aligned"]
        .agg(["mean", "count"])
        .assign(pct=lambda x: 100 * x["mean"])
        .reset_index()
    )


def regressions(ann: pd.DataFrame) -> dict:
    out = {}
    temp_sub = ann[(ann.top_p == 1.0) & ann.inferred_gender.isin(["male", "female"])].copy()
    temp_sub["stereotype_aligned"] = temp_sub["stereotype_aligned"].astype(float)
    imp_semi = temp_sub[temp_sub.prompt_tier.isin(["implicit", "semi"])]

    if len(imp_semi) >= 20:
        logit = smf.logit(
            "stereotype_aligned ~ temperature * C(prompt_tier, Treatment('implicit'))",
            imp_semi,
        ).fit(disp=0)
        out["logit_interaction_key"] = [
            k for k in logit.params.index if "temperature" in k and "C(" in k
        ][0]
        out["logit_interaction_b"] = logit.params[out["logit_interaction_key"]]
        out["logit_interaction_p"] = logit.pvalues[out["logit_interaction_key"]]

    fr_sub = ann[(ann.top_p == 1.0) & ann.female_ratio.notna()].copy()
    for tier in ["implicit", "semi", "explicit"]:
        tsub = fr_sub[fr_sub.prompt_tier == tier]
        if len(tsub) >= 10:
            fit = smf.ols("female_ratio ~ temperature", tsub).fit()
            out[f"ols_{tier}_b"] = fit.params["temperature"]
            out[f"ols_{tier}_p"] = fit.pvalues["temperature"]
            out[f"ols_{tier}_n"] = len(tsub)

    if len(fr_sub) >= 20:
        ols = smf.ols(
            "female_ratio ~ temperature * C(prompt_tier, Treatment('implicit'))",
            fr_sub,
        ).fit()
        key = [k for k in ols.params.index if "temperature" in k and "C(" in k][0]
        out["ols_interaction_b"] = ols.params[key]
        out["ols_interaction_p"] = ols.pvalues[key]

    return out


def v1_binary_temp(ann: pd.DataFrame) -> pd.DataFrame:
    sub = ann[
        (ann.top_p == 1.0)
        & ann.temperature.isin([0.3, 1.5])
        & ann.prompt_tier.isin(["implicit", "semi"])
        & ann.inferred_gender.isin(["male", "female"])
    ]
    return (
        sub.groupby(["model_name", "prompt_tier", "temperature"])["stereotype_aligned"]
        .mean()
        .mul(100)
        .reset_index(name="pct")
    )


def print_section(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    merged_raw = merge_v1_supp()
    v1_raw = load_df(V1_CSV)
    supp_only = load_df(SUPP_CSV)

    merged = annotate(merged_raw)
    v1 = annotate(v1_raw)

    print_section("DATA COUNTS")
    print(f"V1 gender stories:        {len(v1_raw)}")
    print(f"Supplement stories:       {len(supp_only)}")
    print(f"Merged (deduped):         {len(merged_raw)}")
    print(f"Merged evaluable gender:  {merged.inferred_gender.isin(['male','female']).sum()}")
    print(f"V1 evaluable gender:      {v1.inferred_gender.isin(['male','female']).sum()}")

    print_section("TIER RATES — V1 vs MERGED")
    v1_t = tier_rates(v1)
    m_t = tier_rates(merged)
    print(f"{'Tier':<10} {'V1 %':>8} {'V1 n':>6}   {'Merged %':>10} {'Merged n':>8}")
    for tier in ["explicit", "semi", "implicit"]:
        v = v1_t[tier]
        m = m_t[tier]
        print(
            f"{tier:<10} {v['stereo_aligned_pct']:>7.1f}% {v['evaluable']:>6}   "
            f"{m['stereo_aligned_pct']:>9.1f}% {m['evaluable']:>8}"
        )

    print_section("MODEL RATES (implicit + semi) — V1 vs MERGED")
    v1_m = model_rates(v1)
    m_m = model_rates(merged)
    print(f"{'Model':<35} {'V1 %':>8} {'Merged %':>10}")
    for model in sorted(set(v1_m.index) | set(m_m.index)):
        vp = v1_m.loc[model, "pct"] if model in v1_m.index else np.nan
        mp = m_m.loc[model, "pct"] if model in m_m.index else np.nan
        print(f"{model:<35} {vp:>7.1f}% {mp:>9.1f}%")

    print_section("TEMPERATURE ENDPOINTS (top_p=1.0) — MERGED")
    for _, r in temp_endpoints(merged).iterrows():
        print(f"  {r['tier']:<10} T={r['temp']}: {r['pct']:.1f}%  (n={int(r['n'])})")

    print_section("TEMPERATURE SWEEP (top_p=1.0, stereotype-aligned %) — MERGED")
    for tier in ["implicit", "semi", "explicit"]:
        t = temp_sweep_table(merged)
        g = t[t.prompt_tier == tier].sort_values("temperature")
        vals = ", ".join(f"T={row.temperature:.1f}:{row.pct:.1f}%" for _, row in g.iterrows())
        print(f"  {tier}: {vals}")

    print_section("REGRESSIONS — MERGED")
    reg = regressions(merged)
    if "logit_interaction_p" in reg:
        print(
            f"Logistic interaction (implicit vs semi): b={reg['logit_interaction_b']:.3f}, "
            f"p={reg['logit_interaction_p']:.3f}"
        )
    for tier in ["implicit", "semi", "explicit"]:
        if f"ols_{tier}_p" in reg:
            print(
                f"OLS female_ratio slope ({tier}): b={reg[f'ols_{tier}_b']:+.4f}, "
                f"p={reg[f'ols_{tier}_p']:.4f}, n={int(reg[f'ols_{tier}_n'])}"
            )
    if "ols_interaction_p" in reg:
        print(
            f"OLS interaction (semi vs implicit): b={reg['ols_interaction_b']:+.4f}, "
            f"p={reg['ols_interaction_p']:.4f}"
        )

    print_section("V1 TWO-POINT SHIFT BY MODEL (implicit, T=0.3 vs T=1.5)")
    pivot = v1_binary_temp(v1)
    for model in sorted(pivot.model_name.unique()):
        imp = pivot[(pivot.model_name == model) & (pivot.prompt_tier == "implicit")]
        low = imp[imp.temperature == 0.3]["pct"].values
        high = imp[imp.temperature == 1.5]["pct"].values
        if len(low) and len(high):
            print(f"  {model}: {low[0]:.1f}% -> {high[0]:.1f}%  (delta {high[0]-low[0]:+.1f} pp)")

    print_section("ROLE RATES (implicit) — V1 vs MERGED (top roles)")
    v1_r = role_rates(v1)
    m_r = role_rates(merged)
    print(f"{'Role':<15} {'V1 %':>8} {'Merged %':>10}")
    for role in sorted(set(v1_r.index) | set(m_r.index)):
        vp = v1_r.loc[role, "pct"] if role in v1_r.index else np.nan
        mp = m_r.loc[role, "pct"] if role in m_r.index else np.nan
        print(f"{role:<15} {vp:>7.1f}% {mp:>9.1f}%")

    print_section("BOTTOM LINE")
    print(
        "Merged analysis uses one dataset (V1 + supplement, deduped by run_key). "
        "Tier and model numbers shift slightly because supplement adds more cells "
        "at intermediate temperatures and top_p values, not because the method changed."
    )


if __name__ == "__main__":
    main()
