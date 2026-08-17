# Institutional Holdings Content-First UI V1 Plan

State: active
Last Updated: 2026-08-17

## 이걸 하는 이유?

`Research > Institutional Holdings`는 기관별 13F 맥락, 분기 리뷰, 전체 보유와 종목
역조회를 제공하지만, 현재 dark studio rail에 기관 검색, 기관 목록, 다섯 목적지와 데이터
상태가 함께 몰려 있다. 다른 Research surface의 `핵심 요약 -> 근거 탐색 -> 다음 행동`
흐름과 시각 구조가 다르고, 검색 뒤 다른 기관을 선택하면 검색 상태가 선택을 다시
덮어써 전환이 멈추는 회귀도 있다.

이번 task는 사용자가 승인한 `Market Research + Today` content-first 하이브리드로
화면을 정렬하고, 기관 선택을 반복해도 현재 선택과 본문이 일치하도록 만든다.

## 전체 Roadmap

### 1차 — 설계와 상태 계약 확정

- A안 content-first 구조, 기관 선택 동작, refresh와 오류 경계를 문서화한다.
- 완료 조건: 사용자 승인 설계가 모순이나 결정 누락 없이 기록되고 검토된다.

### 2차 — 선택 신뢰성과 content-first shell 구현

- 검색 뒤 기관 전환이 되돌아가는 상태 충돌을 먼저 regression test로 고정한다.
- dark studio rail을 상단 manager control, 수평 research tabs, content-first canvas로 바꾼다.
- 완료 조건: Bill Ackman 검색/선택 뒤 다른 curated manager로 연속 전환할 수 있고,
  선택 기관·헤더·본문·active state가 항상 같은 CIK를 가리킨다.

### 3차 — 반응형·접근성·Browser QA와 문서 정렬

- desktop, tablet, 420px에서 overflow와 탐색 가능성을 확인한다.
- focused automated suite, production component build와 실제 Browser QA를 완료한다.
- 완료 조건: QA screenshot과 task run 기록이 남고 필요한 durable flow 문서가 현재
  구현과 일치한다.

## In Scope

- manager search / select state bug fix
- content-first page header와 compact manager selector
- horizontal research destination tabs
- selected / pending / error / freshness presentation
- existing overview, quarter review, holdings, security와 popularity view의 새 shell 수용
- desktop / tablet / mobile responsive and accessibility behavior
- focused Python / React regression, production component build와 Browser QA

## Out Of Scope

- SEC 13F 수집, amendment, quarter review 계산 또는 DB schema 변경
- 새로운 provider, background refresh, 자동 SEC 요청 또는 scheduler
- manager 비교 화면, favorite 편집 또는 watchlist 정책 변경
- 포트폴리오 지표·수익 proxy 정의 변경
- Market Research, Today 또는 Portfolio Monitoring 자체 UI 변경

## Stop Condition

- 승인된 A안 구조가 실제 Institutional Holdings 화면에 반영된다.
- manager search 뒤 다른 manager 선택이 첫 클릭에 성공한다.
- 좌측 full-height active line과 dark studio rail이 제거된다.
- 기존 다섯 research destination과 명시적 13F refresh 기능이 보존된다.
- focused automated tests와 actual Browser QA가 통과한다.
