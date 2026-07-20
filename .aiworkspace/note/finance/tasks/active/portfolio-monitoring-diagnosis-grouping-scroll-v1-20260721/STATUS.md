# Portfolio Monitoring Diagnosis Grouping / Scroll V1 Status

Status: Complete

- 전체 roadmap `3/3차` 완료.
- 1차: Python-owned `DiagnosisDisplayGroup`과 subject/metric metadata를 추가했다. 상관 집중·현재 낙폭만 표시 가족으로 묶고 raw weakness/all_rows/history는 fact 단위를 유지한다.
- 2차: additive workspace/TypeScript contract와 legacy one-member fallback을 연결했다.
- 3차: 그룹 카드, 종목·종목쌍 상세, desktop 560px 내부 스크롤, mobile 자연 스크롤을 구현하고 canonical static build를 갱신했다.
- 검증: Portfolio Monitoring Python 142개, React 31개, typecheck, production build, py_compile을 통과했다.
- Browser QA: desktop component width 1269px에서 취약점 8개 목록 `clientHeight=560`, `scrollHeight=1024`, `overflowY=auto`; mobile width 377px에서 `maxHeight=none`, `overflow=visible`, horizontal overflow 0, console error 0을 확인했다.
- 범위 밖: 새 진단 family grouping, threshold/severity 정책 변경, DB/registry/saved schema 변경, Backtest/전략 진단 변경.
