# Operations Archive Tabs Removal Plan

## 이걸 하는 이유?

Operations의 정체성을 `Portfolio Monitoring + System / Data Health`로 좁히기 위해, 더 이상 주요 운영 surface로 쓰지 않는 Backtest Run History / Candidate Library archive 탭을 상단 Operations navigation에서 제거한다.

## Scope

- `Operations` top navigation에서 archive page 2개 제거.
- `Operations Overview` read model에서 archive lane / archive action queue 제거.
- archive 데이터 파일, registry, saved setup, helper code는 삭제하지 않는다.
- durable docs는 현재 사용자-facing Operations 구조에 맞춰 동기화한다.

## Non-Goals

- Backtest history / candidate registry 파일 삭제.
- broker order, live approval, account sync, auto rebalance 추가.
- Portfolio Monitoring scenario / saved setup schema 변경.
- Streamlit 외 frontend migration.

## Completion Criteria

- Operations top navigation은 `Operations Overview`, `Portfolio Monitoring`, `System / Data Health`만 포함한다.
- Operations Overview lane은 Portfolio Monitoring / System Data Health만 보여준다.
- archive data / helper path 보존 경계가 문서화된다.
- focused service contract tests, py_compile, doc hygiene checks가 통과한다.
