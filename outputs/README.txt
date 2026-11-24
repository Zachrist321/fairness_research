OUTPUTS FOLDER
==============

Primary results (use these in the report/presentation):

  RESULTS_SUMMARY.json           — headline tiered bias numbers
  stats/tiered_bias_summary.csv  — explicit / semi / implicit rates
  stats/tiered_summary_by_tier.csv
  stats/tiered_summary_by_model.csv
  stats/tiered_summary_by_temperature.csv
  stats/tiered_implicit_summary_by_role.csv
  figures/fig1–fig6.png          — all presentation plots

Supplementary analysis (regression, embeddings):

  stats/mixed_effects.txt
  stats/levene_test.csv
  stats/cohens_kappa.csv
  stats/descriptive_stats.csv      — LLM-judge scores (near-zero floor)
  results_merged.csv

Detailed per-story annotations:

  deterministic_bias/gender_default_annotations.csv
