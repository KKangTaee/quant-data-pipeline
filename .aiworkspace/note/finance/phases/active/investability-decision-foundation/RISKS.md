# Investability Decision Foundation Risks

Status: Active
Created: 2026-05-28

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Gate too strict before provider coverage matures | Useful candidates may be blocked too often | Introduce structured waiver only after explicit policy, expiry, and review trigger exist |
| Gate too loose | Current validation weakness returns under a new UI label | Default selected route remains blocked on critical gaps |
| Evidence packet too verbose | User ignores the most important blockers | Keep packet compact and rank critical gaps first |
| "실전 검토 통과 후보" still sounds too strong | User may confuse it with investment approval | Repeat no-live boundary in Final Review and Selected Dashboard |
| Monitoring timeline becomes another log sprawl | JSONL storage problem repeats | Make monitoring snapshot explicit and compact; no automatic save without approved automation policy |

## Data Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Provider data stale or partial | Operability / exposure evidence may mislead | Track collected_at, as_of_date, coverage_status, staleness; stale snapshot downgrades PASS to REVIEW |
| Current ETF snapshot treated as historical truth | Look-ahead / PIT interpretation weakens | Disclose current snapshot limits; future task can add as-of snapshot id |
| Web crawler source changes | Ingestion breaks silently | Use source map, parser version, and failed-parse status |
| Free API unavailable | Coverage gaps remain | Allow verified crawler through ingestion layer, not UI |
| Raw data accidentally lands in JSONL | Registry becomes heavy and hard to govern | Keep raw provider / holdings / macro data in DB only; look-through board stores compact summary / top rows only |
| Raw robustness experiment output lands in JSONL | Validation result becomes heavy and encourages overfit-by-recording | Keep Robustness Lab to compact summary rows; raw run history and strategy-specific perturbation artifacts stay out of workflow registries |
| Future persistence helper bypasses storage governance | JSONL sprawl returns under a new feature name | Require task plans to classify new persistence against `docs/data/STORAGE_GOVERNANCE.md` |

## Implementation Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Backtest / Practical / Final Review files conflict with active cleanup tasks | Merge and QA cost rises | Keep task write scopes explicit and use integration review before broad changes |
| Existing legacy registries confuse source chain | User may not know which record is canonical | Breadcrumb always starts from Clean V2 source / validation / decision chain |
| Waiver field becomes free-form memo storage | Policy weakens and storage noise returns | Waiver, if added, must be structured and minimal |
| Report export starts before gate contract stabilizes | Dossier may encode unstable semantics | Defer report work until gate hardening lands |

## Open Decisions

- Should structured waiver be allowed at all, or should critical gaps always block selected route?
- Which diagnostics are critical for each validation profile?
- Is paper observation mandatory for every selected route, or only for specific strategy / product types?
- Should current provider snapshot be acceptable, or should final decision require an as-of snapshot id?
- What is the minimum monitoring obligation after a waived or watch-level selection?
