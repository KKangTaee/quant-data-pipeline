# Active Finance Tasks

Status: Active
Last Verified: 2026-06-08

이 폴더는 현재 실행 중인 task 기록과, 아직 archive / done 이동을 하지 않은 retained task 기록을 함께 둔다.

현재 상태를 볼 때는 이 폴더의 모든 하위 폴더를 literal active work로 해석하지 않는다.
현재 작업은 [STATUS_MANIFEST.md](./STATUS_MANIFEST.md), 아래 `Current Active Tasks`, [Roadmap](../../docs/ROADMAP.md)을 우선 확인한다.

권장 구조:

```text
tasks/active/<task-name>/
  PLAN.md
  DESIGN.md
  STATUS.md
  NOTES.md
  RUNS.md
  RISKS.md
```

작은 단일 파일 수정에는 task 문서를 만들지 않아도 된다.
여러 파일을 건드리거나, 조사 / 설계 / QA가 필요한 작업은 active task로 관리한다.

## Current Active Tasks

| Task | Status | Notes |
|---|---|---|
| none | - | 현재 새 active task는 없다. 최신 완료 task는 아래 retained record를 확인한다. |

## Recent Completed / Retained Current Work

| Task | Status | Notes |
|---|---|---|
| `etf-rerun-matrix-workbench-20260608` | Completed record | Backtest 4차 4B. GRS / Risk Parity / Dual Momentum의 rerun scenario matrix를 보여주고, 선택한 ETF 전략만 session-only로 실행해 compact result evidence를 표시한다. |
| `etf-current-anchor-workbench-20260608` | Completed record | Backtest 4차 4A. 기존 run history / Practical Validation source handoff row를 읽어 GRS / Risk Parity / Dual Momentum의 current-anchor readiness와 missing evidence를 read-only로 보여준다. |
| `etf-evidence-expansion-20260608` | Completed record | Backtest 3차 3D. GRS / Risk Parity / Dual Momentum의 current anchor / near miss / not-ready reason / required evidence / next workflow를 read-only로 보여준다. |
| `risk-on-momentum-governance-20260608` | Completed record | Backtest 3차 3C. Risk-On Momentum 5D의 Daily Swing research evidence와 deferred validation / review / monitoring governance module을 read-only로 보여준다. |
| `strict-annual-etf-bridge-20260608` | Completed record | Backtest 3차 3B. Strict Annual 3종 + GTAA / Equal Weight bridge를 read-only로 정리해 component role / validation gap / recommended workflow를 보여준다. |
| `strategy-evidence-inventory-direction-panel-20260608` | Completed record | Backtest 3차 3A. Strategy Evidence Inventory / Direction Panel을 read-only로 구현해 catalog strategy별 maturity / evidence / next action을 보여준다. |
| `merge-review-fixes-20260608` | Completed record | sub-dev / main-dev master merge review 후 Reference internal link, Reference V4 status, catalog test assertion을 바로잡은 기록이다. |
| `reference-drift-guard-qa-polish-v5-20260608` | Completed record | contextual Reference help가 Glossary term / Reference link boundary에서 drift되지 않도록 guard와 표시 polish를 추가한 5차 기록이다. |
| `reference-contextual-links-v4-20260608` | Completed record | 주요 Backtest / Operations 화면에 read-only Reference help expander를 연결한 4차 기록이다. |
| `reference-glossary-concept-dictionary-v3-20260607` | Completed record | `Reference > Guides`와 `Reference > Glossary`가 같은 Streamlit-free concept dictionary와 search helper를 쓰도록 통합한 3차 기록이다. |
| `reference-guides-journey-playbooks-v2-20260607` | Completed record | `Reference > Guides`의 journey 상세, failure state, troubleshooting check step, evidence location을 확장한 2차 기록이다. |
| `reference-guides-center-v1-20260607` | Completed record | `Reference > Guides`를 task-first Reference Center로 개편하고, 기존 portfolio-selection guide를 `Portfolio Selection Journey`로 보존한 기록이다. |
| `futures-monitor-stale-refresh-fix-20260607` | Completed record | Overview Futures Monitor가 현재 UTC lookback 밖의 최신 저장 1m candle을 `Missing`처럼 숨기지 않고, latest stored candle 기준으로 차트를 표시하면서 stale status를 유지하도록 고친 기록이다. |
| `operations-v2-closeout-20260608` | Completed record | Operations Overview V2 5차 closeout. 1차~4차 개편을 최종 QA / runbook / durable docs 기준으로 닫고 normal top-navigation QA path와 direct route diagnostic을 분리한 기록이다. |
| `operations-review-queue-refinement-20260608` | Completed record | Operations Overview V2 4차. Today's Operations Queue를 priority / evidence / metric 기반 review queue로 재정렬해 setup blocker, system run failure, scenario freshness, open review, routine monitoring을 분리한 기록이다. |
| `operations-evidence-health-strip-20260607` | Completed record | Operations Overview V2 3차. Operations Console 상단에 Evidence Health mini strip을 추가해 scenario freshness / selected evidence readiness / open review / system run health를 한 줄로 확인하게 한 기록이다. |
| `operations-portfolio-first-summary-20260607` | Completed record | Operations Overview V2 2차. Operations Console 상단에 Portfolio Monitoring Status summary를 추가해 active portfolio / assigned strategy / stale scenario / blocked / missing / open review / next review를 먼저 읽게 한 기록이다. |
| `operations-cockpit-cleanup-20260607` | Completed record | Operations Overview V2 1차 cleanup. 사용자-facing Operations Overview에서 archive / development-history decision table과 roadmap 흔적을 제거하고 Portfolio Monitoring / System Data Health 중심 cockpit copy로 정리한 기록이다. |
| `refactor-round-closeout-20260607` | Completed record | 10차 구조정리 라운드 closeout. 5차~9차 리팩토링 기준선을 감사하고, 남은 Backtest Compare / Overview / Operations split 후보를 후속 작업으로 분리한 기록이다. |
| `backtest-compare-components-split-20260607` | Completed record | 9차 Backtest Compare Streamlit split first pass. Portfolio Mix Builder visual shell을 `app/web/backtest_compare_components.py`로 이동하고 `app/web/backtest_compare.py`를 실행 / 상태 orchestration 중심으로 낮춘 기록이다. |
| `ingestion-diagnostic-facade-20260607` | Completed record | 7차 대형 Streamlit 파일 분해 7B. Ingestion read-only diagnostic orchestration을 `app/services/ingestion_diagnostics.py`로 이동하고 `app/web/ingestion_console.py`는 렌더 / 세션 상태에 집중하게 한 기록이다. |
| `runtime-backtest-strict-family-split-20260607` | Completed record | 8차 runtime 대형 파일 분해 8C. `app/runtime/backtest.py`의 strict quality / value / quality-value annual and quarterly runtime wrapper family를 `app/runtime/backtest_strict.py`로 이동하고 public facade import를 유지한 기록이다. |
| `runtime-backtest-real-money-split-20260607` | Completed record | 8차 runtime 대형 파일 분해 8B. `app/runtime/backtest.py`의 real-money / guardrail / benchmark / deployment readiness helper family를 `app/runtime/backtest_real_money.py`로 이동하고 public facade import를 유지한 기록이다. |
| `runtime-backtest-risk-on-momentum-split-20260607` | Completed record | 8차 runtime 대형 파일 분해 8A. `app/runtime/backtest.py`의 Risk-On Momentum 5D runtime slice를 `app/runtime/backtest_risk_on_momentum.py`로 이동하고 public facade import를 유지한 기록이다. |
| `streamlit-ingestion-console-split-20260607` | Completed record | 7차 대형 Streamlit 파일 분해 7A. `streamlit_app.py`를 Finance Console shell로 낮추고 `Workspace > Ingestion` render/state/job UI를 `app/web/ingestion_console.py`로 분리한 기록이다. |
| `overview-ingestion-action-boundary-20260607` | Completed record | 6차 수집 / 조회 경계 정리. Overview bounded refresh를 `app/jobs/overview_actions.py` action facade로 모으고, Overview UI의 직접 ingestion / automation / run-history import를 제거한 기록이다. |
| `code-boundary-refactor-audit-20260607` | Completed record | 5차 코드 구조 감사 / 리팩토링 기준선. UI / service / runtime / jobs / finance layer 경계, 대형 파일, 다음 refactor 우선순위를 정리한 기록이다. |
| `post-merge-verification-handoff-20260607` | Completed record | 4차 검증 및 handoff. 1차~3차 결과 검증과 다음 작업자 read order / remaining decisions를 정리한 기록이다. |
| `post-merge-active-state-cleanup-20260607` | Completed record | 3차 active task / phase 상태 정리. 대량 이동 없이 manifest / README / roadmap 기준으로 current state를 정리한 기록이다. |
| `post-merge-boundary-docs-alignment-20260607` | Completed record | 2차 구조 / 경계 문서 정리. UI / service / runtime / loader / DB / storage boundary를 durable docs에 맞춘 기록이다. |
| `post-merge-docs-alignment-20260607` | Completed record | 1차 post-merge docs alignment. 현재 제품 흐름 / 완료된 merged work / active 상태를 정리한 기록이다. |

## Retained Work Records

- 이 폴더에는 완료된 과거 task가 다수 남아 있다.
- 상세 구현 근거, 실행 로그, QA 결과를 찾을 때는 관련 task 폴더의 `STATUS.md`, `RUNS.md`, `NOTES.md`, `RISKS.md`를 확인한다.
- 2026-06-08 기준 200개 task folder가 retained record로 남아 있다. 대량 이동 / archive migration은 별도 승인된 migration task에서 처리한다.
