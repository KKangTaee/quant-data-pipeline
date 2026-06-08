# Risks

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Research output is mistaken for approved roadmap | High | Keep recommendation as evidence until user approval. |
| Reference becomes too broad and loses the current portfolio-selection value | Medium | Preserve current guide as a named journey; add task-first IA around it. |
| Users interpret monitoring guide as live trading readiness | High | Repeat no broker order / no live approval / no auto rebalance boundary in every monitoring section. |
| Help page becomes a wall of text | Medium | Use task cards, compact journey rows, drawers, and search/filter. |
| Docs and UI drift again | Medium | Move guide content to structured rows and update canonical flow docs after implementation. |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Large single-file `reference_guides.py` grows further | Medium | Split static content from render logic in 1차. |
| Service/web boundary violation if catalog imports Streamlit | Medium | Keep catalog Streamlit-free and add/extend py_compile or boundary checks. |
| Streamlit layout text overlap on narrow viewport | Medium | Browser QA desktop and mobile/narrow widths before completion. |
| GraphViz flow remains visually heavy | Low | Keep flow optional or secondary; prioritize scan-friendly journey cards. |
| Search/filter state becomes brittle | Low | Use simple Streamlit controls and stable catalog keys. |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| No user analytics on which Reference questions are most common | Prioritization is based on product audit and recent issues | Start with known stale data / validation / monitoring issues; adjust after use. |
| Portfolio Visualizer official page was not used directly | It is a common portfolio backtesting comparison point | Revisit if an accessible official docs page is needed for later product benchmarking. |
| Browser screenshot capture timed out | Final visual evidence is DOM-based, not image-based | Re-run screenshot during implementation QA after code changes. |
| Glossary content was not deeply audited | 1차 may duplicate terms if Glossary is rich | Audit `Reference > Glossary` before 3차 searchable dictionary. |
| External products change frequently | Benchmark examples may age | Keep source access date and avoid copying vendor-specific UI too literally. |
