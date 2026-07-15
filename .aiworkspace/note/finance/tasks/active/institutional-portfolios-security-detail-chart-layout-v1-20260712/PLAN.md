# Institutional Portfolios Security Detail Chart Layout V1 Plan

Status: Completed
Started: 2026-07-12

## 이걸 하는 이유?

`Workspace > Institutional Portfolios > 종목 분석 > 종목 상세`는 선택 종목 차트와 보유 기관 리스트를 보여주지만, 현재 화면은 차트와 기관 리스트가 2-column으로 나뉘어 종목 상세 흐름이 산만하다. 또한 차트 하단의 기본 range input은 실전 증권 / 거래 앱의 차트 탐색 문법과 달라 어색하게 보인다.

이 task의 목적은 새 provider나 DB 변경 없이 기존 저장 가격 / 13F read model을 더 실사용에 가까운 종목 상세 화면으로 재배치하는 것이다.

## Scope

- 1차: `SecurityDetail`을 2-row 구조로 바꾼다.
  - 상단: 선택 종목 정보, 현재 선택 기관 포트폴리오 내 종목 위치, 차트.
  - 하단: 보유 기관 리스트.
- 2차: chart 하단 기본 range input을 제거하고 금융 차트형 하단 영역으로 바꾼다.
  - time scale, volume bars, draggable-feeling navigator window, crosshair / OHLC strip.
- 3차: 보유 기관 리스트를 하단 full-width scroll panel로 바꾼다.
  - 리스트는 slice로 잘라내지 않고, panel 내부 vertical scroll로 탐색한다.

## Non-Goals

- `lightweight-charts` 신규 의존성 도입.
- 외부 provider / SEC / broker / live trading fetch.
- DB schema, loader, ingestion, selected-security read model 변경.
- 추천, 매수/매도 신호, 실시간 거래 표현 추가.

## Verification

- TDD source contract test로 layout / chart / scroll panel 구조를 검증한다.
- `tests.test_institutional_portfolios`, Python compile, React build, `git diff --check`를 실행한다.
- Browser QA에서 `종목 상세` 화면의 2-row 구조와 scroll holder panel을 확인한다.

## Closeout

- 2026-07-12: 1차~3차를 완료했다.
- 새 provider, DB schema, ingestion, trading / recommendation boundary는 변경하지 않았다.
