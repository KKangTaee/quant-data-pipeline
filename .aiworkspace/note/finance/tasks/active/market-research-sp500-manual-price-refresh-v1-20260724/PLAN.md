# Market Research S&P 500 Manual Price Refresh V1 Plan

Status: Implementation Ready
Last Updated: 2026-07-24

## 이걸 하는 이유?

`Market Research > 지수 가치평가 > S&P 500`은 저장된 `^GSPC` EOD를 현재 가격 기준으로 사용하지만, 현재 화면에는 최신 완료 NYSE 거래일과 DB 가격 기준일을 비교하는 freshness 계약과 사용자가 직접 복구할 수 있는 action이 없다.

그 결과 화면은 `2026-07-16` 가격을 사용하면서도 `READY`로 표시됐고, `2026-07-23`까지 정상 제공되는 provider 자료를 사용자가 화면에서 갱신할 방법이 없었다.

이번 작업은 브라우저 진입 시 DB 자료의 최신성을 판단하고, 뒤처졌을 때만 사용자가 명시적으로 `^GSPC` / `SPY` EOD를 수집한 뒤 가치평가를 다시 계산하도록 만든다.

## Goal

- 최신 완료 NYSE 거래일과 저장된 SPX 가격 기준일을 비교한다.
- 가격 자료가 뒤처졌을 때만 `최신 데이터로 다시 계산` action을 표시한다.
- action은 기존 DB ingestion 경계를 통해 `^GSPC` / `SPY` EOD만 수집한다.
- 수집 후 DB 최신성을 다시 확인하고, 성공했을 때만 캐시를 비우고 새 평가를 표시한다.

## Scope

1. S&P 500 가격 freshness read model
2. S&P 500 전용 수동 EOD refresh action
3. React stale 안내, 실행 상태, 결과 반영
4. service/job/component 회귀 테스트와 실제 Browser QA
5. active task 및 durable finance 문서 정렬

## Non-Goals

- macOS `launchd`, cron, heartbeat 등 백그라운드 자동 실행
- raw job, row count, provider log 중심 진단 패널
- Shiller 월간 자료의 수동 refresh action
- FOMC SEP 또는 S&P Index Earnings의 수동 refresh action
- 공식 EPS source 확보 정책 변경
- 가치평가 산식, bucket, threshold 변경

## Roadmap

### 1차 — Freshness Contract

- 목적: 화면 진입 시 저장 자료가 최신 완료 장 기준인지 판정한다.
- 범위: NYSE calendar, S&P valuation service/read model, service tests
- 완료 조건: current / stale / missing / 장중 / 주말·휴장 상태가 결정적으로 판정된다.

### 2차 — Manual Refresh Action

- 목적: stale 상태를 사용자가 화면에서 직접 복구한다.
- 범위: overview action facade, Streamlit event handler, React component, action tests
- 완료 조건: stale일 때만 버튼이 보이고, `^GSPC` / `SPY` 수집 후 DB 재검증과 캐시 초기화를 거쳐 새 결과를 표시한다.

### 3차 — QA And Documentation

- 목적: 실제 사용 흐름과 운영 계약을 검증하고 문서를 정렬한다.
- 범위: focused/full tests, TypeScript/build, desktop/mobile Browser QA, finance docs/task docs
- 완료 조건: 실제 DB가 최신 완료 장까지 갱신되고, 버튼 전후 화면과 실패 유지 동작이 확인되며, 생성 QA artifact는 커밋하지 않는다.

## Stop Condition

S&P 500 화면이 저장된 SPX 가격일을 최신 완료 NYSE 거래일과 비교하고, stale 또는 missing일 때만 수동 action을 제공하며, action 성공 후 최신 가격 기준의 가치평가를 다시 표시하면 종료한다.
