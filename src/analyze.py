"""Statistical analysis and figure generation."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import levene
from sklearn.metrics import cohen_kappa_score
import statsmodels.formula.api as smf


def merge_results(ckpt_dir: Path) -> pd.DataFrame:
    gen = pd.read_csv(ckpt_dir / "generations.csv")
    pri = pd.read_csv(ckpt_dir / "scores_primary.csv")
    emb = pd.read_csv(ckpt_dir / "embeddings.csv")
    df = gen.merge(pri, on="run_key", how="inner", suffixes=("", "_score"))
    df = df.merge(emb[["run_key", "semantic_distance", "stereotype_similarity"]], on="run_key", how="left")
    return df


def descriptive_table(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["model_name", "prompt_tier", "temperature", "top_p"], dropna=False)
    return g["stereotype_score"].agg(["mean", "std", "count"]).reset_index()


def run_mixed_effects(df: pd.DataFrame):
    df = df.copy()
    df["tier_num"] = df["prompt_tier"].map({"implicit": 1, "semi": 2, "explicit": 3})
    df = df.dropna(subset=["stereotype_score"])
    formula = (
        "stereotype_score ~ temperature * C(prompt_tier) + top_p * C(prompt_tier) + temperature * top_p"
    )
    model = smf.mixedlm(formula, df, groups=df["prompt_id"])
    return model.fit(method="lbfgs", maxiter=200)


def run_levene(df: pd.DataFrame) -> dict:
    tiers = ["implicit", "semi", "explicit"]
    groups = [df.loc[df["prompt_tier"] == t, "stereotype_score"].dropna().values for t in tiers]
    groups = [g for g in groups if len(g) > 1]
    if len(groups) < 2:
        return {"statistic": None, "pvalue": None}
    stat, p = levene(*groups)
    return {"statistic": float(stat), "pvalue": float(p)}


def compute_kappa(primary: pd.DataFrame, secondary: pd.DataFrame) -> float | None:
    merged = primary.merge(
        secondary[["run_key", "stereotype_score"]],
        on="run_key", suffixes=("_a", "_b"),
    ).dropna(subset=["stereotype_score_a", "stereotype_score_b"])
    if len(merged) < 5:
        return None
    return float(cohen_kappa_score(
        merged["stereotype_score_a"].astype(int),
        merged["stereotype_score_b"].astype(int),
    ))


def save_figures(df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    # Fig 1: heatmap temperature x top_p by tier
    for tier in df["prompt_tier"].unique():
        sub = df[df["prompt_tier"] == tier]
        pivot = sub.pivot_table(
            values="stereotype_score", index="temperature", columns="top_p", aggfunc="mean",
        )
        plt.figure(figsize=(8, 5))
        sns.heatmap(pivot, annot=True, fmt=".2f", cmap="RdYlGn_r", center=1.5)
        plt.title(f"Mean Stereotype Score — {tier} prompts")
        plt.tight_layout()
        plt.savefig(out_dir / f"fig1_heatmap_{tier}.png", dpi=150)
        plt.close()

    # Fig 2: score by tier and temperature
    plt.figure(figsize=(10, 5))
    sns.pointplot(data=df, x="temperature", y="stereotype_score", hue="prompt_tier", errorbar="sd")
    plt.title("Stereotype Score by Temperature and Prompt Tier")
    plt.tight_layout()
    plt.savefig(out_dir / "fig2_score_by_temp_tier.png", dpi=150)
    plt.close()


def run_analysis(drive_root: Path) -> dict:
    ckpt = drive_root / "checkpoints"
    out_stats = drive_root / "outputs" / "stats"
    out_figs = drive_root / "outputs" / "figures"
    out_stats.mkdir(parents=True, exist_ok=True)

    df = merge_results(ckpt)
    desc = descriptive_table(df)
    desc.to_csv(out_stats / "descriptive_stats.csv", index=False)

    results = {"n_rows": len(df)}
    try:
        fit = run_mixed_effects(df)
        with open(out_stats / "mixed_effects.txt", "w") as f:
            f.write(str(fit.summary()))
        results["mixed_effects_ok"] = True
    except Exception as e:
        results["mixed_effects_ok"] = False
        results["mixed_effects_error"] = str(e)

    levene_out = run_levene(df)
    pd.DataFrame([levene_out]).to_csv(out_stats / "levene_test.csv", index=False)
    results["levene"] = levene_out

    sec_path = ckpt / "scores_secondary.csv"
    if sec_path.exists():
        sec = pd.read_csv(sec_path)
        pri = pd.read_csv(ckpt / "scores_primary.csv")
        kappa = compute_kappa(pri, sec)
        pd.DataFrame([{"cohens_kappa": kappa}]).to_csv(out_stats / "cohens_kappa.csv", index=False)
        results["cohens_kappa"] = kappa

    df.to_csv(drive_root / "outputs" / "results_merged.csv", index=False)
    save_figures(df, out_figs)
    return results
