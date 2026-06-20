# Overview Market Context Analog / Macro UX V11 Plan

## Goal

`Overview > Market Context`의 `참고: 과거 유사 맥락`과 `Macro 조건 포함 비교`를 prototype-like card stack에서 분석형 읽기 흐름으로 개편한다.

## Scope

- `app/web/overview_dashboard.py`
  - historical analog controls를 과거 유사 맥락 흐름 바로 앞에 배치한다.
- `app/web/overview_ui_components.py`
  - basis ledger를 compact card grid가 아니라 기준 bar / method block / quality strip로 재구성한다.
  - Macro 조건 비교를 broad sample vs conditioned sample 비교 섹션으로 분리한다.
  - 조건 역할을 실제 반영 / 참고 / 제외 / 부족으로 명확히 나눈다.
- `tests/test_service_contracts.py`
  - UI HTML contract가 분석형 구조를 요구하도록 RED/GREEN 테스트를 보강한다.

## Out Of Scope

- historical analog 계산식 변경
- 새로운 provider / FRED / yfinance fetch
- FRED / events / sentiment hard conditioning 추가
- registry / saved JSONL / run_history write
- Final Review / Operations / Backtest core logic 연결

## Steps

1. 기준 컨트롤을 과거 유사 맥락 섹션 흐름 안으로 이동한다.
2. 기준일 / 계산일 / 리더십 / 패턴 / 표본 / 자료 범위를 기준 bar로 재구성한다.
3. 과거 유사 조건 설명을 `현재 기준`, `유사 사례 조건`, `표본 품질`로 나눈다.
4. 결과 요약 문장을 `먼저 볼 점`과 `주의할 점`으로 나눠 읽기 순서를 만든다.
5. `Macro 조건 포함 비교`를 과거 유사 맥락 내부 카드가 아니라 별도 comparison section으로 렌더링한다.
6. Macro 조건 역할을 `표본을 줄인 조건`, `참고 preview`, `이번 계산 제외`, `자료 부족`으로 표현한다.
7. Browser QA와 서비스 contract 테스트로 카드 안 카드 / 작은 텍스트 프로토타입 느낌이 줄었는지 확인한다.

## Completion Criteria

- Broad analog와 Macro conditioned analog가 시각적으로 구분된다.
- 기준 변경이 어떤 참고 통계에 적용되는지 사용자가 바로 이해할 수 있다.
- Macro 조건이 실제 계산 조건인지 참고 정보인지 구분된다.
- 기존 context-only / no prediction / no recommendation boundary가 유지된다.
