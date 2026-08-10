# Inflation Policy Data Pipeline Plan

## 이걸 하는 이유?

승인된 화면이 예시 확률이나 기존 경기 사이클 값에 의존하지 않으려면, 공식 자료의
발표 시각과 수집 시각을 보존하는 독립 DB 계약이 먼저 필요하다.

## Scope

- inflation-policy schema family와 macro vintage `released_at`
- generic FRED vintage adapter와 독립 series catalog
- BEA PCE component, FOMC SEP/decision, NY Fed ACM collectors
- strict as-of loader와 result store
- backend refresh orchestration과 실제 source smoke

## Stop Condition

집중 테스트와 실제 2026 source smoke가 통과하고, 2026-07-29 cutoff가 다음 날 PCE를
제외할 때 완료한다.
