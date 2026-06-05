# Overview Market Sentiment V1 Plan

## 이걸 하는 이유?

Overview는 이미 market movers, futures, events, data health를 묶어 현재 시장 상태를 읽는 화면이다. CNN Fear & Greed와 AAII bearish sentiment는 후보 검증 자체가 아니라 시장 심리 context이므로, Overview에 저장 데이터 기반으로 노출한다.

## Scope

- 1차: CNN Fear & Greed와 AAII Sentiment Survey를 수집해 `finance_meta.macro_series_observation`에 저장한다.
- 1차: `Workspace > Overview > Sentiment` 탭에서 현재값, trend, source freshness, missing/stale 상태를 표시한다.
- 1차: `Workspace > Ingestion`과 Overview 화면에서 manual refresh를 제공한다.
- 1차: Overview Data Health에 Market Sentiment target을 추가한다.

## Out Of Scope

- Practical Validation gate / blocker 연결은 2차로 남긴다.
- live trading signal, order, approval, auto rebalance는 추가하지 않는다.
- 별도 `sentiment_series_observation` table은 만들지 않는다.

## Done

- 수집기는 idempotent UPSERT를 사용한다.
- UI는 provider 실패 / stale / missing을 숨기지 않는다.
- CNN / AAII source 차단 시 job result에 실패 source를 남긴다.
- service contract tests와 Browser QA를 통과한다.
