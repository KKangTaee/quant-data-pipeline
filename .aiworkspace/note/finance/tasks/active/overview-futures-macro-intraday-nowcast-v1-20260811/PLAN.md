# Overview Futures Macro Intraday Nowcast V1 Plan

Last Updated: 2026-08-11

## 이걸 하는 이유?

`선물 매크로`는 지금 선물시장이 어떻게 재가격화되는지 파악하는 화면이지만,
현재 구현은 거래 중인 세션을 화면 전체에서 제외하고 마지막 완료 일봉만 보여준다.
완료 일봉 보호는 과거 검증과 확정 forecast에는 필요하지만 현재 관측까지 전일 기준으로
고정하면 사용자는 `일봉 갱신`을 실패로 받아들이고 장중 변화도 확인할 수 없다.

## Goal

거래 중에는 저장된 최신 완료 5분봉으로 1D / 5D / 20D 현재 관측을 `장중 잠정`으로
계산하고, 미래 5D 검증과 immutable forecast history는 마지막 완료 일봉 기준으로
분리한다. 비거래 시간이나 장중 자료가 적격하지 않을 때는 마지막 완료 일봉으로
fail-closed fallback한다.

## 전체 Roadmap

1. **명세 확정**
   - 장중 관측, 완료 관측, 미래 검증의 소유 경계와 화면 문구를 고정한다.
   - 완료 조건: `DESIGN.md` 사용자 승인.
2. **장중 nowcast 구현**
   - bounded 2d/5m 수집, DB-only 장중 aggregate, 잠정 1D/5D/20D read model과
     React 표시를 구현한다.
   - 완료 조건: 테스트에서 장중·비거래·stale·partial·마감 후 전환을 모두 통과한다.
3. **실환경 검증과 문서 정렬**
   - production component build, desktop/mobile Browser QA, canonical flow/data 문서와
     task closeout을 정렬한다.
   - 완료 조건: 최신 stored data 화면에서 기준 시각과 잠정/확정/검증 구분이 명확하고
     오류·가로 overflow가 없으며 관련 테스트가 통과한다.

현재는 전체 3차 중 1차 명세 확정 단계다.

## In Scope

- `최신 데이터 갱신`에서 현재 pending futures session의 bounded 2d/5m 수집
- 저장 5분봉의 공통 완료 bar cutoff와 session-to-date aggregate
- 마지막 완료 일봉 이력에 장중 synthetic row를 붙인 1D/5D/20D 잠정 계산
- 장중 잠정, 확정 기준일, 데이터 기준 시각과 freshness 표시
- 1D / 5D / 20D 현재 관측과 미래 5D 검증의 시각적 분리
- `NO_EDGE`를 표본 부족과 구분하는 사용자 문구
- incomplete/stale provider data의 last-good fallback

## Out Of Scope

- 장중 row를 `futures_macro_snapshot` 또는 `futures_macro_forecast_history`에 저장
- 장중 상태를 입력으로 한 5D 확률, analog forecast 또는 publication gate
- provider 교체, exchange-grade settlement 또는 realtime feed 보장
- 자동 refresh, websocket, scheduler, trading/monitoring signal
- family 정의, threshold, score 수식 또는 완료 일봉 validation 기준 변경
- 실행 job / row / status 중심 진단 패널 추가

## Stop Condition

- 사용자 서면 명세 승인이 없으면 구현 계획과 production code 변경으로 넘어가지 않는다.
- 장중 forecast 공개나 provider 변경이 필요해지면 현재 task를 확장하지 않고 별도 승인
  범위로 분리한다.
