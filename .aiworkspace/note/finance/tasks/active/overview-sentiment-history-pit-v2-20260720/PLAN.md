# Plan

## 이걸 하는 이유?

Overview Sentiment의 현재 CNN·AAII 해석은 사용할 수 있지만, 같은 날짜의 재수집 값이 canonical table에서 덮어써져 발표 당시 값을 재현할 수 없다. 화면도 최근 180일만 읽기 때문에 장기 축적 상태를 사용자가 확인하기 어렵다. 향후 1W·1M 분석에서 미래 데이터가 섞이지 않도록 지금부터 수집 당시 기록을 보존하고 장기 그래프의 실제 coverage를 드러낸다.

## 전체 잠정 로드맵

1. CNN·AAII 균형 UI와 중복 제거 — 완료
2. 장기 이력과 수집 당시 값의 축적·품질 점검 — 현재 작업
3. 예측 필요성이 유지될 때 독립 데이터 후보 검토
4. point-in-time 검증 후 1W·1M 전망 제공 여부 결정

## 2차 세부 흐름

1. 2-1 현재 coverage, provider window, gap, overwrite, refresh ownership 감사 — 완료
2. 2-2 canonical 최신값 + immutable 수집 당시 기록의 이중 저장 계약 — 승인
3. 2-3 schema, ingestion transaction, as-known loader, daily automation 구현
4. 2-4 `6M / 1Y / 전체` 그래프와 compact coverage evidence, Browser QA
5. 2-5 PIT 축적 상태를 근거로 1W·1M 검증 착수 가능 여부 결정

## 이번 범위

- source별 collection batch와 normalized immutable snapshot schema
- CNN·AAII source-isolated transaction과 canonical compatibility
- 명시적 `known_at` cutoff loader
- 24시간 cadence Overview automation과 기존 manual refresh 유지
- 장기 canonical history 기간 선택과 PIT 시작일/실제 coverage 안내
- focused ingestion, loader, service, frontend regression과 Browser QA

## 이번 범위 밖

- legacy row를 과거 당시 값으로 소급 변환
- raw provider payload 장기 보관
- 신규 심리 source
- 1W·1M 확률 전망 또는 투자 신호
- run/job/row 중심 운영 진단 panel

## 완료 조건

- 동일 날짜 수정값을 재수집해도 이전 snapshot이 남는다.
- UTC cutoff 기준으로 당시까지 관측한 값을 재현한다.
- source 하나의 실패가 다른 source 성공을 막지 않는다.
- canonical current UI와 기존 refresh contract가 유지된다.
- 두 그래프가 공통 `6M / 1Y / 전체` 기간을 사용한다.
- canonical graph range와 PIT accumulation start가 구분된다.
- focused tests, build, diff check, desktop/420px Browser QA를 통과한다.

Authoritative spec: `docs/superpowers/specs/2026-07-20-overview-sentiment-history-pit-v2-design.md`

Executable TDD plan: `docs/superpowers/plans/2026-07-20-overview-sentiment-history-pit-v2.md`

Latest-value follow-up plan: `docs/superpowers/plans/2026-07-20-overview-sentiment-aligned-latest-end.md`

CNN endpoint-label follow-up plan: `docs/superpowers/plans/2026-07-20-overview-sentiment-cnn-endpoint-label.md`
