# Today Home React Workbench V2 Status

Status: Complete
Roadmap: 4/4 complete
Last Updated: 2026-07-22

## Completed

- V1 Today가 React가 아닌 `st.markdown` HTML/CSS primary renderer임을 확인했다.
- 경제사이클과 S&P 500의 React/Vite component ownership과 visual pattern을 비교했다.
- 사용자가 `A. Market Context Workbench` 방향을 선택했다.
- 판단 근거 좌측선 제거, text color + explicit signal/risk label을 승인했다.
- 전체 typography를 승인 시안 대비 1px 확대하기로 했다.
- 현재 curve가 최근 60개 일별 저장 종가 기반 unit-value 관측이며 주봉·장중이 아님을 확인했다.
- date-linear X축, cumulative-return Y축, exact tooltip과 기간/주기 표기를 설계했다.
- `today_home_v2`에 source별 signal/risk/data-quality label, 최근 거래일 수익률의 정확한 두 날짜, 일별 저장 종가 curve metadata를 추가했다.
- Today 본문 전체를 typed React/Vite component로 구현하고 canonical `component_static/` build를 포함했다.
- Python wrapper가 React를 primary로 렌더링하고 allow-list event를 기존 Market Context, Market Movers, Portfolio Monitoring 화면으로 연결한다.
- React 불가 시에만 기존 read-only HTML을 fallback으로 유지한다.
- 전 구간 양수/음수일 때 Y축이 반대 부호 영역을 만들지 않도록 zero baseline을 보정했다.
- desktop, 760px, 420px에서 horizontal overflow가 없고 모바일 date tick이 3개로 축소됨을 확인했다.
- actual root `/`에서 console warning/error 0건과 Market Context 이동을 확인했다.

## Verification Summary

- Today Python contract: `26 passed`, subtests `2 passed`
- 기존 Institutional / Reference / Portfolio Monitoring 회귀: `114 passed`, subtests `67 passed`
- React Vitest: `5 passed`
- TypeScript typecheck와 Vite production build 통과
- `py_compile`, `git diff --check` 통과
- Browser: 1280/760/420, horizontal overflow 0, clean console, action route 확인

## Next

- 이 task의 필수 후속은 없다.
- 주봉/장중 데이터, 기존 상세 탭 개편, 포트폴리오 계산 변경은 별도 승인 범위다.
