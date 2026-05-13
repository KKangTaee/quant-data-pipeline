# RISKS - Product Research Plugin Stage 5

Status: Active
Last Updated: 2026-05-14

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Product research workflow becomes too rigid | Medium | Scripts only enforce required files and sections; content judgment remains human/Codex-driven. |
| Research output is mistaken for approved roadmap | High | Keep handoff rules in skill: research is evidence, implementation needs user approval. |
| Existing `quant-finance-workflow` plugin grows too broad | Medium | Keep product research orchestration small; consider separate plugin only after more repeated runs. |
| Bootstrap script creates stale boilerplate | Medium | Use concise skeletons and require active audit/benchmark work to fill them. |
| Validation script overclaims quality | Medium | Validate structure, not correctness or recommendation truth. |
| Global mirror drifts from repo-local skill source | mitigated | Synced changed skills to `~/.codex/skills` and ran path diff checks. |
