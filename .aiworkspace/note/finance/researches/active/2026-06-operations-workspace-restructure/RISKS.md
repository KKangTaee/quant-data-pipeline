# Risks

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Research output is mistaken for approved roadmap | High | Keep recommendation as evidence until user approval. |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Streamlit top navigation may not support a clean nested IA | Medium | Add `Operations Overview` first and keep existing routes. |
| Navigation/copy changes can drift from docs | Medium | Use `finance-doc-sync` after approved implementation. |
| Operations Overview may need data from multiple helpers | Medium | Build read-model adapter instead of mixing UI logic directly. |
| Removing raw/archive views too soon can hurt auditability | High | Demote before delete; preserve developer expanders or archive links. |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| No user analytics for Operations page usage | Delete/demote decisions need caution | Treat first pass as additive IA, not removal. |
| No Browser QA screenshots in this research pass | Layout and visual hierarchy are not visually validated | Run Browser QA only after a concrete UI task is approved. |
| External product pages are public docs/marketing | Detailed IA and permissions are partly inferred | Use patterns, not literal copying. |
| Legacy registry usage is unclear | Some old tools may still be needed for audit/replay | Inventory registry read/write paths before removal. |

## Product Boundary Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Moving Selected Dashboard back under Backtest | High | Keep post-selection monitoring under Operations. |
| Leaving archive tools as peer Operations tabs | Medium | Add Overview / Archive Recovery lane. |
| Adding account/order/rebalance automation during IA cleanup | High | Keep no-live boundary explicit and out of scope. |
| Automatic monitoring log writes | Medium | Keep manual save semantics unless explicitly approved. |

## Open Questions

- Should the visible top-level page remain `Ops Review`, or should a new `Operations Overview` page become first in the Operations group?
- Should `Selected Portfolio Dashboard` be renamed in UI to `Portfolio Monitoring` while keeping route compatibility?
- Should Archive/Recovery be a visible section on the Overview page only, or should it become a navigation subgroup if Streamlit supports the desired shape?
- Which legacy registries are still needed by active users versus kept only for audit compatibility?
