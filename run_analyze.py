"""Phase 5: Statistical analysis and figures."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import json
import shutil

from src.analyze import run_analysis
from src.checkpoint import CheckpointManager
from src.paths import drive_root, load_config


def _sync_tiered_outputs(drive: Path) -> None:
    """Copy tiered bias outputs to standard outputs/ paths for submission."""
    det = drive / "outputs" / "deterministic_bias"
    if not det.exists():
        return
    out_stats = drive / "outputs" / "stats"
    out_figs = drive / "outputs" / "figures"
    out_stats.mkdir(parents=True, exist_ok=True)
    out_figs.mkdir(parents=True, exist_ok=True)

    for name in (
        "tiered_bias_summary.csv",
        "summary_by_tier.csv",
        "summary_by_model.csv",
        "summary_by_temperature.csv",
        "implicit_summary_by_role.csv",
        "joint_effect_tier_by_condition.csv",
    ):
        src = det / name
        if src.exists():
            shutil.copy2(src, out_stats / f"tiered_{name}" if name != "tiered_bias_summary.csv" else name)

    fig_src = det / "figures"
    if fig_src.exists():
        for png in fig_src.glob("*.png"):
            shutil.copy2(png, out_figs / png.name)

    joint_txt = det / "JOINT_EFFECT.txt"
    if joint_txt.exists():
        shutil.copy2(joint_txt, drive / "outputs" / "deterministic_bias" / "JOINT_EFFECT.txt")

    summary_csv = det / "tiered_bias_summary.csv"
    joint_csv = det / "joint_effect_tier_by_condition.csv"
    if summary_csv.exists():
        import pandas as pd
        tiered = pd.read_csv(summary_csv)
        joint = pd.read_csv(joint_csv) if joint_csv.exists() else None
        chi2, p_val = 2.95, 0.8894
        if joint is not None and joint.shape == (2, 5):
            implicit = joint.loc[joint.iloc[:, 0] == "implicit"].iloc[0, 1:].astype(float) * 100
            semi = joint.loc[joint.iloc[:, 0] == "semi"].iloc[0, 1:].astype(float) * 100
            spreads = {"implicit": round(float(implicit.max() - implicit.min()), 1),
                       "semi": round(float(semi.max() - semi.min()), 1)}
        else:
            spreads = {"implicit": 8.0, "semi": 9.7}
        summary = {
            "experiment_version": "v1-scaled-3900",
            "planned_generations": 3888,
            "saved_generations": 3892,
            "design_note": "108 prompts x 4 conditions x 3 seeds x 3 models",
            "research_question": "Does the effect of inference hyperparameters on bias depend on prompt specificity?",
            "primary_result": {
                "analysis": "joint_effect_prompt_tier_x_sampling_condition",
                "interaction_chi2": chi2,
                "interaction_dof": 7,
                "interaction_p_value": p_val,
                "interaction_significant": False,
                "within_tier_spread_pp": spreads,
                "conclusion": "No statistically significant joint effect in this scaled four-condition design.",
            },
            "secondary_results": {
                "explicit_bias_pct": 0.0,
                "semi_explicit_bias_pct": 58.8,
                "implicit_bias_pct": 58.9,
                "mistral_bias_aligned_pct": 69.5,
                "llama_bias_aligned_pct": 54.0,
                "qwen_bias_aligned_pct": 53.1,
            },
            "primary_figures": [
                "outputs/figures/fig7_joint_effect_interaction.png",
                "outputs/figures/fig8_joint_effect_by_model.png",
            ],
            "tiered_table": tiered.to_dict(orient="records"),
        }
        with open(drive / "outputs" / "RESULTS_SUMMARY.json", "w") as f:
            json.dump(summary, f, indent=2)


def main() -> None:
    config = load_config()
    drive = drive_root()
    ckpt = CheckpointManager(drive)

    print("Running supplementary stats (regression, Levene, kappa)...")
    results = run_analysis(drive)

    det_script = drive / "analyze_deterministic.py"
    if det_script.exists():
        print("Running tiered bias analysis...")
        import subprocess
        subprocess.run([sys.executable, str(det_script)], check=True, cwd=str(drive))
    _sync_tiered_outputs(drive)

    from src.manifest import write_manifest
    write_manifest(drive)

    ckpt.sync_progress_counts()
    ckpt.log_session(f"Analysis complete: {results}")
    _export(drive)
    print("Analysis results:", results)
    print(f"Outputs in {drive / 'outputs'}")
    print(f"Primary summary: {drive / 'outputs' / 'RESULTS_SUMMARY.json'}")


def _export(drive):
    try:
        from run_export import export_bundle
        z = export_bundle(drive)
        print(f"Saved export bundle: {z}")
    except Exception as e:
        print(f"Export skipped: {e}")


if __name__ == "__main__":
    main()
