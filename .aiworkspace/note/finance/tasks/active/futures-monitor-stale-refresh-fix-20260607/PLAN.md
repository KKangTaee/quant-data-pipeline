# Futures Monitor Stale Refresh Fix 2026-06-07

Status: Active

## 이걸 하는 이유?

`Workspace > Overview > Futures Monitor`에서 `Refresh Futures OHLCV`를 실행해도 선물 차트와 데이터가 갱신되지 않는 간헐 현상의 원인을 찾고, 저장된 최신 선물 캔들이 화면에 안정적으로 반영되게 한다.

## Scope

- 원인 추적: Futures Monitor 수집 / 저장 / 로더 / UI refresh 경계 확인
- 코드 범위: `app/services/futures_market_monitoring.py`, 관련 contract test
- 문서 범위: active task 기록과 root handoff log만 최소 갱신

## Stop Condition

- stale / sparse provider 상황에서도 저장된 최신 futures candle window를 읽는 회귀 테스트가 실패 후 통과한다.
- 기존 Futures Monitor 수집 / ingestion job contract test가 계속 통과한다.
- UI render path가 외부 provider를 직접 호출하지 않는 경계를 유지한다.

## Out Of Scope

- 새 provider 추가, DB schema 변경, 자동 OS scheduler 변경
- Macro Thermometer scoring 로직 변경
- registry / saved JSONL / generated QA 이미지 정리
