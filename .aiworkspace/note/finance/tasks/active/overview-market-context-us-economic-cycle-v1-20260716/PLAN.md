# Overview Market Context U.S. Economic Cycle V1 Plan

Status: Complete — 1차~5차 + actual bootstrap
Last Updated: 2026-07-16

## 이걸 하는 이유?

사용자가 공부한 회복·확장·둔화·침체 프레임을 단순 설명 카드가 아니라, 당시 공개된 미국 거시 데이터로 현재 위치와 1·2개월 후 불확실성을 검증 가능하게 보여주는 제품 기능으로 확장한다. 기존 Market Context의 자산·가치평가 화면은 보존하고, 경제 사이클을 같은 레벨에서 선택할 수 있게 한다.

## Authoritative Documents

- Approved design: [`docs/superpowers/specs/2026-07-16-us-economic-cycle-regime-forecast-design.md`](../../../../../../docs/superpowers/specs/2026-07-16-us-economic-cycle-regime-forecast-design.md)
- Detailed TDD plan: [`docs/superpowers/plans/2026-07-16-us-economic-cycle-regime-forecast.md`](../../../../../../docs/superpowers/plans/2026-07-16-us-economic-cycle-regime-forecast.md)
- Research bundle: [`researches/active/2026-07-us-economic-cycle-regime-forecast/`](../../../researches/active/2026-07-us-economic-cycle-regime-forecast/)

## Tentative Roadmap

1. **1차 — Vintage 데이터 의미·저장 계약**
   - 목적: later revision을 차단하는 raw vintage business key와 strict as-of loader를 만든다.
   - 범위: catalog, DB schema, FRED/ALFRED collector, loader, focused tests.
   - 완료 조건: 과거 origin이 이후 발표·수정값을 읽지 못하고 재수집이 멱등이다.
2. **2차 — 현재 국면 엔진과 과거 history**
   - 목적: 실물·고용 중심 현재 4국면 확률과 설명 근거를 계산한다.
   - 범위: features, labels, h0 model, artifact/snapshot persistence.
   - 완료 조건: 누수 없는 현재 분포와 월별 replay snapshot이 재현된다.
3. **3차 — +1M/+2M 예측·검증**
   - 목적: direct horizon, transition prior, calibration, rolling-origin publication gate를 연결한다.
   - 범위: forecast model, validation, baselines, jobs, materialization.
   - 완료 조건: 각 horizon이 독립적으로 READY/LIMITED 판정을 받고 미승인 확률은 저장·표시되지 않는다.
4. **4차 — Overview UI**
   - 목적: 사용자가 확률·cycle clock·근거·10년 ribbon을 한 화면에서 읽게 한다.
   - 범위: service, `경제 사이클 | S&P 500 | 미국 개별주식` selector, separate React component.
   - 완료 조건: UI는 compact DB snapshot만 읽고 provider/model job을 실행하지 않는다.
5. **5차 — Actual QA·문서 정렬**
   - 목적: actual vintage bootstrap, gate 결과, responsive Browser QA, regression, durable docs를 닫는다.
   - 범위: actual run, desktop/420px QA, data/architecture/runbook/roadmap/task docs.
   - 완료 조건: 검증 통과 horizon만 숫자를 표시하며 관련 회귀와 문서가 일치한다.

명세 승인, 구현 계획, 1차 vintage 데이터 계약, 2차 현재 국면/과거 snapshot 엔진, 3차 horizon별 예측·검증·materialization, 4차 Overview 서비스·선택기·시각화, 5차 actual bootstrap·Browser QA·회귀·문서 정렬까지 완료해 진행률은 `5/5`다. 후속으로 발급된 key를 세션 환경에서만 사용해 17개 시계열 1,232,856행과 121개월 replay를 적재했다. Actual gate는 h0/h1/h2 모두 `LIMITED`이므로 숫자 확률은 공개하지 않는다.

## Scope

- United States only.
- Current, +1M, +2M four-phase probability distributions.
- Vintage-aware raw data, model validation, artifact/snapshot persistence.
- Market Context same-level cycle visualization.
- Exact files, TDD sequence, commands, and gates are in the detailed implementation plan.

## Explicit Exclusions

- 한국/글로벌 복수 국가 모델.
- ADS/WEI separate connector, proprietary leading indicators, paid data.
- dollar/gold/commodity-driven phase label.
- official recession declaration, portfolio gate, trading signal, broker execution, auto rebalance.
- visible ingestion/job diagnostic panel and unattended scheduler.
- validation threshold relaxation to force a READY result.

## Stop Conditions

- `FRED_API_KEY`가 없으면 actual vintage bootstrap만 중단하고 구현·fixture 검증은 계속한다.
- actual rolling-origin gate가 실패하면 해당 horizon을 `LIMITED`로 종료한다. 임의 데이터 합성이나 threshold 완화는 하지 않는다.
- 기존 S&P 500/미국 개별주식 selector 또는 collection behavior가 회귀하면 4차 완료로 처리하지 않는다.
