# Status

## 2026-07-07

- 1차 진행 중: Market Movers non-daily EOD refresh의 smart target / delta refresh 기반 구현.
- RED 확인: 기존 구현은 stale/missing 구분 없이 전체 심볼 full-window 수집을 호출했다.
- GREEN 확인: stale 심볼은 start/end delta, missing 심볼은 full window, current 심볼은 skip하도록 계약 테스트 통과.
