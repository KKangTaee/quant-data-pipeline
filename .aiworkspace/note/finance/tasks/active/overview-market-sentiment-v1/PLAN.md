# Overview Market Sentiment V1 Plan

## 이걸 하는 이유?

Overview는 이미 market movers, futures, events, data health를 묶어 현재 시장 상태를 읽는 화면이다. CNN Fear & Greed와 AAII bearish sentiment는 후보 검증 자체가 아니라 시장 심리 context이므로, Overview에 저장 데이터 기반으로 노출한다.

## Scope

- 1차: CNN Fear & Greed와 AAII Sentiment Survey를 수집해 `finance_meta.macro_series_observation`에 저장한다.
- 1차: `Workspace > Overview > Sentiment` 탭에서 현재값, trend, source freshness, missing/stale 상태를 표시한다.
- 1차: `Workspace > Ingestion`과 Overview 화면에서 manual refresh를 제공한다.
- 1차: Overview Data Health에 Market Sentiment target을 추가한다.
- 1차 후속: Sentiment 탭을 단순 지표 노출에서 `데이터 상태 -> 공포/탐욕 판정 -> CNN 내부 드라이버 -> AAII 비관론 -> 종합 문맥 -> 다음 확인` 순서의 해석 UX로 개선한다.
- 2차: `Backtest > Practical Validation`에 CNN Fear & Greed / AAII sentiment를 시장 심리 context overlay로 표시한다.

## Out Of Scope

- Practical Validation gate / blocker 연결은 하지 않는다. 2차는 context overlay만 추가한다.
- live trading signal, order, approval, auto rebalance는 추가하지 않는다.
- 별도 `sentiment_series_observation` table은 만들지 않는다.

## Done

- 수집기는 idempotent UPSERT를 사용한다.
- UI는 provider 실패 / stale / missing을 숨기지 않고, 데이터 신뢰도와 해석 단계를 함께 보여준다.
- CNN / AAII source 차단 시 job result에 실패 source를 남긴다.
- service contract tests와 Browser QA를 통과한다.
- Practical Validation overlay는 `context_only` boundary를 명시하고, 기존 validation gate / registry / saved setup / live trading 경계를 바꾸지 않는다.
