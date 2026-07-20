# Reference Center React V1 Notes

## Decisions

- Reference의 제품 가치는 유지하고 Guides / Glossary의 별도 navigation만 제거했다.
- Search-first Hybrid A를 사용하며 검색어를 모르는 사용자는 6개 current journey에서 시작한다.
- 사용자 catalog는 curated 24-item 계약이고 내부 `docs/GLOSSARY.md`는 runtime source가 아니다.
- legacy·개발자 용어와 log/run history/diagnostic UI는 사용자 Reference에서 제외한다.
- 검색, filter, detail, related-item 이동은 React local state이며 Python은 허용된 `navigate_to_surface` intent만 처리한다.
- Backtest destination은 기존 `request_backtest_panel`을 재사용하고 다른 surface는 configured `st.Page` target으로 이동한다.
- invalid deep link는 home payload와 compact changed/removed 안내로 복구한다.

## Implementation Evidence

- Canonical ownership: `app/services/reference_center.py`, `app/web/reference_center.py`, `app/web/reference_center_react_component.py`.
- React ownership: `app/web/streamlit_components/reference_center_workbench/`.
- Contextual help coverage: Overview, Institutional Portfolios, Ingestion, Backtest Analysis, Practical Validation, Final Review, Portfolio Monitoring.
- Deleted active legacy paths: `app/web/reference_guides.py`, `app/services/reference_guides_catalog.py`, `app/services/reference_glossary_catalog.py` and their legacy tests.
- Browser QA found that an auto-height iframe made a fixed drawer as tall as the full catalog. When a lower result was involved, the drawer content could move outside the visible parent viewport. The modal-open frame is now intentionally capped at 760px and the drawer owns its scroll; closing restores automatic full-list height.
- Final integration review caught durable documentation drift in `SCRIPT_STRUCTURE_MAP.md` and `BACKTEST_UI_FLOW.md`; both now describe the single `/reference` architecture and seven-surface contextual-help coverage instead of the deleted Guides / Glossary split.
