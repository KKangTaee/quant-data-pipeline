# Product Direction

Status: Active
Last Verified: 2026-05-12

## Product Summary

`finance` 프로젝트는 데이터 수집, 백테스트, 실전 후보 검증, 최종 포트폴리오 선정 이후 모니터링까지 이어지는 퀀트 리서치 워크스페이스다.

현재 제품의 중심은 "좋아 보이는 백테스트 결과"를 바로 투자 판단으로 받아들이지 않고,
데이터 신뢰도, ETF 운용성, holdings / exposure, macro context, stress / sensitivity, Final Review evidence를 통해
실전 추적 가능한 후보인지 확인하는 데 있다.

## Target Experience

- 사용자는 Backtest Analysis에서 전략이나 저장된 포트폴리오 mix를 후보 source로 만든다.
- Practical Validation은 후보를 12개 진단으로 검증한다.
- Final Review는 select / hold / reject / re-review 판단을 남긴다.
- Selected Portfolio Dashboard는 최종 선정된 포트폴리오의 이후 성과와 monitoring signal을 확인한다.
- Ingestion은 백테스트와 Practical Validation에 필요한 DB-backed data snapshot을 수집한다.

## Core Pillars

| Pillar | Meaning |
|---|---|
| Evidence First | 백테스트 수익률보다 데이터 신뢰도와 검증 근거를 우선한다 |
| DB-Backed Runtime | UI에서 직접 원격 fetch하지 않고, ingestion과 loader를 통해 DB 데이터를 사용한다 |
| Practical Validation | 실전 운용 전 ETF 비용, 유동성, holdings, macro, stress, sensitivity를 확인한다 |
| Clear Workflow Boundary | Backtest Analysis, Practical Validation, Final Review, Selected Dashboard의 책임을 분리한다 |
| No Live Trading | 현재 시스템은 live approval, broker order, auto rebalance를 만들지 않는다 |

## Non Goals

- 자동 매매 주문 생성
- broker account holding 자동 연결
- 투자 수익 보장 표현
- 모든 ETF provider를 완전하게 지원하는 universal connector
- 모든 실험 로그와 임시 run artifact를 장기 문서로 보존
- phase 문서와 task 문서를 하나의 무거운 진행 로그로 합치는 것

## Current Product Boundary

현재 사용자-facing 주요 화면:

- `Workspace > Ingestion`
- `Workspace > Overview`
- `Backtest > Backtest Analysis`
- `Backtest > Practical Validation`
- `Backtest > Final Review`
- `Operations > Backtest Run History`
- `Operations > Candidate Library`
- `Operations > Selected Portfolio Dashboard`
- `Reference > Guides`

현재 active development focus:

- Practical Validation V2의 P2 diagnostic normalization 마무리
- 문서 체계 재구성
- 이후 P3 수준의 QA, Final Review handoff, selected monitoring 연결 정리
