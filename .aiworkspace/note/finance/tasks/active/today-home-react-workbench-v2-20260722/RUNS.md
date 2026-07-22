# Today Home React Workbench V2 Runs

## 2026-07-22 Design Investigation

- V1 Today renderer와 recent commit을 확인했다.
- 경제사이클 / S&P 500 `declare_component`, TSX, CSS, Vite package를 확인했다.
- Portfolio Monitoring daily group curve와 existing ValueChart axis/tooltip implementation을 추적했다.
- Visual companion에서 A/B/C 방향, risk-label 수정, +1px typography, chart-semantics 수정안을 순차 승인받았다.

## 2026-07-22 Implementation And Verification

- written spec 승인 후 `IMPLEMENTATION_PLAN.md` 순서대로 service contract, chart presentation, React UI, Streamlit adapter를 RED/GREEN으로 구현했다.
- service RED: signal fields/schema 부재 3 failures; GREEN: Today 전체 19 passed 당시 확인.
- component adapter RED: wrapper/module/routing 부재 7 failures; GREEN: focused 6 passed + 2 subtests.
- React presentation RED: all-positive domain lower bound `-0.192`; GREEN: 5 passed.
- 최종 Today Python contract: `26 passed`, subtests `2 passed`.
- 기존 연결 surface 회귀: `114 passed`, subtests `67 passed`.
- React: Vitest `5 passed`, `tsc --noEmit`, Vite build `172 modules transformed`.
- actual root `/`: 1280/760/420에서 React primary, risk text, daily/close/intraday labels, responsive tick/overflow를 확인했다.
- 760 inner `717/717`, 420 inner `377/377`, desktop inner `1109/1109` client/scroll width로 horizontal overflow가 없었다.
- 새 browser session console warning/error 0건, `시장 근거 자세히 보기`가 `/overview?overview_tab=market-context`로 이동함을 확인했다.
