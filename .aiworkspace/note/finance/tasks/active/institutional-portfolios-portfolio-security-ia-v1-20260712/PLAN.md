# Institutional Portfolios Portfolio / Security IA V1 Plan

Status: Completed
Started: 2026-07-12

## 이걸 하는 이유?

현재 `Institutional Portfolios`의 1차 탭은 `요약 / 전체 보유 / 보유 기관 조회 / 기관 보유 랭킹`을 같은 레벨로 보여준다.
하지만 앞의 두 탭은 선택한 기관의 포트폴리오를 보는 흐름이고, 뒤의 두 탭은 선택한 티커 / 기업을 기준으로 여러 기관을 보는 흐름이다.

이 task의 목적은 기능을 크게 늘리지 않고 IA를 정리해 사용자가 지금 `기관 포트폴리오`를 보는지, `종목 분석`을 보는지 바로 알게 하는 것이다.

## Scope

- React workbench 1차 탭을 `포트폴리오` 그룹과 `종목 분석` 그룹으로 나눈다.
- `보유 기관 조회` 탭은 `종목 상세`로 바꾸고, 차트 / 기업 정보 / 현재 포트폴리오 비중 / 보유 기관 리스트를 이 안에 유지한다.
- `기관 보유 랭킹`은 `종목 분석` 그룹의 보조 탐색 탭으로 둔다.
- 포트폴리오 비중 / 전체 보유 / 성과 row 클릭은 `종목 상세` view로 이동한다.

## Non-Goals

- DB schema 변경.
- 새 provider / 외부 사이트 fetch.
- live trading / 추천 / broker / auto rebalance 연결.
- 보유 기간 계산 신규 지표 추가. 이번 task는 기존 `보유 기관` 의미의 IA 정리다.

## Verification

- TDD source contract test로 탭 그룹과 `security` view 전환을 검증한다.
- `tests.test_institutional_portfolios`, `py_compile`, React `npm run build`, `git diff --check`를 실행한다.
- Browser QA에서 그룹 탭과 종목 상세 이동을 확인한다.
