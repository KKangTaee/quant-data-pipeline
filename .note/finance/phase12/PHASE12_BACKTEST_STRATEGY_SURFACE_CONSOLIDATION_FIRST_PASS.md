# Phase 12 - Backtest Strategy Surface Consolidation First Pass

## 왜 이 작업을 했는가

- `app/web/pages/backtest.py`는 현재도 정상 동작하지만,
  single / compare / history prefill / compare override / strategy label mapping까지
  한 파일에 몰려 있어서 유지보수 부담이 커지고 있었다.
- 특히 quality/value 계열은
  - `Quality Snapshot`
  - `Quality Snapshot (Strict Annual)`
  - `Quality Snapshot (Strict Quarterly Prototype)`
  - `Value Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Quarterly Prototype)`
  - `Quality + Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Quarterly Prototype)`
  처럼 표면에 개별 전략으로 직접 노출되어,
  사용자 입장에서는 family 구조보다 구현 세부명이 먼저 보이는 상태였다.

## 쉬운 설명

- 이번 작업은 전략 자체를 새로 쓴 것이 아니다.
- 대신 화면에서 보이는 전략 목록을
  - `Quality`
  - `Value`
  - `Quality + Value`
  로 단순화하고,
  그 안에서 `Strict Annual`, `Strict Quarterly Prototype` 같은 variant를 고르는 구조로 바꾼 것이다.
- 즉,
  - 전략 **로직**은 그대로
  - 전략 **선택 방식**만 더 관리하기 쉽게 바뀌었다.

## 현재 전략이 실제로 관리되는 위치

- `finance/strategy.py`
  - 시뮬레이션 / 의사결정 레이어
  - 실제 리밸런싱과 포트폴리오 진행 로직
- `finance/sample.py`
  - DB 데이터를 읽어서 strategy-friendly 입력으로 조립하는 레이어
- `app/web/runtime/backtest.py`
  - 웹앱에서 호출하는 DB-backed runtime wrapper
  - result bundle / meta / validation surface 조립
- `app/web/pages/backtest.py`
  - Streamlit UI / form / compare / history orchestration

즉 quality/value 전략이 현재 `backtest.py` 안에서 계산되는 것은 아니다.  
문제가 된 것은 주로 **UI와 orchestration surface가 한 파일에 과도하게 몰려 있던 점**이다.

## 이번 first pass에서 바뀐 것

- 새 파일 `app/web/pages/backtest_strategy_catalog.py` 추가
  - strategy family / variant / concrete strategy key / display name 매핑을 별도 관리
- `Single Strategy`
  - top-level 선택지는 이제
    - `Equal Weight`
    - `GTAA`
    - `Risk Parity Trend`
    - `Dual Momentum`
    - `Quality`
    - `Value`
    - `Quality + Value`
  로 단순화
- `Compare & Portfolio Builder`
  - same family surface 사용
  - family 선택 후 내부 variant를 고르는 구조로 정리
- `History -> Load Into Form`
  - 기존 concrete strategy key를 그대로 읽되,
  - UI는 family + variant 형태로 복원

## 왜 이렇게 했는가

- 현재 코드는 이미 실사용 중이라,
  runtime key나 strategy simulation path를 크게 흔들면 회귀 위험이 크다.
- 그래서 이번 pass는
  - `strategy_key`
  - runtime wrapper
  - sample / strategy 계산 경로
  를 유지한 채,
  **전략 표면만 안전하게 정리하는 방식**을 택했다.

## 이번 pass에서 일부러 하지 않은 것

- quality/value form renderer 전체를 여러 파일로 완전히 분해하지는 않았다.
- 이유:
  - 현재 form 함수들이 `st.session_state`, prefill, compare override와 강하게 연결되어 있어
    한 번에 전부 이동하면 회귀 위험이 커진다.
- 대신 first pass는
  - catalog / selection rule 분리
  - top-level family surface 통합
  - history/prefill compatibility 유지
  까지만 진행했다.

## 다음에 더 할 수 있는 것

- `backtest.py`의 quality/value family renderer를
  family별 별도 파일로 추가 분리
- compare family block도 별도 helper/module로 분리
- strategy surface와 runtime dispatch 사이의 mapping helper를 더 일반화

## 현재 판단

- 이번 구조 변경은
  - 사용자 표면을 더 단순하게 만들고
  - strategy family 개념을 명확히 드러내며
  - 기존 runtime key를 보존하는
  안전한 first pass 리팩터링으로 보는 편이 맞다.
