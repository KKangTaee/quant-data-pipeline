# Overview Market Intelligence Plan

Status: Closeout
Created: 2026-05-28

## 이걸 하는 이유?

현재 `Workspace > Overview`는 지금까지 백테스트와 후보 검토로 쌓은 portfolio candidate의 운영 우선순위를 보여준다.
이 흐름은 유지 가치가 있지만, 사용자가 매일 앱을 열었을 때 "미국 시장에서 지금 무엇이 강한가", "어떤 sector / industry가 좋은가", "곧 있는 큰 이벤트는 무엇인가"를 한 화면에서 확인하기에는 부족하다.

이 phase의 목적은 Overview를 후보 운영 현황만 보는 화면에서, DB-backed market intelligence entry point로 확장하는 것이다.

## Scope Lock

포함한다.

- Coverage 1000 / 2000 기준 daily / weekly / monthly top movers
- S&P 500 기준 intraday previous-close daily movers
- yearly top movers period
- monthly sector / industry leadership
- effective market date, stale data, returnable coverage 표시
- 기존 candidate priority / funnel / next actions / recent activity 보존
- Overview tab 구조 추가
- 무료 데이터 원칙 문서화
- FOMC official calendar collector
- bounded earnings free-source prototype

포함하지 않는다.

- 유료 API 사용
- Overview render 중 외부 provider / 웹사이트 직접 호출
- earnings calendar production collector 또는 full coverage earnings scan
- broker order, live approval, auto rebalance
- top movers를 자동 current candidate로 승격
- heatmap polish

## Free Data Policy

- Market movers와 sector / industry leadership은 기존 MySQL price/profile data를 읽는다.
- 외부 데이터 수집이 필요한 calendar 데이터는 `Ingestion -> DB/cache -> loader/service -> Overview` 흐름을 따른다.
- FOMC는 Federal Reserve official page를 무료 official source로 본다.
- Earnings는 무료 library / 웹 파싱 prototype이 가능하지만 source confidence를 `vendor` 또는 `unofficial`로 표시한다.
- Overview의 refresh button은 직접 scraping하지 않고 ingestion job wrapper를 호출해 DB snapshot을 갱신한다.

## First Build Done Criteria

- `Market Movers`, `Sector / Industry`, `Events`, `Candidate Ops` tab이 생긴다.
- `Market Movers`는 S&P 500 / Coverage 1000 / 2000, daily / weekly / monthly / yearly, Top N을 지원한다.
- `Sector / Industry`는 monthly 기준 sector / industry Top N을 지원한다.
- `Events`는 FOMC와 bounded earnings prototype row를 표시한다.
- latest raw date가 sparse/null인 경우 effective usable market date를 별도로 선택한다.
- 기존 candidate ops 내용은 `Candidate Ops`에서 계속 볼 수 있다.
- focused compile/test와 browser smoke를 실행한다.

## Follow-Up Scope

- Heatmap or treemap visualization
- Earnings official-source cross-check, stale estimate cleanup, broader low-frequency collection cadence
