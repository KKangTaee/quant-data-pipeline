# Overview Sentiment React UX Status

## 2026-07-07

- User approved staged development for `Workspace > Overview > Sentiment` React UX after analysis.
- Branch/worktree: current `codex/sub-dev`; no new branch created.
- Planned flow: 1차 contract/payload, 2차 React scaffold, 3차 summary/freshness, 4차 drivers/AAII/next checks, 5차 evidence/graphs/docs closeout.
- Generated artifacts, run history, QA screenshots, and `.DS_Store` must remain uncommitted unless explicitly requested.
- 1차 status: complete. Added a tested Python adapter that converts the existing service-owned Sentiment snapshot into a serializable `sentiment_react_workbench_v1` payload. The current Streamlit UI is not replaced yet.
- 1차 QA: focused RED/GREEN payload test, existing Sentiment snapshot contract test, Sentiment `py_compile`, and `git diff --check` passed.
- 2차 status: complete. Added the `sentiment_workbench` Streamlit custom component scaffold, Python wrapper, optional React render path, and React action event bridge for refresh / reload. Existing Streamlit controls remain as fallback when the component build is unavailable.
- 2차 QA: focused RED/GREEN scaffold test, payload contract test, Sentiment `py_compile`, `npm install`, `npm run build`, and `git diff --check` passed. `node_modules` was removed from the worktree after build and must not be committed.
- 3차 status: complete. Reworked the React first viewport around service-owned phase/headline/summary, core metric cards, freshness counts, and refresh/reload actions tied to the stored data basis.
- 3차 QA: focused RED/GREEN summary/freshness surface test and Vite production build passed. New build assets replaced the previous scaffold bundle; `node_modules` was removed again after build.
- 4차 status: complete. Added React sections for CNN / AAII cross-read, service-owned analysis steps, driver lanes, CNN component explanations, and next checks. The frontend displays existing service text and fields without inventing new recommendations.
- 4차 QA: focused RED/GREEN driver/payload tests and Vite production build passed. New build assets replaced the 3차 bundle; `node_modules` was removed after build.
- 5차 status: complete. Added React evidence / graph sections for history line chart, CNN component bars, and stored raw/component/history evidence tables. React-rendered Sentiment no longer duplicates the old Streamlit detail sections; fallback remains available when the component build is absent.
- 5차 QA: focused RED/GREEN evidence-surface test, Vite production build, Browser QA, contrast fix, docs sync, and final regression checks passed. Browser QA screenshots were saved as generated artifacts under this task directory and are intentionally uncommitted.
- Follow-up status: complete. Removed the default next-check card surface from the React workbench and hid next-check analysis steps from the first-pass reading flow. Added history chart y-axis labels, hover guide, focus dot, and tooltip with date / series / value / source.
- Follow-up QA: focused RED/GREEN UI contract tests, Vite production build, Browser QA hover check, screenshot inspection, compile, focused regression, and `git diff --check` passed.
- Feature expansion 1차 status: complete. Extended the service read model with recent range context, CNN / AAII divergence context, and CNN component history change context. React/UI display is not changed in this phase.
- Feature expansion 2차 status: complete. Added a tested React payload `interpretation` contract carrying service-owned `range_context`, `divergence`, and `component_history` without adding frontend-generated interpretation copy.
- Feature expansion 3차 status: complete. Added React UI for recent percentile/range cards and the CNN headline / CNN component / AAII divergence panel inside the cross-read flow. The panel displays service-owned status, summary, and axis details.
- Feature expansion 4차 status: complete. Added a React component-history section that shows each CNN component's latest value, previous/latest dates, change, and service-owned change detail before the graph/evidence section.
- Feature expansion 5차 status: complete. Browser QA confirmed the React iframe rendered 3 range cards, 3 divergence axes, and 7 component-history cards. Durable docs and root handoff logs were synced; QA screenshots remain generated artifacts and are not committed.
- Duplicate-metric follow-up status: complete. Removed the repeated CNN / AAII core metric row from the React cross-read section so the top summary cards are not duplicated before range and divergence context. The cross-read flow now starts with recent range cards, then service-owned divergence analysis.
- Divergence / conclusion layout follow-up status: complete. Reframed the divergence status as a `지표 합의 상태` pill so `뚜렷한 엇갈림` reads as the agreement state between CNN headline, CNN components, and AAII survey. Reworked the five conclusion cards from a fixed 3-column grid to a wrapping flex rail, removing the empty 3x2 visual gap on desktop.
