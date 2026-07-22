# Today Home React Workbench V2 Status

Status: Design Review
Roadmap: 1/4 in progress
Last Updated: 2026-07-22

## Completed

- V1 Today가 React가 아닌 `st.markdown` HTML/CSS primary renderer임을 확인했다.
- 경제사이클과 S&P 500의 React/Vite component ownership과 visual pattern을 비교했다.
- 사용자가 `A. Market Context Workbench` 방향을 선택했다.
- 판단 근거 좌측선 제거, text color + explicit signal/risk label을 승인했다.
- 전체 typography를 승인 시안 대비 1px 확대하기로 했다.
- 현재 curve가 최근 60개 일별 저장 종가 기반 unit-value 관측이며 주봉·장중이 아님을 확인했다.
- date-linear X축, cumulative-return Y축, exact tooltip과 기간/주기 표기를 설계했다.

## Current

- Written spec 사용자 검토 대기.

## Next

- spec 승인 후 `writing-plans`로 상세 구현 계획을 작성한다.
- 이후 TDD로 2/4차 React component와 payload contract 구현을 시작한다.
