CHECKPOINT FILES — each row = one completed experiment unit

generations.csv        — 3,892 model outputs (3,888 design + 4 pilot rows)
scores_primary.csv     — supplementary LLM-judge scores (0-3)
scores_secondary.csv   — secondary judge subsample (388 rows)
embeddings.csv         — semantic distance vs stereotype references
failures.csv           — logged errors (does not block resume)
*.bak.csv              — backup snapshots every 50 rows

Primary reported results: outputs/RESULTS_SUMMARY.json and outputs/stats/tiered_*.csv
Join key for all tables: run_key
Format: model|prompt_id|temperature|top_p|seed
