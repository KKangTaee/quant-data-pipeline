# Phase 5 Practical Investment Readiness Policy

## 목적

- 이 문서는 Phase 5 이후 `finance` 프로젝트를
  **직접 투자 판단에 참고 가능한 수준의 백테스트/연구 환경**으로
  끌어올리기 위한 운영 원칙을 정리한다.
- 목표는 자동매매 시스템이 아니라,
  사용자가 결과를 읽고 실제 투자 의사결정에 참고할 수 있는
  **실전형 decision-support research environment**를 만드는 것이다.

## 목표 수준

이 프로젝트가 지향하는 실전형 수준은 아래와 같다.

1. 전략이 실제로 어떤 유니버스에서 실행되었는지 설명 가능해야 한다
2. 가격 최신성 부족, stale symbol, factor coverage 부족을
   실행 전후로 명확히 알 수 있어야 한다
3. 결과가 좋아 보여도
   point-in-time / survivorship / freshness 한계를 같이 읽을 수 있어야 한다
4. preset 이름과 경고 정보가 함께 읽혀서
   실제 usable state를 오해하지 않게 해야 한다
5. 사용자가 결과를 보고
   “왜 이렇게 나왔는지”를 추적할 수 있어야 한다

## managed universe 운영 원칙

현재 strict managed preset은
**historical backtest 타당성**을 우선하는 방향으로 운영한다.

### 기본 원칙

- source universe:
  - `United States`
  - `stock`
  - `profile filtered`
  - `market_cap DESC`
- target universe size:
  - `100`
  - `300`
  - `500`
  - `1000`

### historical-backtest policy

기본 정책은 아래다.

1. preset ticker list는 run-level에서 고정한다
2. selected end date 기준 stale 여부로
   run 전체 universe를 미리 교체하지 않는다
3. 각 rebalance date마다
   - 가격이 있는 종목
   - factor snapshot이 usable한 종목
   만 자연스럽게 후보로 남긴다

예:

- `CADE`가 `2026-01-30`까지 가격이 있으면
  `2026-01` rebalance에서는 여전히 후보가 될 수 있다
- 그러나 `2026-02-27` 시점에 가격이 없으면
  그 시점부터 자연스럽게 후보에서 빠진다
- 이 과정에서 run 전체 universe를
  `1001`, `1002`, `1003`으로 미리 대체하지 않는다

### transparency policy

실전형으로 갈수록 data 상태는 조용히 숨겨지면 안 된다.

따라서 현재는 교체가 아니라
**경고와 해석 가능성**을 우선한다.

보여줘야 하는 정보:

- selected end date
- stale / missing symbol count
- first stale / missing symbols
- common latest / newest latest / spread
- strict preset이 historical semantics라는 설명

## stale symbol에 대한 현재 해석 원칙

stale symbol은 아래 중 하나일 수 있다.

- local ingestion gap
- upstream source gap
- symbol change / corporate action
- likely delisted
- confirmed delisted

현재 구현 수준에서는
**freshness를 진단/경고 레이어로 사용**하는 것이 우선이다.

중장기적으로는 아래 진단 레이어를 추가하는 것이 바람직하다.

- `local_ingestion_gap`
- `source_gap`
- `likely_delisted_or_symbol_changed`
- `confirmed_delisted`

즉:

- 운영용 경고는 먼저 freshness로 처리하고
- 원인 분류는 그 위에 별도 진단 레이어로 추가한다

## 실전형 백테스트 해석 원칙

이 프로젝트에서 “실전용”은 아래를 뜻한다.

- 과거 구간에서 그 당시 usable했던 종목을 가능한 한 자연스럽게 포함한다
- stale price / factor coverage issue가 숨겨지지 않는다
- selection, rejection, overlay, cash fallback이 결과에 드러난다
- preset이 static list라는 점과
  실제 rebalance-date candidate filtering이 별도라는 점을 읽을 수 있다

이 프로젝트에서 아직 포함되지 않는 것은 아래다.

- 완전한 live trading automation
- broker execution integration
- 완전한 point-in-time universe membership reconstruction
- corporate action / delisting metadata의 완전한 표준화

즉 현재 목표는:

- “바로 자동매매하는 시스템”이 아니라
- **사용자가 백테스트를 보고 실제 투자 판단을 내릴 수 있을 정도로
  데이터 상태와 전략 동작이 투명한 연구 시스템**

## 중요한 한계

실전형으로 가더라도 아래 한계는 계속 명시해야 한다.

1. managed universe가 현재 시점 market-cap ranking을 사용하면
   survivorship bias가 완전히 사라지지 않는다
2. freshness 경고만으로는
   상폐/심볼변경/소스누락 원인을 완전히 구분하지는 못한다
3. factor 전략은 여전히 factor definition / accounting coverage / filing timing에 민감하다
4. risk overlay가 추가되어도
   first pass는 month-end only일 수 있으며 intramonth 방어는 별도 단계다

## Phase 5 실행 기준으로의 번역

Phase 5에서 “실전형”을 위해 우선 고정할 원칙은 아래다.

1. strict managed preset은 run-level static universe를 유지한다
2. freshness는 preflight 경고로 유지한다
3. compare / history / interpretation에서
   실제 selection / overlay / cash fallback을 읽을 수 있게 유지한다
4. 실전형 목표는 성능 수치만이 아니라
   **해석 가능성 + 데이터 상태 투명성**까지 포함한다

## 현재 상태와 다음 구현

현재 구현 상태:

- stale-price preflight는 이미 존재한다
- stale symbol은 실제 리밸런싱 날짜에서 자연스럽게 후보에서 제외된다
- managed preset은 run-level static universe를 유지한다

다음 자연스러운 구현은:

1. stale reason classification
2. 필요 시 delisting / symbol-change 진단 레이어
3. 이후에야 별도 investable-now mode가 정말 필요한지 재검토
