# Institutional Portfolios Two-Tier Tabs V1 Plan

Status: Completed
Started: 2026-07-12
Completed: 2026-07-12

## 이걸 하는 이유?

직전 task에서 `포트폴리오`와 `종목 분석`을 한 줄 안에서 그룹으로 나눴지만, 실제 화면에서는 그룹 라벨과 탭 버튼이 같은 레벨처럼 보여 여전히 어색하다.

이 task의 목적은 기능을 늘리지 않고 탭 IA를 `상위 영역 선택 -> 세부 탭 선택` 구조로 바꿔 사용자가 현재 보고 있는 맥락을 더 쉽게 읽게 하는 것이다.

## Scope

- React workbench navigation을 2단 구조로 바꾼다.
  - 상위 탭: `포트폴리오`, `종목 분석`
  - 포트폴리오 하위 탭: `요약`, `전체 보유`
  - 종목 분석 하위 탭: `종목 상세`, `기관 보유 랭킹`
- 포트폴리오 비중 / holdings / performance drilldown은 계속 `종목 분석 > 종목 상세`로 이동한다.
- 기존 Streamlit shell, service read model, ingestion, DB schema, event id는 변경하지 않는다.

## Stop Condition

- TDD source contract가 2단 탭 구조를 검증한다.
- Focused Python tests, py_compile, React build, git diff check가 통과한다.
- Browser QA에서 상위 탭과 하위 탭이 구분되어 보이고, 종목 클릭 시 `종목 분석 > 종목 상세`가 활성화되는 것을 확인한다.
