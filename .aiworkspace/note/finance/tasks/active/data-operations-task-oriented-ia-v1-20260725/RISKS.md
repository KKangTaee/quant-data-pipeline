# Risks

Status: Open
Updated: 2026-07-25

## Product Risks

- Primary workflow가 너무 단순하면 전문 사용자가 필요한 low-level action을 찾기 어려울 수 있다.
- Advanced catalog가 다시 collector wall이 되면 기존 문제가 반복된다.
- consumer 목적이 겹치는 `daily_market_update`, `metadata_refresh`를 중복 form으로 만들면 drift가 생긴다.
- history 범위를 너무 좁히면 consumer-origin data refresh 추적이 어려울 수 있다.

## Data Risks

- current snapshot을 PIT readiness로 표현하면 안 된다.
- bounded default가 full universe coverage를 조용히 줄이면 안 된다.
- workflow step 순서가 source correctness를 보장하는 것처럼 보이면 안 된다.
- partial success를 전체 workflow 완료로 표현하면 안 된다.

## Engineering Risks

- `_bind_page_globals()` 제거 과정에서 hidden session / helper dependency가 드러날 수 있다.
- 기존 source-string tests가 intentional UI removal을 regression으로 판단할 수 있다.
- page / views / forms 분리를 한 commit에 과도하게 묶으면 회귀 원인 추적이 어려워진다.
- run-history old payload는 workflow ownership metadata가 없어 fallback classification이 필요하다.

## Mitigations

- 3A / 3B / 3C를 distinct implementation unit과 commit으로 나눈다.
- workflow mapping을 pure contract로 먼저 테스트한다.
- action form과 dispatcher는 unique ownership을 유지한다.
- old history는 known job name mapping만 적용하고 unknown은 default UI에서 제외한다.
- desktop/mobile Browser QA에서 first-action visibility와 overflow를 확인한다.

## Deferred Risks

- background queue
- scheduler / cron
- cancellation and resume
- multi-user authorization
- remote deployment operational security

이 항목들은 4차 후보이며 V1 구현 완료 조건이 아니다.
