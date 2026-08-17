# Market Research Flat Navigation V1 Plan

## 이걸 하는 이유?

Market Research의 경기 국면과 물가·정책을 같은 깊이에서 바로 열고, 모바일 하위 탐색이 본문을 밀어내지 않게 한다.

## Scope

- `경제 사이클` 사용자 노출 label을 `경기 국면`으로 교체
- `물가·정책` canonical sibling view 추가
- economic-cycle workbench 내부 중복 탭 제거
- A안 editorial family/view rail 유지
- 모바일 view rail compact single-row 전환
- focused regression, production build, Browser QA

## Out Of Scope

- macro calculation/data contract 변경
- module body redesign
- sticky/drawer/diagnostic UI

## Stop Condition

두 direct route가 올바른 본문을 열고 360px에서 하위 탐색이 한 줄 compact rail로 동작하며, 자동 검증과 실제 Browser QA가 통과하면 종료한다.

## Detailed Plan

- `docs/superpowers/plans/2026-08-17-market-research-flat-navigation.md`
