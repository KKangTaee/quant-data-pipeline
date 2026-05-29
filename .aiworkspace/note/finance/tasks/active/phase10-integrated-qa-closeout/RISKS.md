# Phase 10 Integrated QA Closeout Risks

| Risk | Mitigation |
| --- | --- |
| Phase 10 docs show complete before QA passes | Run verification first and record exact results |
| Generated/local artifacts are accidentally committed | Keep `.DS_Store`, run history, registries, saved setup, and artifacts unstaged |
| Phase 10 overstates investability | Closeout notes say this strengthens validation evidence gates, not that it approves real trades |
| Phase 11 scope gets mixed into closeout | Leave Phase 11 as handoff only |

## Residual Risks

- Phase 10 does not implement a full walk-forward optimizer or ML hyperparameter governance platform.
- OOS holdout and regime split thresholds are compact deployable-fit heuristics, not formal statistical proof.
- Macro regime split depends on available DB-backed macro observation history and current bucket thresholds.
- Phase 11 should address portfolio construction risk controls before treating selected candidates as operationally robust.
