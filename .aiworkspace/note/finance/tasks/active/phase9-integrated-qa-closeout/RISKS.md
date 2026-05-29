# Phase 9 Integrated QA Closeout Risks

| Risk | Mitigation |
| --- | --- |
| Phase 9 docs show complete before QA passes | Run verification first and record exact results |
| Generated/local artifacts are accidentally committed | Keep `.DS_Store`, run history, registries, saved setup, and artifacts unstaged |
| Phase 9 overstates investability | Closeout notes should say this strengthens evidence gates, not that it approves real trades |
| Phase 10 scope gets mixed into closeout | Leave Phase 10 as handoff only |

## Residual Risks

- Phase 9 does not implement a full execution simulator or broker-grade market impact model.
- Weighted / saved mix sources may still need deeper component-level aggregation for turnover / net cost curve proof.
- Profile-specific liquidity / capacity thresholds remain a future refinement.
- Phase 10 should address walk-forward, out-of-sample, and regime split robustness before calling a strategy production-grade.
