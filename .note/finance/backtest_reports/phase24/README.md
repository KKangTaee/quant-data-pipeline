# Phase 24 Backtest Report Archive

## 목적

이 폴더는 `Phase 24 New Strategy Expansion`에서 나온 개발 검증용 report를 모아 두는 archive다.

여기 report는 신규 전략의 투자 성과를 확정하는 문서가 아니다.
`quant-research` 전략 문서에서 출발한 새 전략이 `finance` 코드와 DB-backed runtime에서 실제로 실행 가능한지 확인하는 문서다.

## 현재 문서

- `PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md`
  - `Global Relative Strength` 전략의 core simulation, sample helper, runtime wrapper가 실제로 import / compile / DB-backed smoke run을 통과하는지 확인한 report
  - 이 문서는 core/runtime first pass 검증에 집중한다
- `PHASE24_GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE_VALIDATION.md`
  - 같은 전략이 `Backtest` UI, compare, history payload, saved replay override까지 연결되는지 확인한 report
  - 남은 항목은 실제 Streamlit 화면에서 사용자가 수행하는 manual QA다
