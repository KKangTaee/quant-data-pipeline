# RISKS - Product Research Plugin Split

Status: Active
Last Updated: 2026-05-14

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| `finance-task-intake` routes to skills from another plugin | mitigated | Skill names stayed stable and both plugins are registered in marketplace. |
| global mirror points to old source mentally | mitigated | Docs now state product research source lives in `quant-finance-product-research`. |
| script paths become stale | mitigated | Updated `finance-product-research-workflow`, AGENTS, README, ROADMAP, and ran py_compile/dry-run. |
| old plugin still appears to own research because of wording | mitigated | Removed product research wording from old plugin manifest and current docs. |
| plugin split looks like product roadmap approval | Medium | Keep split scoped to tooling/source management only. |
