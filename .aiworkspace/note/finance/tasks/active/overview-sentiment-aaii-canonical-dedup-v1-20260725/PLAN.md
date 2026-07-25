# Plan

## 이걸 하는 이유?

AAII 주간 설문의 과거 HTML 수요일 row와 공식 XLS 목요일 row가 canonical DB에 함께 남아 같은 주차가 두 관측처럼 그래프에 표시된다. 공식 workbook 날짜를 canonical 기준으로 고정하고 기존 중복을 제거해 주간 변화 경로와 표본 수를 정확하게 유지한다.

## Scope

- AAII XLS canonical date-window reconciliation
- TDD regression
- 기존 canonical full-workbook atomic cleanup
- downstream payload 검증
- data/architecture 문서 정렬

## Stop Condition

- immutable snapshot 또는 batch 재작성 필요
- AAII 판정/차트 UX 변경 필요
- official workbook 이외 새 source 도입 필요

상세 설계와 실행 순서는 아래를 따른다.

- `docs/superpowers/specs/2026-07-25-overview-sentiment-aaii-canonical-dedup-design.md`
- `docs/superpowers/plans/2026-07-25-overview-sentiment-aaii-canonical-dedup.md`
