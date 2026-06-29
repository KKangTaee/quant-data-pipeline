# Plan

## Purpose

Market Movers Polish V3 5차는 섹터/시장 확산 맥락을 한글 중심으로 정리하고 반복되는 sector lane 정보를 compact하게 만든다.

## Scope

- Sector breadth headline/detail/status/stat/lane 문구를 한글 표시 언어로 변환한다.
- `Freshness`, `adv / dec`, `positive`, `Top Loser`, `Decliners` 같은 영어 UI 문구를 제거한다.
- Sector lane 영역에 내부 스크롤을 적용해 화면을 과도하게 늘리지 않는다.
- 기존 service/read model과 DB/provider 경계는 변경하지 않는다.

## Completion Criteria

- SP500 Daily sector map에서 한글 headline/detail/lane labels가 보인다.
- SP500 Weekly sector map도 같은 표시 언어를 쓴다.
- NASDAQ empty state와 mobile viewport가 깨지지 않는다.
- 섹터 확산은 context-only 설명으로 유지된다.
