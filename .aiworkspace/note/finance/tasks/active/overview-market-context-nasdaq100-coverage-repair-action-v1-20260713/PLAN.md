# Overview Market Context Nasdaq-100 Coverage Repair Action V1 Plan

Status: Design Approved — Awaiting Written Spec Review
Last Updated: 2026-07-13

## 이걸 하는 이유?

Nasdaq-100 · QQQ proxy 가치평가는 실제 희석 EPS로 설명되는 보유 비중이 95% 미만이면 의도적으로 차단된다. 현재 화면은 차단 이유를 설명하지만 사용자가 같은 화면에서 부족한 자료를 보강하고 다시 계산할 수 없다. 사용자가 별도 명령을 실행하지 않아도 차단 카드에서 한 번의 action으로 최근 60개월 자료 보강, 재계산, 화면 갱신까지 끝내도록 한다.

## Goal

- Nasdaq coverage blocker에 `60개월 가치평가 자료 보강` action을 제공한다.
- action은 최근 60개월의 과거 편입·퇴출 종목까지 대상으로 누락 EPS와 가격 이력을 선별 보강한다.
- 실행은 현재 Streamlit 화면에서 동기적으로 기다리며 단계별 진행 상태를 표시한다.
- 수집 결과는 종목 단위로 DB에 즉시 저장해 부분 실패 후 재실행을 이어받는다.
- 완료 후 60개월을 재계산하고 cache를 비운 뒤 같은 화면을 자동 재조회한다.
- 모든 월이 95% gate를 통과하면 그래프를 표시하고, 통과하지 못하면 갱신된 coverage와 남은 원인을 표시한다.

## Five-Stage Roadmap

### 1차 — Coverage Repair Plan

- 최근 60개월 holdings/EPS/price 상태를 월별로 진단한다.
- non-equity 보유를 계산 대상에서 제외하고 EPS, price, identity, unsupported-source gap을 구분한다.
- 이미 충분한 종목은 제외한 repeat-safe repair plan을 만든다.

완료 조건: 같은 DB snapshot에서 동일한 대상 symbol/CIK/date range/reason을 반환하는 pure/service contract가 테스트를 통과한다.

### 2차 — Resumable Ingestion / Persistence

- 기존 SEC EDGAR statement ingestion과 OHLCV ingestion을 repair plan 대상에만 적용한다.
- 작은 batch, progress callback, 종목 단위 UPSERT, partial failure evidence를 제공한다.
- 무료 원천에서 제공하지 않는 상장폐지 가격이나 해외 issuer 분기 EPS는 합성하지 않는다.

완료 조건: 중간 실패 뒤 재실행이 이미 저장된 coverage를 재사용하고 중복 business row를 만들지 않는다.

### 3차 — 60-Month Rematerialization / Quality Gate

- 저장된 holdings/statements/prices로 최근 60개월을 다시 materialize한다.
- 월별 weighted coverage 95%, aggregate earnings yield, calibration contract를 그대로 적용한다.
- pass/fail 뒤 최신 read model과 remaining gap summary를 생성한다.

완료 조건: pass면 60개월 graph-ready row가 생성되고 fail이면 임의 보간 없이 월/원인별 blocker가 남는다.

### 4차 — React Action / Synchronous Progress UX

- coverage blocker에 `60개월 가치평가 자료 보강` 버튼을 추가한다.
- React event를 Python action facade가 nonce 기반으로 한 번만 소비한다.
- 대상 확인, EPS 보강, 가격 이력 보강, 가치평가 재계산, 완료 순서의 사용자 중심 진행 상태를 표시한다.
- 완료 후 valuation cache를 clear하고 rerun한다.

완료 조건: 성공 시 그래프로 자동 전환하고 부분 성공/실패 시 갱신된 blocker와 재시도 action을 표시한다.

### 5차 — QA / Docs / Commit

- unit, service contract, ingestion failure/resume, idempotency, React event, cache/rerun을 검증한다.
- 실제 DB에서 최근 60개월 ready count와 coverage를 확인한다.
- desktop과 420px Browser QA를 수행하고 task/canonical docs/runbook을 동기화한다.
- unrelated untracked research folder와 generated screenshot은 stage하지 않는다.

완료 조건: fresh verification evidence, Browser QA screenshot, 문서 동기화, coherent Korean commit이 생성된다.

## Scope

### In Scope

- Nasdaq valuation coverage blocker 전용 repair plan과 one-click synchronous action
- 최근 60개월 holdings constituent의 SEC diluted EPS와 EOD price gap 보강
- existing ingestion/DB/loader/service/React 경계 재사용
- partial failure, resume, event dedup, cache clear, updated blocker feedback

### Out Of Scope

- UI에서 SEC/provider 직접 fetch
- background queue/daemon 신설
- coverage gate 완화
- foreign/FY-only annual EPS proxy 도입
- 상장폐지 가격이나 missing EPS 합성/보간
- 유료/account/token provider 도입
- raw job row 중심 운영 패널

## Stop Conditions

- 무료·무계정 원천으로 제공되지 않는 값을 임의로 생성하지 않는다.
- 월별 weighted coverage가 95% 미만이면 그 달을 READY로 승격하지 않는다.
- action 재실행이 duplicate event 또는 duplicate business row를 만들면 UI 연결을 진행하지 않는다.
- 수집이 UI layer에서 직접 실행되거나 DB를 우회하면 구현을 중단하고 경계를 수정한다.

## Verification Outline

```bash
.venv/bin/python -m unittest tests.test_nasdaq100_valuation tests.test_market_context_valuation -v
.venv/bin/python -m unittest tests.test_service_contracts -v
npm run build --prefix app/web/streamlit_components/market_context_valuation
.venv/bin/python -m py_compile finance/data/nasdaq100_valuation.py app/jobs/ingestion_jobs.py app/jobs/overview_actions.py app/web/overview/market_context_helpers.py
git diff --check
git status --short
```
