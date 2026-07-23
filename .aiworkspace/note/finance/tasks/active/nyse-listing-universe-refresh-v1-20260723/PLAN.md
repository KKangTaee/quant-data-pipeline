# NYSE Listing Universe Refresh V1

Status: Design approved
Date: 2026-07-23

## 이걸 하는 이유?

전체 가격·자산 프로필 수집은 `finance_meta.nyse_stock`과 `finance_meta.nyse_etf`를
symbol source로 사용한다. 두 master의 마지막 NYSE listing snapshot은 2026-05-31이어서,
그 뒤 공식 목록에 들어온 ticker는 전체 수집 대상으로 선택될 수 없다.

사용자가 Ingestion에서 주식·ETF 현재 universe를 한 번에 안전하게 최신화할 수 있게 하여,
신규 상장 ticker가 후속 가격·프로필 수집의 입력으로 자연스럽게 포함되도록 한다.

## 잠정 전체 Roadmap

### 1차 — 기준 경로와 노후화 검증

- 목적: source → master table → 전체 수집 consumer를 확인한다.
- 범위: `finance/data/nyse.py`, `finance/data/nyse_db.py`,
  `app/jobs/symbol_sources.py`, Ingestion source selector, 실제 DB.
- 완료 조건: 마지막 snapshot과 현재 NYSE 공식 목록의 차이를 수치로 확인한다.
- 상태: 완료.

### 2차 — 안전한 universe refresh 구현

- 목적: 주식·ETF 공식 목록을 함께 검증한 뒤 current master와 lifecycle에 저장한다.
- 범위: NYSE collector/writer, ingestion job/dispatcher/registry, 단위·계약 테스트.
- 완료 조건: 비정상 source 응답은 기존 master를 보존하고, 정상 snapshot은 current master를
  canonical replace하며 과거 가격과 lifecycle evidence를 삭제하지 않는다.
- 상태: 대기.

### 3차 — Ingestion 사용자 흐름과 QA

- 목적: 사용자가 전체 가격 수집 전에 universe를 쉽게 최신화한다.
- 범위: Ingestion `일상 운영 / 검증 데이터` 첫 action, 문서, Browser QA.
- 완료 조건: 마지막 갱신 기준과 action이 보이고, 실행 후 최신 master가 후속 symbol source에
  반영되며 자동 테스트와 실제 화면 QA가 통과한다.
- 상태: 대기.

## 이번 작업 범위

- NYSE 공식 listings API의 주식·ETF current snapshot을 한 번에 갱신한다.
- 두 source를 모두 수집·검증한 뒤 DB write를 시작한다.
- `nyse_stock`과 `nyse_etf`는 current listing master로 유지한다.
- `nyse_symbol_lifecycle`에는 current snapshot evidence를 보존한다.
- Ingestion 운영 화면 첫 위치에 compact한 최신화 action을 둔다.
- 완료 결과는 전체·추가·제외 건수와 기준일을 중심으로 안내한다.

## 범위 제외

- 일별 가격 업데이트와 universe refresh의 자동 결합
- scheduler/cron 자동화
- 새 운영 진단 패널 또는 raw status dashboard
- 가격 이력, registry JSONL, saved setup 삭제 또는 재작성
- `financial_advisor` 변경

## Stop Condition

- 주식·ETF source 중 하나라도 비정상이면 기존 current master가 유지된다.
- 정상 refresh 뒤 `NYSE Stocks`와 `NYSE Stocks + ETFs` source가 새 master를 읽는다.
- 관련 자동 테스트, diff check, Browser QA와 문서 sync가 끝난다.
