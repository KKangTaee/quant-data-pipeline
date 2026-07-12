# Overview Market Context Nasdaq-100 Valuation V1 Plan

Status: Design Review
Last Updated: 2026-07-12

## 이걸 하는 이유?

현재 Market Context의 가치평가 화면은 S&P 500만 지원한다. 사용자는 계정, API token, 유료 데이터 계약 없이 같은 판단 흐름을 Nasdaq-100에도 적용하고 싶다. 무료 공개자료에는 완성된 Nasdaq 공식 index-level EPS/PER history가 없지만, SEC의 QQQ holdings와 기업 actual을 결합하면 출처와 한계를 숨기지 않는 QQQ proxy 가치평가를 만들 수 있다.

## Goal

- `Nasdaq-100 (QQQ proxy)`를 S&P 500 가치평가 화면의 두 번째 index option으로 제공한다.
- Graph 1은 공개 공시로 재구성한 월별 trailing P/E의 최근 60개월 분포를 표시한다.
- Graph 2는 현재 QQQ EPS proxy에 기존 FOMC SEP GDP+PCE 성장률을 적용해 예상 QQQ 가격 구간을 표시한다.
- Graph 2 history는 1년·3년·5년을 제공하되 과거 holdings anchor 품질을 명시한다.
- 모든 원격 수집은 ingestion에서 수행하고 UI는 DB-backed read model만 렌더링한다.

## Five-Stage Roadmap

### 1차 — Public Source Coverage Spike

- SEC N-PORT/N-30B-2 discovery와 parser fixture
- historical holding identity mapping
- diluted EPS/price/weight coverage와 known Nasdaq P/E calibration
- 완료 조건: 60개월 current multiple history와 1/3/5년 rolling warmup에 필요한 월 중 최소 95% weighted coverage

### 2차 — Ingestion / DB / Loader

- SEC holdings backfill과 idempotent UPSERT
- holding identifier columns와 Nasdaq monthly valuation table
- filing-aware TTM EPS와 monthly reconstructed P/E materialization
- 완료 조건: DB에 raw holdings와 derived monthly rows가 저장되고 재실행 결과가 안정적임

### 3차 — Service / FOMC Scenario

- current QQQ EPS proxy resolver
- 60m/36m multiple regime
- latest SEP GDP+PCE expected EPS와 QQQ price band
- 1/3/5년 reconstructed history
- 완료 조건: JSON-safe Nasdaq read model이 S&P와 동일한 핵심 contract를 제공함

### 4차 — React Index Selector

- `S&P 500 / Nasdaq-100 · QQQ proxy` selector
- SPX/QQQ copy와 단위 generic rendering
- public filing reconstruction badge, coverage, basis date, limitation
- 완료 조건: 두 index를 전환해도 각 그래프와 hover/기간 selector가 정상 동작함

### 5차 — Automation / QA / Docs / Commit

- existing Overview automation에 Nasdaq refresh 연결
- focused unit/service contract/DB smoke/Browser QA
- active task와 canonical finance docs 동기화
- generated screenshot은 커밋하지 않음
- 완료 조건: 실제 DB 데이터로 두 graph가 렌더링되고 검증 근거와 남은 위험이 기록됨

## Scope

### In Scope

- QQQ SEC holdings와 SEC company actual 기반 reconstructed P/E/EPS
- existing QQQ EOD, FOMC SEP, S&P React valuation surface 재사용
- 1/3/5년 history와 source-quality 표시

### Out Of Scope

- Nasdaq 공식 index-level P/E라고 표시
- NDX price licensing 또는 Nasdaq GIW/GIFFD 계약
- GuruFocus/FactSet/LSEG/Bloomberg 구매
- analyst consensus EPS
- UI에서 SEC/Invesco/Yahoo 직접 호출
- scraping, login gate 우회, current constituents의 무근거 과거 소급

## Stop Conditions

- weighted EPS/price coverage가 95% 미만이면 production-ready graph로 표시하지 않는다.
- 공개 Nasdaq trailing P/E 관측점 대비 median absolute percentage error가 5%를 넘거나 단일 관측 오차가 10%를 넘으면 `BLOCKED` read model과 원인을 제공하고 공식값처럼 렌더링하지 않는다.
- ADR/복수 클래스 mapping이 설명되지 않은 상태에서 해당 weight를 actual coverage로 세지 않는다.
