# Runs

- 2026-07-11: active storage audit — source 2 rows, validation 2 rows, final decision 6 rows, Monitoring setup 3 rows, legacy reusable saved portfolio 2 rows.
- 2026-07-11: single candidate dry run — `GRS Liquid Macro Top2` stored-period runtime replay PASS, 125 portfolio rows / 125 benchmark rows, current Practical Validation score 9.1, workspace / review roles present.
- 2026-07-11: atomic rebuild — source 6 rows, validation 6 rows, schema-v3 final decision 6 rows, Monitoring setup 3 rows. All six replay PASS / `READY_FOR_FINAL_REVIEW` / monitoring candidate ready.
- 2026-07-11: read-model invariant check — all source / validation / decision / dashboard references valid; old IDs absent; investment report role counts no longer collapse to `final_decision_input=10`.
- 2026-07-11: focused unittest 5개 PASS: Practical Validation workspace 2개, Final Review Level2 disposition / scorecard 2개, Selected Dashboard CRUD 1개.
- 2026-07-11: py_compile PASS; `git diff --check` PASS.
- 2026-07-11: Browser QA blocked by localhost URL security policy before page read/reload. No workaround attempted.
