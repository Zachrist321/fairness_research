CHECKPOINT FILES — each row = one completed experiment unit

generations.csv      — model outputs (text, temperature, top_p, seed)
scores_primary.csv   — Llama judge stereotype scores (0-3)
scores_secondary.csv — Mistral judge (10% subsample for Cohen's kappa)
embeddings.csv       — semantic distance vs stereotype references
failures.csv         — errors/refusals (does not block resume)
*.bak.csv            — backup snapshots every 50 rows

Join key for all tables: run_key
Format: model|prompt_id|temperature|top_p|seed
