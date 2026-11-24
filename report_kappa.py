"""Calculate Cohen's Kappa and other agreement statistics between Llama and Gemini judges."""

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score, confusion_matrix

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.paths import drive_root

def main() -> None:
    drive = drive_root()
    
    pri_path = drive / "checkpoints" / "scores_primary.csv"
    gem_path = drive / "checkpoints" / "scores_gemini.csv"
    
    if not pri_path.exists():
        print(f"Primary scores file not found at {pri_path}")
        return
    if not gem_path.exists():
        print(f"Gemini scores file not found at {gem_path}")
        return

    pri = pd.read_csv(pri_path)
    gem = pd.read_csv(gem_path)
    
    # Merge on run_key
    merged = pri.merge(gem, on="run_key", suffixes=("_llama", "_gemini"))
    
    n_overlap = len(merged)
    print(f"Overlap size: {n_overlap} stories")
    if n_overlap == 0:
        print("No overlapping rows to compare.")
        return

    # Extract scores
    y_llama = merged["stereotype_score_llama"].astype(int)
    y_gemini = merged["stereotype_score_gemini"].astype(int)

    # Compute Kappa
    kappa = cohen_kappa_score(y_llama, y_gemini)
    
    # Compute raw agreement
    raw_agreement = (y_llama == y_gemini).mean()

    print(f"Cohen's Kappa: {kappa:.4f}")
    print(f"Raw Agreement: {raw_agreement:.4%}")

    # Score distributions
    llama_dist = y_llama.value_counts().reindex([0, 1, 2, 3], fill_value=0)
    gemini_dist = y_gemini.value_counts().reindex([0, 1, 2, 3], fill_value=0)

    # Confusion matrix
    labels = [0, 1, 2, 3]
    cm = confusion_matrix(y_llama, y_gemini, labels=labels)
    cm_df = pd.DataFrame(cm, index=[f"Llama_{i}" for i in labels], columns=[f"Gemini_{i}" for i in labels])

    # Disagreement cases
    disagreements = merged[y_llama != y_gemini].copy()
    
    # Load generations to get the generated text
    gen_df = pd.read_csv(drive / "checkpoints" / "generations.csv")
    disagreements = disagreements.merge(gen_df[["run_key", "generated_text"]], on="run_key", how="left")

    # Generate Markdown Report
    report = []
    report.append("# LLM Judge Reliability Report: Llama vs. Gemini")
    report.append(f"\n*   **Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"*   **Sample Size:** {n_overlap} stories (drawn from the top 10% highest stereotype similarity scores)")
    report.append(f"*   **Llama Judge Model:** `meta-llama/Llama-3.1-8B-Instruct` (Primary)")
    report.append(f"*   **Gemini Judge Model:** `gemini-2.5-flash` (Secondary)\n")
    
    report.append("## Headline Metrics")
    report.append(f"- **Cohen's Kappa:** `{kappa:.4f}`")
    report.append(f"- **Raw Percent Agreement:** `{raw_agreement:.2%}`\n")
    
    report.append("## Score Distributions")
    report.append("| Stereotype Score | Llama Count | Gemini Count |")
    report.append("|:---:|:---:|:---:|")
    for score in labels:
        report.append(f"| {score} | {llama_dist[score]} | {gemini_dist[score]} |")
    report.append("\n")
    
    report.append("## Confusion Matrix")
    report.append(cm_df.to_markdown())
    report.append("\n")
    
    report.append("## Agreement by Demographic Dimension")
    dims = merged["demographic_dimension_llama"].unique()
    report.append("| Dimension | n | Raw Agreement | Kappa |")
    report.append("|:---|:---:|:---:|:---:|")
    for dim in dims:
        sub = merged[merged["demographic_dimension_llama"] == dim]
        sub_llama = sub["stereotype_score_llama"].astype(int)
        sub_gemini = sub["stereotype_score_gemini"].astype(int)
        sub_raw = (sub_llama == sub_gemini).mean()
        try:
            sub_kappa = cohen_kappa_score(sub_llama, sub_gemini)
            kappa_str = f"`{sub_kappa:.4f}`"
        except Exception:
            kappa_str = "N/A"
        report.append(f"| {dim} | {len(sub)} | {sub_raw:.2%} | {kappa_str} |")
    report.append("\n")

    report.append("## Agreement by Prompt Tier")
    tiers = merged["prompt_tier_llama"].unique()
    report.append("| Prompt Tier | n | Raw Agreement | Kappa |")
    report.append("|:---|:---:|:---:|:---:|")
    for tier in tiers:
        sub = merged[merged["prompt_tier_llama"] == tier]
        sub_llama = sub["stereotype_score_llama"].astype(int)
        sub_gemini = sub["stereotype_score_gemini"].astype(int)
        sub_raw = (sub_llama == sub_gemini).mean()
        try:
            sub_kappa = cohen_kappa_score(sub_llama, sub_gemini)
            kappa_str = f"`{sub_kappa:.4f}`"
        except Exception:
            kappa_str = "N/A"
        report.append(f"| {tier} | {len(sub)} | {sub_raw:.2%} | {kappa_str} |")
    report.append("\n")

    report.append("## Qualitative Disagreements")
    if len(disagreements) == 0:
        report.append("No disagreements found between Llama and Gemini.")
    else:
        report.append(f"There are **{len(disagreements)}** stories where the judges disagreed. Below are examples:\n")
        # Sort disagreements so we show larger differences first
        disagreements["diff"] = (disagreements["stereotype_score_gemini"] - disagreements["stereotype_score_llama"]).abs()
        for idx, row in disagreements.sort_values(by="diff", ascending=False).head(10).iterrows():
            report.append(f"### Example {idx+1}: {row['run_key']}")
            report.append(f"- **Demographic Dimension:** {row['demographic_dimension_llama']}")
            report.append(f"- **Prompt Tier:** {row['prompt_tier_llama']}")
            report.append(f"- **Llama Score:** `{row['stereotype_score_llama']}`")
            report.append(f"  *Llama Justification:* \"{row['justification_llama']}\"")
            report.append(f"- **Gemini Score:** `{row['stereotype_score_gemini']}`")
            report.append(f"  *Gemini Justification:* \"{row['justification_gemini']}\"")
            story_excerpt = str(row['generated_text']).replace('\n', ' ')
            report.append(f"- **Story Excerpt (first 400 chars):** *\"{story_excerpt[:400]}...\"*\n")
            report.append("---")
            
    # Save files
    out_stats = drive / "outputs" / "stats"
    out_stats.mkdir(parents=True, exist_ok=True)
    
    # Save CSV with summary
    pd.DataFrame([{
        "cohens_kappa": kappa, 
        "raw_agreement": raw_agreement,
        "n_overlap": n_overlap,
        "n_llama_nonzero": (y_llama > 0).sum(),
        "n_gemini_nonzero": (y_gemini > 0).sum()
    }]).to_csv(out_stats / "cohens_kappa_gemini.csv", index=False)
    
    # Save markdown report
    report_text = "\n".join(report) + "\n"
    (out_stats / "gemini_agreement_report.md").write_text(report_text)
    
    print(f"Saved Cohen's Kappa CSV to {out_stats / 'cohens_kappa_gemini.csv'}")
    print(f"Saved Markdown report to {out_stats / 'gemini_agreement_report.md'}")

if __name__ == "__main__":
    main()
