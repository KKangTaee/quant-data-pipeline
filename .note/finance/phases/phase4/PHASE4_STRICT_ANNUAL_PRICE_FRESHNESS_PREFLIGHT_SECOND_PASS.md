# Phase 4 Strict Annual Price Freshness Preflight Second Pass

## 목적

- strict annual single-strategy preflight를 단순 상태 확인에서 operator 대응 UX까지 확장한다.

## 이번 변경

- `Price Freshness Preflight`가 stale / missing symbol을 보여주는 것에서 끝나지 않고,
  바로 `Daily Market Update`에 넣을 수 있는 refresh payload를 함께 노출하도록 보강했다.
- `refresh_symbols_all`을 runtime helper에서 계산해 UI가 실제 대응 대상 전체를 볼 수 있게 했다.
- strict annual forms는 현재 선택한 preset이
  - public default인지
  - compare/light preset인지
  - staged operator preset인지
  바로 읽을 수 있는 status note도 같이 보여준다.

## 의미

- strict annual large-universe 실행 전
  stale symbol을 operator가 바로 재수집할 수 있게 되었다.
- final-month duplicate row나 shifted row가 보였을 때
  문제를 전략 로직이 아니라 daily price freshness 관점에서 먼저 점검하는 흐름이 더 명확해졌다.

## 현재 상태

- `US Statement Coverage 300`:
  - current public default
- `US Statement Coverage 100`:
  - compare/light preset
- `US Statement Coverage 500`, `US Statement Coverage 1000`:
  - staged operator preset

