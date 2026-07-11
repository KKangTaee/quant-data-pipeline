# Overview Market Movers Top Actions / Monthly History V1 Plan

## 이걸 하는 이유?

Market Movers 비-Daily 화면의 `가격 이력 갱신` 버튼 안에 수집 대상, 기간, 긴 원인 문구가 함께 들어가 행동명이 묻힌다. Monthly 갱신 후에도 FDXF/HONA처럼 실제 provider 가용 이력이 짧은 신규 종목이 계속 재수집 대상으로 남아 같은 경고와 버튼이 반복된다. 사용자는 버튼을 짧게 읽고, 실제 보강 가능한 문제와 기다려야 하는 짧은 이력 문제를 구분할 수 있어야 한다.

## 잠정 개발 차수

1. 상단 action 문구를 `짧은 버튼 + 외부 보조 설명`으로 분리한다.
2. Monthly 갱신 후에도 짧은 provider 이력만 남은 종목을 durable issue로 기록한다.
3. preflight가 durable limited-history issue를 재수집 대상에서 제외하고 별도 상태로 설명한다.
4. 현재 FDXF/HONA 상태를 backfill하고 Browser QA로 Monthly 화면을 검증한다.

## 범위

- Market Movers React 상단 action row와 관련 payload/CSS.
- Market Movers EOD refresh preflight/result와 `market_data_issue`의 limited-history issue type.
- `nyse_price_history` freshness summary의 first/latest/row-count evidence.
- 서비스 계약, ingestion contract, Browser QA, durable docs.

## 범위 밖

- S&P 500 membership 계산 또는 Monthly 수익률 계산식 변경.
- FDXF/HONA를 universe에서 임의 제거하거나 과거 가격을 합성하는 작업.
- 새 provider, 새 DB table/schema, 자동 매매/검증/모니터링 의미 추가.

## 완료 조건

- 버튼에는 행동명만 남고 수집 대상/기간 설명은 button 밖에 표시된다.
- full-window 갱신 후에도 row 수가 부족한 symbol은 `limited_price_history` issue로 기록된다.
- 같은 symbol은 이후 preflight에서 반복 갱신 대상이 아니라 `짧은 이력 제외` 상태로 보인다.
- 관련 테스트와 Browser QA가 통과한다.
