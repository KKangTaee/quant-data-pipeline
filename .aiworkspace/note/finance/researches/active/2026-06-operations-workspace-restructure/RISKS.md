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

## 2026-06-07 Risk Refresh

Resolved / changed:

- `Operations Overview` is now first in the Operations group, so the old open question about whether to add it is resolved.
- `Selected Portfolio Dashboard` is now user-facing `Portfolio Monitoring`; legacy file / URL names remain for compatibility.
- `Ops Review` is now user-facing `System / Data Health`.

Current risks:

| Risk | Impact | Mitigation |
| --- | --- | --- |
| User-facing Operations Overview still exposes development history / completed roadmap language | Medium | Move roadmap/audit material to docs or keep behind lower-priority reference; lead with portfolio monitoring state. |
| Archive pages remain peer pages in top navigation even after semantic demotion | Medium | Keep pages for recovery, but route users from Overview first; consider nav demotion only after Streamlit constraints are checked. |
| Removing archive tools before registry path audit | High | Inventory read/write and recovery handoff paths before deletion. |
| Adding a new tab for every unclear concept | Medium | Use the rule: new tab only if it answers portfolio state, evidence health, recovery, or report handoff better than existing lanes. |

Updated open questions:

- Can Streamlit navigation support hiding or nesting Archive pages without making recovery too hard?
- Which portfolio-level summary fields are already available from `load_final_selected_portfolio_dashboard()`, and which require runtime read-model extension?
- Should development history remain visible anywhere in the product UI, or move entirely to `.aiworkspace` docs?
