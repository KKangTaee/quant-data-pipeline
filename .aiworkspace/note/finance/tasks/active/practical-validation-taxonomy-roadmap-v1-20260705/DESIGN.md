# Practical Validation Taxonomy And Direction

Status: Draft
Created: 2026-07-05

## Summary

현재 Practical Validation은 기능이 부족한 상태가 아니다. 문제는 근거 생성층, gate 변환층, evidence board 표시층이 화면에서 모두 비슷한 중요도로 노출되면서 사용자가 "무엇을 먼저 고쳐야 하는가"와 "Final Review에서 판단할 것은 무엇인가"를 구분하기 어렵다는 점이다.

개편 방향은 다음과 같다.

- 2단계 Practical Validation은 "Final Review로 넘길 만큼 검증 근거가 충분한가?"만 책임진다.
- 3단계 Final Review는 "이 후보를 모니터링 후보로 선택 / 보류 / 재검토 / 거절할 것인가?"를 책임진다.
- diagnostics는 raw evidence layer로 낮추고, audits와 modules를 user-facing 판단 구조의 주 데이터로 쓴다.
- selected-route preflight는 안전장치로 유지하되 "최종 선택 판단"처럼 보이지 않게 `Final Review readiness preview`로 낮춘다.

## Current Code Responsibility

| File | Current Responsibility | Design Direction |
|---|---|---|
| `app/web/backtest_practical_validation/page.py` | source 확인, profile 입력, replay 실행, gate, evidence board, provider action, save/handoff가 한 파일에 혼재 | V6에서 orchestration only로 축소 |
| `app/web/backtest_practical_validation/components.py` | HTML/CSS visual shell helper | React 전환 전까지 shell helper로 유지 |
| `app/web/backtest_practical_validation/source_summary.py` | 현재 re-export | V6에서 source / Backtest handoff queue 렌더 owner |
| `app/web/backtest_practical_validation/replay_panel.py` | 현재 re-export | V5/V6에서 replay action owner |
| `app/web/backtest_practical_validation/provider_actions.py` | 현재 re-export | V5/V6에서 provider action owner |
| `app/web/backtest_practical_validation/evidence_boards.py` | 현재 re-export | V4/V6에서 Evidence Workbench owner |
| `app/services/backtest_practical_validation_diagnostics.py` | 12 diagnostics, audits, selected preflight, modules assembly | V1/V3에서 workspace read model input source |
| `app/services/backtest_practical_validation_modules.py` | module-level gate planner and Final Review move gate | V2에서 stage boundary copy / selected preflight treatment 정리 |
| `app/services/backtest_practical_validation_board_registry.py` | board -> module map | 기본 접힘 기술 지도 유지 |
| `app/services/backtest_selected_route_preflight.py` | Final Review selected-route policy pre-run | V2에서 readiness preview로 낮춤 |
| `app/services/backtest_evidence_read_model.py` | Final Review investability packet / selection gate policy | 3단계 selected decision owner로 유지 |

## Current Layer Model

```text
Selection Source
  -> Practical Diagnostics (12 raw domains)
  -> Domain Audits (normalized criteria rows)
  -> Validation Modules (required / conditional / reference gate)
  -> Validation Board Map (screen explanation)
  -> Final Review Gate / Handoff
```

현재 화면 문제는 위 모든 층을 비슷한 density로 보여주는 데서 생긴다.

새 표시 원칙:

```text
User-facing:
  Gate Summary
  Fix Queue
  Core Evidence Workbench
  Provider Actions
  Save / Final Review Handoff

Collapsed technical details:
  Raw diagnostics
  Board map
  Source traits
  Policy rows
  JSON payload
```

## 12 Diagnostics Taxonomy

| Diagnostic | What It Checks | Stage-2 Classification | Display Direction |
|---|---|---|---|
| Input Evidence Layer | source id, active components, target weight, Data Trust, curve, replay, period coverage, benchmark parity, provider coverage | Core | Gate / source confirmation |
| Asset Allocation Fit | asset exposure, unknown weight, profile equity threshold, provider exposure | Core, but represented through construction / look-through | Merge into Construction / Look-through evidence |
| Concentration / Overlap / Exposure | max component weight, provider holdings, top holding, overlap, asset exposure | Core | Construction Risk Audit is primary |
| Correlation / Diversification / Risk Contribution | component return matrix, correlation, volatility contribution proxy | Conditional core for weighted mix | Risk Contribution Audit primary |
| Regime / Macro Suitability | FRED / proxy macro context, regime split validation | Conditional for tactical / hedged profiles | Collapse unless tactical source/profile |
| Sentiment / Risk-On-Off Overlay | risk-on/off context proxy | Supporting context | Keep context-only; never gate-leading |
| Stress / Scenario Diagnostics | stress windows, computed vs covered windows, MDD / spread interpretation | Core | Robustness Lab primary |
| Alternative Portfolio Challenge | simple baseline comparison | Supporting evidence | Collapse under Evidence Workbench |
| Leveraged / Inverse ETF Suitability | leveraged / inverse exposure and profile allowance | Conditional core | Show only when applicable |
| Operability / Cost / Liquidity | provider operability, cost assumption, excluded tickers, price/volume proxy | Core | Backtest Realism / Provider primary |
| Robustness / Sensitivity / Overfit | sensitivity, rolling validation, overfit audit | Core | Robustness Lab primary |
| Monitoring Baseline Seed | post-selection review cadence / trigger seed | Downstream reference | Move to Final Review / Operations reference |

## Audit Taxonomy

### Validation Efficacy

Rows:

- Backtest source contract
- Data Trust boundary
- Runtime replay evidence
- Runtime period coverage
- Benchmark parity
- Walk-forward temporal validation
- OOS holdout validation
- Regime split validation
- Provider / freshness evidence
- Robustness / stress coverage
- PIT / look-ahead guard
- Survivorship / universe guard
- Execution / storage boundary

Stage-2 role: core evidence strength.

### Data Coverage

Rows:

- Price DB window coverage
- Provider snapshot freshness
- PIT price window coverage
- Universe / listing evidence
- Survivorship / delisting control
- Data storage boundary

Stage-2 role: core data trust and PIT coverage.

### Construction Risk

Rows:

- Component weight concentration
- Provider look-through coverage
- Top holding concentration
- Holdings overlap
- Asset bucket exposure
- Storage / execution boundary

Stage-2 role: core construction risk.

### Risk Contribution

Rows:

- Component return matrix coverage
- Pairwise correlation
- Risk contribution concentration
- Drop-one component dependency
- Storage / execution boundary

Stage-2 role: conditional core for weighted mix.

### Component Role / Weight

Rows:

- Component role source coverage
- Profile-aware weight discipline
- Role concentration discipline
- Profile intent role fit
- Weight rationale coverage
- Storage / execution boundary

Stage-2 role: conditional core for weighted mix. General REVIEW should flow to Final Review; missing role / rationale can block when selection-critical.

### Backtest Realism

Rows:

- Transaction cost model
- Net cost curve proof
- Turnover evidence
- Cost / slippage sensitivity evidence
- Liquidity / operability evidence
- Net performance policy
- Rebalance / trade timing
- Tax / account scope
- Execution boundary

Stage-2 role: core for cost, turnover, liquidity, net performance, rebalance timing.

`Tax / account scope` should be demoted to Final Review reference. It should not sit visually beside core 2단계 practical evidence.

## Validation Module Taxonomy

| Module | Requirement | Stage Owner | Stage-2 Decision |
|---|---|---|---|
| Source Integrity | Required | Practical Validation | Core gate |
| Latest Runtime Replay | Required | Practical Validation | Core gate |
| Benchmark / Comparator Parity | Required | Practical Validation | Core gate |
| Validation Efficacy | Required | Practical Validation | Core gate |
| Data Coverage | Required | Practical Validation | Core gate |
| Construction Risk | Required | Practical Validation | Core gate |
| Backtest Realism | Required | Practical Validation | Core gate, excluding tax/account visual priority |
| Stress / Robustness | Required | Practical Validation | Core gate |
| ETF Provider Investability | Conditional | Practical Validation | Show when ETF-like |
| Leveraged / Inverse Suitability | Conditional | Practical Validation / Final Review | Show when applicable; review details can move to Final Review |
| Risk Contribution | Conditional | Practical Validation | Weighted mix only |
| Component Role / Weight | Conditional | Practical Validation | Weighted mix only |
| Macro / Regime Fit | Conditional | Practical Validation | Tactical / hedged profile only |
| Monitoring Baseline | Reference | Selected Dashboard | Downstream reference |
| Tax / Account Scope | Reference | Final Review | Downstream reference |
| Selected-route Preflight | Required today | Practical Validation | Keep as readiness preview, not final decision |

## Stage Boundary

### Keep In Practical Validation

- Source integrity
- Backtest에서 넘어온 2차 확인 queue
- Latest runtime replay
- Runtime period coverage
- Benchmark / comparator parity
- Data coverage / PIT / survivorship
- Provider investability and gap actions
- Liquidity / cost / turnover / net performance
- Construction risk / concentration / overlap / look-through exposure
- Stress / robustness / sensitivity / overfit
- Validation efficacy
- Practical blocker and fix queue

### Move Or Demote To Final Review

- Selected-route final choice semantics
- Final memo
- Select / hold / re-review / reject decision
- Monitoring candidate save
- Tax / account scope
- Monitoring baseline confirmation
- Selected Dashboard handoff interpretation
- General REVIEW item operator judgment

### Keep Collapsed As Technical Detail

- Raw diagnostics table
- Profile-aware score breakdown
- Applied Validation Map
- Source traits JSON
- `policy_rows`
- Raw route names
- schema version
- Practical Validation result JSON

## Duplicate / Excessive UI Candidates

| Current Surface | Issue | Direction |
|---|---|---|
| Practical Diagnostics summary plus individual audit boards | Same facts appear once as diagnostic domains and again as audit rows | Audits become primary; diagnostics collapse |
| Applied Validation Map | Useful for developers, not first-read workflow | Collapse under technical details |
| Board context badges on every board | Explains map repeatedly | Keep only in Workbench technical info |
| Provider Coverage plus Look-through plus Construction Risk | Provider evidence is repeated across three areas | Workbench groups provider state once, with drilldown |
| Robustness diagnostic plus Robustness Lab | Same stress / sensitivity evidence appears twice | Robustness Lab primary, diagnostic raw collapsed |
| Monitoring Baseline Seed | 3단계 / Operations meaning | Move to downstream reference |
| Tax / account scope row | Final judgment / account implementation meaning | Demote from 2단계 gate visual priority |
| Save blocker table and Fix Queue cards | Same blocking modules repeated | Fix Queue cards first; table collapsed |

## Target Workspace Read Model

V3 should introduce a service read model shaped like:

```python
{
    "summary": {...},
    "source_queue": [...],
    "profile": {...},
    "replay_action": {...},
    "gate_summary": {...},
    "fix_queue": [...],
    "evidence_groups": [
        {"group_id": "core_readiness", "rows": [...]},
        {"group_id": "data_coverage", "rows": [...]},
        {"group_id": "construction", "rows": [...]},
        {"group_id": "realism", "rows": [...]},
        {"group_id": "robustness", "rows": [...]},
        {"group_id": "conditional", "rows": [...]},
    ],
    "provider_actions": {...},
    "handoff_state": {...},
    "technical_details": {...},
}
```

The page should read this model instead of directly interpreting many service payloads.

## Target Screen Flow

Target 5-flow:

1. 후보 확인
2. 실전 검증 실행 / 최신 replay
3. 2차 검증 결론과 Fix Queue
4. 근거 Workbench
5. 저장하고 Final Review로 이동

The first visible answer should be:

```text
이 후보는 지금 Final Review로 넘길 수 있는가?
막는 항목은 무엇인가?
사용자가 지금 바로 할 수 있는 보강 action은 무엇인가?
자세한 근거는 어디에서 펼치면 되는가?
```

## React Component Direction

React custom components should be used only where a visible card and real action need to live inside one DOM surface.

Priority:

1. Practical Validation Control Center
2. Latest Runtime Replay action card
3. Gate / Fix Queue board
4. Provider Data Gap action card
5. Save & Final Review handoff action
6. Evidence Workbench filter / accordion only if Streamlit tabs remain too fragmented

Python remains responsible for:

- service execution
- session state
- registry append
- rerun
- provider job orchestration
- validation result build

React owns only:

- card layout
- local button / selection interactions
- component event payload
- status presentation inside the card

## Implementation Sequencing

The safest sequence is taxonomy/read-model first, UI rearrangement second, React third, physical split fourth.

Reason:

- React first would only make the current repeated taxonomy prettier.
- Physical split first would move a 2,586-line page without clarifying what each panel owns.
- Gate semantics first could accidentally change product behavior before the UI boundary is agreed.

Therefore:

1. V1/V3 establish read model contracts.
2. V2 clarifies stage language without changing gate math.
3. V4 changes the visible flow.
4. V5 adds React components where necessary.
5. V6 physically splits `page.py`.
6. V7/V8 finish status language and durable docs.
