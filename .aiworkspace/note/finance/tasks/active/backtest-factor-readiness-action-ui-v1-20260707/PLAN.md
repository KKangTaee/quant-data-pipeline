# Backtest Factor Readiness Action UI V1

Status: Done
Date: 2026-07-07

## 이걸 하는 이유?

Quality / Value strict form의 Factor Readiness가 `Requested / Covered / INFO / REVIEW` 같은 내부 진단값 중심으로 보여서, 사용자가 정상 백테스트를 위해 무엇을 고쳐야 하는지 바로 알기 어려웠다.

## Scope

- Strict factor preset 안내는 후보군 선택 맥락만 짧게 표시한다.
- Factor Readiness React component는 `문제 / 영향받는 티커 / 해결 방법` 중심으로 다시 구성한다.
- 가격 보강과 statement 보강이 가능한 경우 같은 패널에서 수동 실행 버튼을 제공한다.
- provider/source gap은 반복 업데이트 버튼이 아니라 수동 확인 문제로 표시한다.

## Non-Goals

- OHLCV provider 교체
- DB schema 변경
- universe 선정 정책 변경
- strategy runtime / factor 계산 변경
- registry / saved JSONL rewrite
- live approval / broker order / auto rebalance 의미 추가
