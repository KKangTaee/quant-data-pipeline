# Final Review Liquidity Evidence Copy V1 Plan

## 이걸 하는 이유?

Level3 사용자는 유동성 근거의 의미를 판단해야 하지만 현재 first-read 카드가 내부 enum을 그대로 보여줘 기술 구현을 해석해야 한다. 판정 의미를 유지하면서 사용자가 현재 상태와 통과 기준을 바로 읽게 한다.

## 전체 roadmap

1. `1차`: Decision Brief 표시 adapter와 상태별 계약 테스트 구현
2. `2차`: focused regression, actual Browser QA, 문서 동기화와 커밋

## 범위

- `app/services/backtest_final_review_decision_brief.py`
- 관련 Final Review contract test
- 사용자 흐름 문서와 task closeout 기록

## 중단 조건

- 유동성 Gate나 upstream `proof_status` 의미를 바꿔야 한다면 구현을 중단하고 범위를 다시 확인한다.
- registry / saved JSONL은 수정하거나 stage하지 않는다.
