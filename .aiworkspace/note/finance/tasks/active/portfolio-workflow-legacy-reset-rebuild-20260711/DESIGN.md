# Design

## Source Chain

현재 main chain은 아래 세 registry와 Monitoring saved setup이다.

1. `PORTFOLIO_SELECTION_SOURCES.jsonl`
2. `PRACTICAL_VALIDATION_RESULTS.jsonl`
3. `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`
4. `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`

## Rebuild Direction

- 기존 rows를 최신 형식으로 직접 변환하지 않는다.
- 원본 전략 replay contract 또는 기존 weighted source contract에서 현재 service를 다시 실행한다.
- 새 selection / validation / decision ID를 생성해 구형 레코드와 혼동되지 않게 한다.
- Final Review decision의 operator reason / constraints / next action은 기존 판단 의미를 유지하되 현재 schema boundary를 사용한다.
- live approval, broker order, auto rebalance는 생성하지 않는다.

## Rollback

active JSONL을 변경하기 전에 workspace 밖 임시 디렉터리에 원본 파일 checksum과 사본을 남긴다. 생성 결과가 불완전하면 사본으로 복원하고 작업을 완료 처리하지 않는다.
