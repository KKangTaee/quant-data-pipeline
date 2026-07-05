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
- Current status: 4차 pending.
