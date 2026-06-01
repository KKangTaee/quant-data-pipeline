# Backtest Analysis Stage 1 Closeout

Status: Active
Last Verified: 2026-05-30

## Purpose

이 문서는 2026-05-30 기준 `Backtest > Backtest Analysis` 1단계의 현재 완료 상태를 요약한다.

Backtest Analysis는 최종 투자 판단 화면이 아니다. 이 단계의 목적은 단일 전략 또는 Portfolio Mix 후보를 만들고, 1차 후보 판단을 통과한 경우에만 `Practical Validation`으로 넘길 current selection source를 만드는 것이다.

## Session Weaknesses Addressed

이번 세션에서 Backtest Analysis 쪽에서 확인한 주요 약점은 아래와 같다.

| Weakness | Resolution |
|---|---|
| Backtest / validation / final review 단계 의미가 섞여 보임 | 검증 checkpoint 용어를 정리하고 Backtest Analysis를 1차 후보 생성 단계로 고정 |
| Real-Money 영역이 probation / monitoring / deployment처럼 후속 단계까지 검증하는 것처럼 보임 | Backtest Real-Money를 Promotion / execution source / validation source 중심의 1차 readiness로 축소 |
| Shortlist가 Promotion과 별도 검증 항목처럼 보임 | `Promotion Suggested Route`로 흡수해 추천 경로 역할로 낮춤 |
| Practical Validation handoff 버튼이 단순 저장 / preset처럼 보임 | 1차 후보 판단을 통과한 경우에만 활성화되는 handoff gate로 변경 |
| Runtime Payload와 결과 정보가 상시 펼쳐져 UX가 무거움 | payload와 raw evidence를 접힘 상세로 낮추고 checkpoint / summary-first UI로 재배치 |
| 기존 Compare & Portfolio Builder가 비교와 조합을 한 화면에서 섞음 | `Portfolio Mix Builder`로 재정의하고 여러 component를 하나의 weighted mix 후보로 만드는 흐름으로 고정 |
| Portfolio Mix 실행 후 component 결과가 9개 tab과 원본 table 중심으로 혼잡함 | component card overview, `요약 / 차트 / 진단 / 상세` 4-tab, stepper, scoped CSS로 재정리 |
| Mix 생성 후 상단 단계 카드가 3단계로 즉시 갱신되지 않음 | mix 생성 후 rerun하고, 3번 `Mix 후보 판단`은 active / blocked 판단 단계로 표시하며 4번은 handoff 가능 시 ready로만 표시 |

## Current Stage 1 Flow

```text
Backtest Analysis
  -> Single Strategy 또는 Portfolio Mix Builder
  -> Result Integrity / Performance Shape 확인
  -> Candidate Readiness 또는 Mix 후보 1차 판단
  -> Practical Validation 후보로 보내기
```

### Single Strategy

- 사용자는 단일 전략을 실행한다.
- Runtime Payload는 기본 검토 대상이 아니라 필요할 때 확인하는 상세 정보다.
- Latest Backtest Run은 결과를 읽는 순서를 제공한다.
- Data Trust Summary는 결과 기간, 가격 최신성, excluded ticker, warning을 먼저 확인하게 한다.
- Real-Money / Candidate Readiness는 다음 단계로 넘겨도 되는지 보는 1차 gate다.
- `실전성 검증으로 보내기`는 Promotion / execution source / validation source blocker가 없을 때만 활성화된다.

### Portfolio Mix Builder

- 여러 component 전략을 같은 기간 조건으로 실행한다.
- component 실행 결과는 weight를 정하기 위한 재료다.
- 사용자는 weight와 date alignment를 정해 하나의 weighted mix 후보를 만든다.
- 상단 stepper는 `Component 실행 -> Weight 구성 -> Mix 후보 판단 -> Practical Validation` 순서로 현재 위치를 보여준다.
- Mix 후보 판단은 mix result, 100% / 2개 이상 positive component weight, component data trust, component 1차 후보 readiness를 본다.
- blocker가 없으면 mix 전체를 하나의 current selection source로 Practical Validation에 보낸다.

## Current Storage Boundary

- Backtest Analysis handoff는 current selection source를 등록하는 workflow action이다.
- 사용자 메모용 저장, phase별 snapshot 저장, preset 저장을 새로 만들지 않았다.
- saved mix는 reusable setup이며 validation / approval record가 아니다.
- Backtest run history는 local runtime artifact라 보통 커밋하지 않는다.
- Final decision, live approval, broker order, account sync, auto rebalance는 Backtest Analysis 범위가 아니다.

## Verification Basis

최근 closeout 기준 검증:

- `.venv/bin/python -m py_compile app/web/backtest_compare.py`
- `git diff --check`
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - 133 tests passed
- Browser smoke on `http://127.0.0.1:8502/backtest`
  - `Portfolio Mix Builder` open
  - default `Equal Weight + GTAA` component run
  - `Mix 후보 결과 생성`
  - stepper state and `Mix 후보 1차 판단` panel 확인

`pytest` command is not the current local verification path because the active venv has no `pytest` module. Use `unittest tests.test_service_contracts` unless the environment changes.

## Remaining Follow-Ups

- 후보끼리 read-only로 비교하는 별도 tool은 아직 분리 구현하지 않았다.
- saved mix inspector는 여전히 raw record / detail 중심 영역이 남아 있어, 필요하면 별도 UX task로 정리한다.
- weighted mix의 cost / turnover aggregation, profile-specific threshold, selected replay hardening은 Phase 14 이후 prioritization 대상이다.
- Backtest Analysis 1단계는 여기서 닫고, 다음 검증 품질은 `Practical Validation`과 `Final Review`에서 확인한다.
