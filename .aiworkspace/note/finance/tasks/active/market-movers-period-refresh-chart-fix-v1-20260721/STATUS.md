# Status

Status: Complete
Completed: 2026-07-21

## Roadmap Position

- 1차 진단·정책 확정: 완료
- 2차 bounded refresh·신규 상장 eligibility·차트 구현: 완료
- 3차 실제 수집·build·browser QA·문서 정렬: 완료
- broader Market Movers 기능 roadmap: `4/5차`; 5차 sector conditional outlook은 historical episode와 OOS publication gate 이후 별도 진행

## Delivered

- Weekly는 필수 1주 앞에 1주 overlap을 더하고 Monthly는 필수 1개월 앞에 1개월 overlap을 더해 최신 완료 시장일까지 수집한다.
- stale limited-history 종목도 다시 수집하며, 최신 상태이지만 선택 기간 시작일보다 실제 첫 가격일이 늦은 신규 상장 종목은 `selected period history unavailable`로 랭킹에서 제외한다.
- 가격 차트에 실제 날짜 X축 눈금을 추가하고 가격·재무 tooltip을 고점에서는 아래로 배치해 상단 잘림을 방지했다.
- 재무 차트의 exact 결산일 hover, 분기/연간 X축, scrollbar·pointer drag·keyboard 탐색 계약을 유지했다.

## Verification Summary

- Market Movers service contracts: `89 passed`
- Market Movers decision UI contracts: `27 passed`
- Vite production build: success
- Actual weekly S&P 500 refresh: 503/503 symbols, 5,533 rows, 0 failures, 138.11 seconds
- Browser: weekly ranking basis moved from `2026-07-07` to `2026-07-20`; subsequent manual refresh showed `최신 503개 스킵 가능` and a new manual-refresh timestamp
- Browser: price date ticks, price hover, financial quarter ticks, exact period-end tooltip, no top clipping confirmed

## Commits

- `c4e5bdd3` 변동 종목 기간별 가격 보강 범위를 수정
- `13f0b921` 변동 종목 신규 상장 기간 제외 근거를 추가
- `230804fd` 변동 종목 차트 날짜축과 호버 표시를 개선
- `05a4dff6` 재무 차트 툴팁을 가시 영역에 고정
