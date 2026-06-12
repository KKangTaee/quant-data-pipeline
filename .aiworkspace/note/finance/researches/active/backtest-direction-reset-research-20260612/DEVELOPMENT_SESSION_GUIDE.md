# Backtest Direction Reset Development Session Guide

Status: Active
Last Updated: 2026-06-12 KST

## Purpose

이 문서는 `backtest-direction-reset-research-20260612` 리서치 결과를 바탕으로, 각 개발 차수를 새 Codex 세션에 나누어 요청하기 위한 실행 가이드다.

이 문서 자체는 승인된 구현 계획이 아니다. 각 차수는 새 세션에서 다시 `finance-task-intake`로 scope를 확인하고, 사용자가 해당 차수를 명시 승인한 뒤 task를 열어 진행한다.

## Overall Direction

Backtest Analysis는 실행 / 비교 / 후보 source / replay 가능성 확인에 집중한다.
Evidence / governance / diagnostics는 compact handoff, Reference/report, Practical Validation, Final Review, Operations Monitoring으로 분리한다.

핵심 원칙:

- Backtest Analysis 기본 화면은 execution-first를 유지한다.
- 5A/5B처럼 runtime/result bundle contract를 고도화하는 방향은 유지한다.
- 3A~4B처럼 evidence/governance/workbench panel이 기본 화면을 무겁게 만드는 방향은 반복하지 않는다.
- History / Saved replay는 재현성이지 validation pass가 아니다.
- Practical Validation이 evidence gate, Final Review가 selected-route gate, Operations Monitoring이 post-selection read-only monitoring을 소유한다.
- Strict Quarterly Prototype과 Risk-On Momentum 5D는 별도 gate 승인 전까지 prototype / research lane으로 둔다.

## Common Rules For Every New Session

### Required Reads

새 세션마다 먼저 아래를 읽는다.

```bash
sed -n '1,260p' .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/RECOMMENDATION.md
sed -n '1,320p' .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/DEVELOPMENT_SESSION_GUIDE.md
sed -n '1,260p' .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/RISKS.md
sed -n '1,260p' .aiworkspace/note/finance/docs/PROJECT_MAP.md
sed -n '1,260p' .aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md
sed -n '1,260p' .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md
```

필요 시 함께 읽는다.

```bash
sed -n '1,300p' .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/CURRENT_PROJECT_AUDIT.md
sed -n '1,300p' .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/FEATURE_CANDIDATES.md
sed -n '1,280p' .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/UI_PATTERNS.md
```

### Required Skills

새 구현 세션의 기본 skill 순서:

1. `finance-task-intake`
2. 해당 domain skill
   - Backtest UI / handoff / replay: `finance-backtest-web-workflow`
   - Strategy runtime / metadata / smoke: `finance-strategy-implementation`
   - Practical Validation handoff가 실제로 바뀌는 경우: `finance-backtest-web-workflow`
3. 구현 후 필요 시 `finance-integration-review`
4. 승인된 구현 완료 후 durable docs sync가 필요할 때만 `finance-doc-sync`

### Common Do Not

명시 승인 전까지 하지 않는다.

- 새 Backtest Analysis evidence / governance / workbench panel 추가
- registry / saved JSONL / run_history / generated artifact rewrite
- provider / FRED direct fetch
- Practical Validation / Final Review / Portfolio Monitoring behavior 변경
- `docs/ROADMAP.md` 또는 phase/task plan을 research recommendation만으로 확정 변경
- strict quarterly prototype label 제거
- Risk-On Momentum monitoring signal화
- live approval, broker order, account sync, auto rebalance

### Common Verification

변경 종류에 맞게 최소한 아래를 검토한다.

```bash
git status --short
git diff --check
```

Python/UI 변경 시 예시:

```bash
.venv/bin/python -m py_compile app/web/backtest_analysis.py app/web/backtest_result_display.py
.venv/bin/python -m pytest tests/test_service_contracts.py -q
```

실제 명령은 각 차수에서 touch한 파일과 기존 test structure를 보고 좁게 정한다.
UI 변경이 있으면 Browser QA와 screenshot을 남긴다. Screenshot은 generated artifact이므로 사용자가 명시하지 않으면 커밋하지 않는다.

## Development Roadmap

| 차수 | 상태 | 핵심 목적 | 기본 owner |
| --- | --- | --- | --- |
| 1차 | Next approval target | Backtest result handoff contract + compact maturity label | `finance-backtest-web-workflow` |
| 2차 | After 1차 | History / Saved replay semantics cleanup | `finance-backtest-web-workflow` |
| 3차 | After 1차 or 2차 | ETF evidence expansion sequence | `finance-strategy-implementation` / report-focused workflow |
| 4차 | After 1차~3차 | Strict Annual + ETF sleeve validation handoff | `finance-backtest-web-workflow` |
| 5차 | Separate decision | Strict Quarterly Prototype maturation or Risk-On Momentum governance | depends on selected path |

각 차수는 독립 새 세션으로 진행한다. 이전 차수의 commit hash, task folder, Browser QA screenshot, 남은 risk를 다음 세션 첫 메시지에 포함하면 좋다.

## 1차 Session Guide: Backtest Result Handoff Contract

### Goal

Backtest Analysis 결과가 "다음에 무엇을 해도 되는지"를 compact하게 말하게 한다.
핵심은 새 panel이 아니라 handoff contract다.

구분해야 하는 네 object:

- `Run Result`: 이번 실행 결과
- `Replayable Setup`: history/saved setup으로 재현 가능한 설정
- `Validation Source`: Practical Validation으로 넘길 수 있는 후보 source
- `Monitoring Record`: Final Review selected-route 이후 Operations에서 관찰하는 기록

### Scope

가능성이 높은 파일:

- `app/services/backtest_result_read_model.py`
- `app/web/backtest_result_display.py`
- `app/web/backtest_single_strategy.py`
- `app/web/backtest_compare.py`
- `app/services/backtest_strategy_evidence_inventory.py`
- relevant focused tests under `tests/`

문서:

- active task docs only
- durable docs는 구현 완료 후 `finance-doc-sync` 승인 시 반영

### Explicit Non-Scope

- Practical Validation 동작 변경
- Final Review 동작 변경
- Monitoring 동작 변경
- registry / saved JSONL / run_history write
- 새 Backtest Analysis panel
- quarterly prototype formalization
- Risk-On downstream promotion

### Completion Criteria

- result summary나 result-adjacent compact strip에서 maturity label과 missing gate reason을 읽을 수 있다.
- `Run Result`와 `Replayable Setup`이 `Validation Source`와 구분된다.
- strict quarterly는 prototype으로 남는다.
- Risk-On Momentum은 research lane으로 남는다.
- Backtest Analysis 기본 화면은 Single Strategy / Portfolio Mix Builder 우선이다.

### Verification

최소 기대:

```bash
git diff --check
.venv/bin/python -m py_compile app/web/backtest_result_display.py app/web/backtest_single_strategy.py app/web/backtest_compare.py
```

서비스 read model을 추가하면 focused pytest를 만든다.
UI 변경이 있으면 Browser QA로 기본 Backtest Analysis와 result view를 확인한다.

### Suggested New Session Prompt

```text
Backtest Direction Reset 1차를 진행해줘.

먼저 아래 문서를 읽어줘.
- .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/RECOMMENDATION.md
- .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/DEVELOPMENT_SESSION_GUIDE.md
- .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/RISKS.md

이번 1차 목표는 Backtest Result Handoff Contract야.
Backtest Analysis 기본 화면은 execution-first로 유지하고, 새 evidence/governance/workbench panel은 추가하지 마.
Run Result / Replayable Setup / Validation Source / Monitoring Record를 compact하게 구분하고,
strategy maturity label과 missing gate reason을 result-adjacent read model로 표현해줘.

금지:
- Practical Validation / Final Review / Monitoring behavior 변경
- registry / saved JSONL / run_history / generated artifact rewrite
- provider / FRED direct fetch
- strict quarterly prototype 정식 승격
- Risk-On Momentum monitoring signal화
- docs/ROADMAP.md 변경

구현 전 task docs를 열고, TDD 가능한 read-model부터 시작해줘.
UI 변경이 있으면 Browser QA screenshot까지 남겨줘.
```

## 2차 Session Guide: Replay Semantics Cleanup

### Goal

History Replay와 Saved Portfolio Replay가 "재현성"으로 읽히게 정리한다.
Saved / replayed가 validation pass나 selected decision으로 보이면 안 된다.

### Scope

가능성이 높은 파일:

- `app/web/backtest_history.py`
- `app/web/backtest_history_helpers.py`
- `app/services/backtest_saved_portfolio_replay.py`
- `app/runtime/candidate_library.py`
- `app/web/backtest_compare.py`
- relevant focused tests

### Explicit Non-Scope

- JSONL rewrite
- Candidate promotion
- unsupported strategy lifecycle 확장
- Practical Validation result write
- Final Review decision write

### Completion Criteria

- History / Saved surfaces가 1차의 handoff contract 용어와 일치한다.
- Replay는 reproducibility로 설명된다.
- Candidate Library support 범위가 ETF + strict annual 중심임을 숨기지 않는다.
- quarterly와 Risk-On은 prototype / research lane으로 남는다.

### Verification

```bash
git diff --check
.venv/bin/python -m py_compile app/web/backtest_history.py app/web/backtest_history_helpers.py app/services/backtest_saved_portfolio_replay.py app/runtime/candidate_library.py
```

가능하면 replay/load parity 관련 focused tests를 실행한다.
UI copy 변경이 있으면 Browser QA로 History / Saved replay 화면을 확인한다.

### Suggested New Session Prompt

```text
Backtest Direction Reset 2차를 진행해줘.

1차 결과와 아래 guide를 먼저 읽어줘.
- .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/DEVELOPMENT_SESSION_GUIDE.md
- .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/RECOMMENDATION.md

이번 목표는 History Replay / Saved Portfolio Replay semantics cleanup이야.
Replay와 saved setup은 재현성이지 validation pass가 아니라는 점을 UI/read model/copy에서 일관되게 보여줘.
1차의 Run Result / Replayable Setup / Validation Source / Monitoring Record 용어와 맞춰줘.

금지:
- JSONL rewrite
- Candidate promotion
- Practical Validation / Final Review / Monitoring behavior 변경
- quarterly/Risk-On lifecycle 확장
- docs/ROADMAP.md 변경

가능한 한 focused tests와 Browser QA로 확인해줘.
```

## 3차 Session Guide: ETF Evidence Expansion Sequence

### Goal

5A/5B runtime metadata를 바탕으로 GRS, Risk Parity Trend, Dual Momentum의 durable evidence를 보강한다.
기본 방향은 report/reference/evidence 정리이지 새 default panel이 아니다.

### Scope

대상 전략:

- Global Relative Strength
- Risk Parity Trend
- Dual Momentum

가능성이 높은 위치:

- `.aiworkspace/note/finance/reports/backtests/strategies/`
- `.aiworkspace/note/finance/reports/backtests/INDEX.md`
- existing ETF evidence services only if approved
- runtime smoke only if approved

### Explicit Non-Scope

- current-candidate registry write
- provider direct fetch
- Practical Validation result 생성
- 새 ETF strategy 추가
- Backtest Analysis default panel 추가

### Completion Criteria

각 전략마다 최소한 아래를 정리한다.

- current anchor
- near miss
- not-ready reason
- required evidence
- provider/cost/benchmark caveat
- next allowed workflow

### Verification

문서 중심이면 source/path verification과 `git diff --check`.
runtime smoke가 포함되면 해당 strategy focused smoke/test를 명시적으로 실행한다.

### Suggested New Session Prompt

```text
Backtest Direction Reset 3차를 진행해줘.

이번 목표는 ETF Evidence Expansion Sequence야.
GRS / Risk Parity Trend / Dual Momentum의 5A/5B runtime metadata를 바탕으로 durable strategy evidence를 보강하되,
새 Backtest Analysis default panel은 만들지 마.

먼저 아래 문서를 읽어줘.
- .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/DEVELOPMENT_SESSION_GUIDE.md
- .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/CURRENT_PROJECT_AUDIT.md
- .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/SOURCES.md
- .aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md

각 ETF 전략에 대해 current anchor / near miss / not-ready reason / required evidence / provider-cost-benchmark caveat / next workflow를 정리해줘.

금지:
- current-candidate registry write
- provider direct fetch
- Practical Validation result write
- saved/run_history/generated artifact rewrite
- 새 ETF strategy 추가
- docs/ROADMAP.md 변경
```

## 4차 Session Guide: Strict Annual + ETF Sleeve Validation Handoff

### Goal

Strict Annual 3종과 GTAA / Equal Weight를 winner ranking이 아니라 portfolio construction candidate source로 Practical Validation에 안전하게 연결한다.

대상:

- Quality Strict Annual
- Value Strict Annual
- Quality + Value Strict Annual
- GTAA
- Equal Weight

### Scope

가능성이 높은 파일:

- `app/web/backtest_compare.py`
- `app/services/backtest_practical_validation_source.py`
- `app/services/backtest_component_role_weight_audit.py`
- `app/services/backtest_construction_risk_audit.py`
- relevant focused tests

### Explicit Non-Scope

- Final Review auto-selection
- Monitoring scenario creation
- live approval / broker order
- registry/saved/run_history rewrite
- Risk-On or quarterly inclusion

### Completion Criteria

- strict annual core + ETF sleeve source가 role / target weight / known weakness / required validation evidence를 가진다.
- Practical Validation으로 넘길 때 이 정보가 candidate-source metadata로만 읽힌다.
- Final Review selected-route는 여전히 downstream gate다.

### Verification

```bash
git diff --check
.venv/bin/python -m py_compile app/web/backtest_compare.py app/services/backtest_practical_validation_source.py
```

서비스 테스트와 Browser QA로 Backtest -> Practical Validation handoff를 확인한다.

### Suggested New Session Prompt

```text
Backtest Direction Reset 4차를 진행해줘.

목표는 Strict Annual + ETF Sleeve Validation Handoff야.
Quality / Value / Quality+Value Strict Annual과 GTAA / Equal Weight를 winner ranking이 아니라
role / weight / known weakness / required validation evidence가 있는 Practical Validation candidate source로 연결해줘.

먼저 아래 문서를 읽어줘.
- .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/DEVELOPMENT_SESSION_GUIDE.md
- .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/RECOMMENDATION.md
- .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md

금지:
- Final Review auto-selection
- Monitoring scenario creation
- live approval / broker order / auto rebalance
- registry/saved/run_history rewrite
- Risk-On Momentum 또는 strict quarterly 포함
- docs/ROADMAP.md 변경

UI 변경이 있으면 Browser QA screenshot을 남겨줘.
```

## 5차 Session Guide: Prototype / Research Lane Decision

### Goal

5차는 하나의 큰 작업이 아니다. 아래 둘 중 하나만 선택해 별도 세션으로 진행한다.

- 5A path: Strict Quarterly Prototype Maturation Gate
- 5B path: Risk-On Momentum Governance Design

둘을 한 세션에 섞지 않는다.

## 5A Path: Strict Quarterly Prototype Maturation Gate

### Goal

Quarterly prototype이 정식 후보가 되려면 어떤 evidence가 필요한지 구현 또는 설계한다.
기본 상태는 prototype label 유지다.

### Required Evidence

- quarterly PIT rows
- filing lag handling
- history replay parity
- saved replay policy
- Candidate Library lifecycle decision
- Practical Validation source compatibility
- current anchor / not-ready reason report

### Suggested New Session Prompt

```text
Backtest Direction Reset 5A를 진행해줘.

이번 목표는 Strict Quarterly Prototype Maturation Gate야.
Quality / Value / Quality+Value Strict Quarterly Prototype을 정식 승격하지 말고,
prototype label을 유지한 상태에서 정식 후보가 되려면 필요한 PIT / filing lag / replay / validation evidence gate를 설계하거나 구현해줘.

금지:
- prototype label 제거
- annual strict와 같은 readiness로 표현
- registry/saved/run_history rewrite
- Practical Validation / Final Review behavior 변경 without separate approval
- docs/ROADMAP.md 변경
```

## 5B Path: Risk-On Momentum Governance Design

### Goal

Risk-On Momentum 5D를 Daily Swing research lane에서 downstream workflow로 넘길 수 있는지 별도 governance를 설계한다.
초기 목표는 monitoring signal이 아니라 review evidence다.

### Required Evidence

- Daily Swing Practical Validation module contract
- Final Review selected-route blocker / review-required rule
- artifact / trade log compact evidence policy
- universe / survivorship review
- daily review cadence and stale signal handling
- no-live-order boundary

### Suggested New Session Prompt

```text
Backtest Direction Reset 5B를 진행해줘.

이번 목표는 Risk-On Momentum 5D Governance Design이야.
Risk-On Momentum을 바로 Practical Validation / Final Review / Portfolio Monitoring으로 승격하지 말고,
Daily Swing 전용 validation module, selected-route rule, artifact policy, universe/survivorship review, daily review cadence를 설계해줘.

초기 output은 monitoring signal이 아니라 review evidence 기준이어야 해.

금지:
- monitoring signal 구현
- final selected-route 자동 승인
- generated artifact를 registry로 직접 승격
- live approval / broker order / auto rebalance
- docs/ROADMAP.md 변경
```

## Recommended Session Order

가장 안전한 순서:

1. 1차 Backtest Result Handoff Contract
2. 2차 Replay Semantics Cleanup
3. 3차 ETF Evidence Expansion Sequence
4. 4차 Strict Annual + ETF Sleeve Validation Handoff
5. 5A 또는 5B 중 하나만 선택

변형 가능:

- ETF 전략군을 먼저 깊게 보고 싶으면 1차 후 바로 3차로 갈 수 있다.
- Practical Validation 연결을 빨리 보고 싶으면 1차 후 4차로 갈 수 있다.
- quarterly 또는 Risk-On은 1차 전에는 시작하지 않는 편이 좋다. maturity/handoff 언어가 먼저 고정되어야 하기 때문이다.

## Final Handoff Checklist For Each Session

각 세션 final response에 반드시 남기게 한다.

- 전체 roadmap 중 몇 차를 완료했는지
- 이번 차수에서 바꾼 화면 / 코드 / 문서
- 이번 차수에서 하지 않은 일
- 실행한 verification command와 결과
- Browser QA screenshot path, UI 변경이 있었다면
- 남은 risk
- 다음 차수에서 읽을 위치
- commit hash
