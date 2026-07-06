# Futures Macro Evidence / Original Data UX Status

## 2026-07-06

- Scope accepted: user approved 1차~5차 execution with `개발 -> QA -> 커밋` repeated.
- Overall roadmap: 1차 역할 분리, 2차 과거점검 의미 정리, 3차 원본표 구조 개선, 4차 React-원본표 연결, 5차 최종 QA/docs.
- Phase 1 status: complete. React evidence drawer is now titled `현재 근거`; lower Streamlit disclosure is now `계산 근거 / 원본 표` and no longer repeats the React evidence interpretation caption.
- Phase 1 QA complete: RED/GREEN focused unittest, `py_compile`, and `git diff --check` passed.
- Phase 2 status: complete. Historical validation summary now reads as `현재 해석의 과거 일관성`, uses `비슷한 과거 상태`, separates directional applicability, and removes `과거 발생` / `과거 점검 요약` / `PIT 날짜` from user-facing app copy.
- Phase 2 QA complete: RED/GREEN focused tests, FuturesMacroThermometer contract class, React payload contract check, `py_compile`, and `git diff --check` passed.
- Phase 3 status: complete. Raw tables now read in calculation order: `현재 점수 -> 구성 기여 -> 선물 일봉 변화 -> 과거 표본`, with matching expander names and a compact raw-table map above the dataframes.
- Phase 3 QA complete: RED/GREEN source contract, scaffold contract, FuturesMacroThermometer contract class, `py_compile`, and `git diff --check` passed.
- Phase 4 status: complete. React evidence items now preserve and render `score_label`, `symbol`, and `contribution_z`, so top evidence can be compared with lower score-contribution/raw tables.
- Phase 4 QA complete: RED/GREEN payload and React source contracts, evidence service contracts, `py_compile`, `git diff --check`, and React `npm run build` passed.
- Phase 5 status: complete. Final QA/docs updated ROADMAP, PROJECT_MAP, flows README, Overview runbook, root handoff logs, and task records.
- Phase 5 QA complete: final focused contract suite, `py_compile`, React `npm run build`, `git diff --check`, and Browser QA passed for rendered React validation labels plus opened lower `계산 근거 / 원본 표` DOM. Screenshot saved as `browser-qa-futures-macro-evidence-original-data-phase5.png` and left uncommitted as generated QA artifact.
- Final state: 1차~5차 complete. Remaining follow-up is only optional improved iframe click automation for opening the React `현재 근거` details; DOM/source/build contracts cover the metadata render path.
- Follow-up UX clarification complete: React command / 자료 기준 now labels the futures daily date as `CME/yfinance 일봉 세션 기준`, and score chips show polarity hints such as `+ 금리 부담 확대 · - 금리 부담 완화` so positive / negative values read as directional pressure rather than generic good / bad.
- Follow-up QA complete: RED/GREEN focused contracts, FuturesMacroThermometer contract suite, `py_compile`, React `npm run build`, and Browser QA passed. Screenshot saved as `browser-qa-futures-macro-session-basis-score-hints.png` and left uncommitted as generated QA artifact.
- Follow-up flow clarification complete: React flow tabs now start with `1D` before `1W` / `1M`, so the current standardized score can be compared against recent 1-trading-day raw moves before checking 5D and 20D context.
- Follow-up flow QA complete: RED/GREEN flow-context contracts, focused 26-test Futures Macro suite, `py_compile`, `git diff --check`, and Browser QA passed. Screenshot saved as `browser-qa-futures-macro-1d-flow-tab.png` and left uncommitted as generated QA artifact.
- Historical validation UX follow-up Phase 1 complete: React payload now carries an explicit `validation.insight` contract that frames historical validation as `오늘과 비슷했던 과거 상태 확인`, including current state, similar historical sample, directionality applicability, and confidence effect.
- Historical validation UX follow-up Phase 2 complete: the React command strip now keeps only data refresh / reload actions, while the historical validation action lives inside the dedicated `오늘과 비슷했던 과거 상태 확인` panel with its own explanation and CTA.
- Historical validation UX follow-up Phase 3 complete: the validation insight now includes a `현재근거와 연결` bridge card, summarizing current evidence counts so users can read historical validation as a check on the current evidence, not a separate module.
- Historical validation UX follow-up Phase 4 complete: when React is available, the lower `계산 근거 / 원본 표` disclosure no longer repeats the historical validation summary and instead explains that it is for source / score / futures daily raw-table tracing.
- Historical validation UX follow-up Phase 5 complete: validation payload now carries chart-readiness metadata for similar-state frequency and forward-return distribution, without rendering graphs yet. ROADMAP, PROJECT_MAP, root logs, and task records are aligned.
- Historical validation component split complete: the React historical validation panel now lives in `src/HistoricalValidationPanel.tsx` with a local `MetricTile` helper. The Streamlit custom component boundary, Python action dispatch, copy, layout classes, and user-facing behavior are unchanged.
- Historical validation card-section follow-up complete: the React historical validation panel is now visually separated as an independent `과거 점검` section card with header, state tiles, action control, and result tiles. Calculation / DB / Python action boundaries are unchanged.
- React section boundary follow-up complete: one Streamlit custom component / iframe is still used, but the internal React surface now separates `MacroContextSection`, `RecentFlowSection`, and `HistoricalValidationPanel` so the UI reads as `매크로 컨텍스트`, `최근 흐름`, and `과거 점검` blocks.
