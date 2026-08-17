# Institutional Holdings Hybrid Quarter Review V1 Plan

## 이걸 하는 이유?

현재 Institutional Holdings는 SEC 통합 13F ZIP을 사용자가 직접 지정해 적재할 수
있지만, 기본 URL이 이전 dataset으로 고정되어 있고 저장된 자료가 최신 분기인지
달력 기준으로 판단하지 못한다. 개별 대가의 새 13F가 EDGAR에 공개되어도 SEC 통합
ZIP이 나오기 전에는 화면을 갱신할 수 없다.

사용자는 실시간 시세처럼 계속 확인하는 기능을 원하지 않는다. 저장된 최신 보고
분기와 공식 제출 일정을 로컬에서 비교해 갱신 시점에만 버튼을 보여주고, 명시적으로
버튼을 눌렀을 때 공개 자료 확인·다운로드·DB 반영을 한 번에 끝내야 한다. 새 분기가
들어오면 직전 보고 포트폴리오가 다음 분기와 공개일 사이에 어떤 결과를 냈고 어떤
종목이 `NEW / ADD / KEEP / REDUCE / DROP`으로 바뀌었는지도 함께 설명해야 한다.

## 전체 Roadmap

### 1차 — 로컬 일정 기반 갱신 필요성

- 목적: 탭 진입 시 외부 요청 없이 새 분기 갱신 가능 시점을 판단한다.
- 범위: 공식 13F 제출일 계산, DB 최신 보고분기 비교, UI status/action contract.
- 완료 조건: 아직 제출 시점이 아니면 버튼을 숨기고, 최신 저장 분기가 뒤처졌다면
  정확한 대상 분기의 `업데이트 확인 및 갱신` 버튼을 노출한다.
- 다음 연결: 버튼 command가 2차 hybrid source discovery를 호출한다.

### 2차 — EDGAR 개별 공시 + SEC 통합 ZIP 갱신

- 목적: 통합 ZIP 공개 전에는 watchlist 개별 filing을, 공개 후에는 전체 ZIP을 사용한다.
- 범위: source discovery, individual filing parser, amendment resolution, idempotent UPSERT,
  bulk reconciliation, partial-success contract.
- 완료 조건: explicit click 한 번으로 가능한 최신 자료를 반영하고, 완전히 적재된
  manager만 최신 분기로 승격하며 동일 accession 재실행이 중복 row를 만들지 않는다.
- 다음 연결: 두 개의 유효 분기가 생기면 3차 review 계산을 연다.

### 3차 — 두 성과 구간과 보유 변화

- 목적: 새 분기 공개 시 이전 공개 포트폴리오의 결과를 해석한다.
- 범위: 분기말→분기말, filing일→다음 filing일 price proxy, coverage, contribution,
  `NEW / ADD / KEEP / REDUCE / DROP`.
- 완료 조건: 가격이나 identifier가 없는 비중을 0% 수익으로 오인하지 않고
  `READY / LIMITED / NOT_AVAILABLE` coverage와 함께 결정론적으로 계산한다.
- 다음 연결: service payload가 4차 React presentation을 공급한다.

### 4차 — Institutional Holdings 분기 리뷰 UX

- 목적: 사용자가 최신화와 직전 분기 평가를 한 화면 흐름에서 끝낸다.
- 범위: freshness action, progress/result feedback, `분기 리뷰` destination,
  비교 분기 selector, 성과·변화·기여 detail과 responsive layout.
- 완료 조건: 최신이면 불필요한 갱신 버튼이 보이지 않고, 갱신이 필요하면 다음 행동이
  명확하며, 완료 후 최신 transition review로 바로 이어진다.
- 다음 연결: 5차 actual data/browser QA에서 전체 흐름을 닫는다.

### 5차 — 검증과 문서 정렬

- 목적: SEC/DB/UI 경계와 사용자 의미를 실제 환경에서 확인한다.
- 범위: fixture/unit/integration test, actual SEC bounded smoke, actual DB replay,
  desktop/mobile Browser QA, durable docs/runbook sync.
- 완료 조건: focused tests, py_compile, React test/typecheck/build, diff check,
  actual Browser QA screenshot과 문서 closeout이 모두 남는다.

## Scope

- 로컬 제출 일정 기반의 update-due 판단
- explicit click 이후의 SEC 통합 dataset discovery
- watchlist CIK별 EDGAR submissions/filing 수집
- base filing과 amendment를 보존하는 effective quarter resolution
- 기존 manager/filing/holding ledger의 idempotent 갱신과 bulk reconciliation
- 이전→현재 분기의 position change 및 두 성과 proxy
- React-first Institutional Studio의 갱신 action과 분기 리뷰
- 관련 schema/data/flow/runbook 문서 정렬

## Non-goals

- 탭 진입 시 SEC/EDGAR 자동 호출
- 주기 scheduler, 알림 발송 또는 unattended ingestion
- 전체 SEC filer의 개별 EDGAR 수집; 개별 경로는 curated watchlist에 한정
- 실제 펀드 NAV 수익률 추정
- 옵션, 공매도, 현금, hedge 구조를 주식 종가로 대체
- 매수·매도 추천, broker order 또는 auto rebalance

## Stop Condition

사용자가 승인한 설계와 구현 계획이 충돌하거나 amendment semantics, source access,
가격 coverage 때문에 결과를 안전하게 표현할 수 없으면 추측으로 진행하지 않고
active task `RISKS.md`에 기록한 뒤 범위를 다시 확인한다.

## Done Criteria

- 탭 render 자체는 외부 네트워크 요청을 만들지 않는다.
- DB 최신 report period가 공식적으로 제출 가능한 최신 분기보다 뒤처질 때만 primary
  update action이 나타난다.
- 클릭 시 bulk-first discovery 후 bulk 미공개이면 watchlist individual fallback을 사용한다.
- manager별 성공/실패가 격리되고 incomplete filing은 latest pointer를 승격하지 않는다.
- latest/previous effective quarter가 amendment-aware하게 재구성된다.
- 두 performance window가 별도 coverage와 함께 표시된다.
- 변화 label은 share/principal amount 기준이며 reported value 변화를 거래로 해석하지 않는다.
- 실제 DB와 Browser QA를 포함한 검증과 durable doc sync가 완료된다.
