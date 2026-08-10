# Economic Cycle Freshness and Asset Pathway Recovery Plan

## 이걸 하는 이유

경제사이클 수동 최신화의 실제 75.616~96.836초 지연을 줄이고, 별도 자산 경로의 stale DB rows 때문에 측정값 전체가 `자료 부족`으로 사라지는 문제를 해결한다.

## Roadmap

- 1차: bounded concurrent vintage fetch와 deterministic DB write
- 2차: asset refresh, scope freshness, delayed measurement/UI
- 3차: actual refresh, Browser QA, durable documentation

## Completion

- stale scope만 갱신한다.
- delayed last-good measurement는 날짜와 함께 보이지만 현재 신호에서 제외된다.
- 기존 자산 카드 구조와 경제사이클 phase 계산을 유지한다.
