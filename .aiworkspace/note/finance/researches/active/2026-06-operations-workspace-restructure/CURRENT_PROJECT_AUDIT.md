# Current Project Audit

## Snapshot

현재 top navigation은 세 그룹이다.

- `Workspace`: Overview, Ingestion, Backtest
- `Operations`: Ops Review, Selected Portfolio Dashboard, Backtest Run History, Candidate Library
- `Reference`: Guides, Glossary

`Selected Portfolio Dashboard`가 `Workspace`가 아니라 `Operations`에 있는 것 자체는 현재 제품 정의와 맞다. Backtest에서 후보를 만들고 Practical Validation / Final Review를 통과한 뒤, 선정된 전략을 monitoring portfolio에 담아 이후 성과, review signal, 리밸런싱 target, open issue를 확인하는 화면이기 때문이다. 이 화면은 새 전략을 만드는 research workspace라기보다 선정 이후의 운영 관찰 화면이다.

다만 현재 `Operations`는 역할이 섞여 있다. `Ops Review`는 ingestion / runtime health 운영 콘솔이고, `Selected Portfolio Dashboard`는 투자 후보 운영 관찰 화면이며, `Backtest Run History`와 `Candidate Library`는 과거 실행 / legacy 후보를 다시 열기 위한 archive or recovery 도구다. 네 화면을 같은 레벨의 탭으로 두면 사용자는 "현재 해야 할 운영 판단"과 "과거 실행을 뒤지는 보조 도구"를 구분하기 어렵다.

## Local Evidence

| Area | Local source | What it proves |
| --- | --- | --- |
| Product direction | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | 제품은 data collection, backtest, practical validation, final portfolio selection, monitoring으로 이어지는 quant research workspace이며 live trading은 non-goal이다. |
| Navigation code | `app/web/streamlit_app.py` | `Operations`에 Ops Review, Selected Portfolio Dashboard, Backtest Run History, Candidate Library가 같은 level로 등록되어 있다. |
| Backtest UI flow | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Backtest Analysis -> Practical Validation -> Final Review -> Selected Portfolio Dashboard 흐름과 Operations 보조 화면의 역할이 문서화되어 있다. |
| Portfolio selection flow | `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | Selected Dashboard는 monitoring portfolio, scenario update, read-only recheck/readiness/provider evidence를 담당한다. |
| Project map | `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Selected Dashboard 소유 파일과 runtime model 경계가 `app/web/final_selected_portfolio_dashboard.py`, `app/runtime/final_selected_portfolios.py`로 분리되어 있다. |
| Ops Review UI | `app/web/ops_review.py` | 웹앱 run health, failure artifact, log, runtime snapshot 점검 화면이며 실행/재현은 전용 화면으로 라우팅한다. |
| Backtest Run History UI | `app/web/backtest_history.py` | 저장된 backtest run을 inspect하고 form 복원, rerun, Practical Validation handoff를 제공하는 운영/재현 도구다. |
| Candidate Library UI | `app/web/backtest_candidate_library.py` | 저장된 Current Candidate / Pre-Live 후보를 다시 열고 contract 기반 result curve를 rebuild하는 보관함이다. |
| Selected Dashboard UI | `app/web/final_selected_portfolio_dashboard.py` | Final Review selected 후보를 사용자가 만든 monitoring portfolio에 담고, scenario / review signal / allocation boundary를 확인한다. |

## Surface Classification

| Surface | User-facing / internal / mixed | Notes |
| --- | --- | --- |
| `Operations > Ops Review` | Internal / ops console | Ingestion job, run history, failure files, logs, runtime marker를 보는 시스템 운영 화면. 사용자의 투자 판단 workflow와 직접 연결되지는 않는다. |
| `Operations > Selected Portfolio Dashboard` | User-facing monitoring | Final Review에서 selected 된 전략을 monitoring portfolio에 담아 이후 성과와 review signal을 확인한다. 현재 위치는 개념적으로 타당하다. |
| `Operations > Backtest Run History` | Mixed / archive + recovery | 과거 run을 되살려 form 복원, rerun, Practical Validation handoff를 할 수 있다. 주 workflow라기보다 재현/감사용 보조 화면이다. |
| `Operations > Candidate Library` | Mixed / archive + replay | legacy/current/pre-live 후보를 다시 inspect하고 result curve를 rebuild한다. 새 후보 생성 단계가 아니라 보관함이다. |
| `Workspace > Backtest` | User-facing research workflow | 후보 생성, Practical Validation, Final Review가 있는 active workbench. 선정 후 monitoring은 여기서 벗어나는 것이 맞다. |
| `Workspace > Ingestion` | Mixed / data operations | 데이터 수집 action surface. Ops Review와 일부 health context가 겹친다. |
| `Reference > Guides / Glossary` | Reference | workflow 의미와 용어 설명. Operations 개편 후에도 route guide의 landing target으로 유효하다. |

## Strengths

- Stage ownership 자체는 좋다. Backtest가 research/build, Final Review가 decision, Selected Dashboard가 post-selection monitoring을 맡는다.
- Selected Dashboard의 no-live-boundary가 반복적으로 표시된다. 승인, 주문, account sync, auto rebalance를 만들지 않는 점이 분명하다.
- Operations 보조 화면들은 이미 스스로 "주 workflow가 아니라 보관함/재현/점검 도구"라고 설명한다.
- `Ops Review`는 실행 실패, artifact, log, runtime snapshot을 한곳에 모아 시스템 운영 콘솔의 seed가 된다.
- `Backtest Run History`와 `Candidate Library`는 오래된 registry / saved contract를 보존하면서 최신 흐름으로 다시 진입하는 안전한 bridge다.
- Navigation grouping이 이미 넓은 레벨에서는 맞다. 대규모 라우팅 재작성 없이 정보 위계를 개선할 여지가 있다.

## Weaknesses

- `Operations` 안의 화면들이 같은 중요도로 노출된다. 실제로는 `Selected Portfolio Dashboard`와 `Ops Review`가 primary이고, Run History / Candidate Library는 secondary archive다.
- `Operations`라는 이름 아래 시스템 운영과 portfolio monitoring이 섞여 있다. 사용자 입장에서는 "내 포트폴리오를 볼 곳"과 "앱/데이터 상태를 볼 곳"이 같이 놓인다.
- Backtest Run History는 `Practical Validation으로 보내기` 같은 workflow handoff를 품고 있어, archive 화면이 다시 primary workflow처럼 느껴질 수 있다.
- Candidate Library는 legacy Current Candidate / Pre-Live registry를 다루므로, 현재 selected-route 중심 흐름과의 관계가 더 낮은 위계로 표시되어야 한다.
- Operations landing page가 없다. 사용자가 Operations를 눌렀을 때 "오늘 확인할 것"과 "보조 도구"가 한 번에 정리되는 hub가 없다.
- Selected Dashboard는 현재 위치가 맞지만 이름이 길고 목적이 monitoring portfolio인지 selected strategy pool인지 즉시 드러나지 않는다.
- 제거 대상과 숨김 대상이 구분되어 있지 않다. legacy 화면을 삭제하면 재현/감사 기능을 잃고, 그대로 두면 주 workflow처럼 보인다.

## Product Boundaries

- Keep Final Review and Selected Portfolio Dashboard as decision support, not live approval.
- Do not turn research output into roadmap commitment without user approval.
- Keep `Backtest Run History` and `Candidate Library` as read/replay/rehydration tools unless a future task explicitly promotes them.
- Keep `Operations` free of broker order, account sync, automatic rebalance, and live deployment approval.
- Do not rewrite registry or saved JSONL as part of information-architecture cleanup.

## Audit Conclusion

`Selected Portfolio Dashboard`는 `Operations`에 있는 것이 맞다. 다만 지금의 `Operations`는 "선정 후 운영"과 "시스템 운영"과 "legacy/archive replay"가 같은 선반에 올라와 있어 개편 가치가 크다.

권장 방향은 삭제 중심이 아니라 위계 재정의다.

1. `Operations`를 "운영 현황을 보는 곳"으로 유지한다.
2. 그 안에서 `Portfolio Monitoring`과 `System Operations`를 primary로 나눈다.
3. `Backtest Run History`와 `Candidate Library`는 `Archive / Recovery Tools`로 낮춘다.
4. Selected Dashboard는 `Selected Portfolio Dashboard`라는 현재 route를 유지하되, 화면/문구상 "선정 후 monitoring portfolio"임을 더 분명히 한다.
5. 진짜 삭제는 사용 빈도와 대체 경로가 확인된 뒤에만 한다.

## 2026-06-07 Refresh

현재 code / docs 기준으로 2026-06-03 리서치의 1차 결론 일부는 이미 구현됐다.

| Area | Current fact | Implication |
| --- | --- | --- |
| Navigation | `Operations` group now contains `Operations Overview`, `Portfolio Monitoring`, `System / Data Health`, `Archive: Backtest Runs`, `Archive: Candidates`. | 단순히 Overview를 추가하는 일은 완료 상태다. 다음 개편은 top navigation peer 문제와 화면 정체성 보강이다. |
| Operations landing | `app/web/operations_overview.py` renders `Operations Console`, Today's Operations Queue, primary lanes, archive/reference lanes, no-live boundary, and completed 1차~5차 roadmap. | 현재 약점은 landing 부재가 아니라 landing이 prototype/debug 설명을 일부 품고 있고 실제 사용자가 "오늘 무엇을 봐야 하는가"를 더 강하게 밀어주지 못하는 점이다. |
| Portfolio Monitoring | `Operations > Portfolio Monitoring` is already the user-facing name; legacy file/path names keep `selected-portfolio-dashboard` compatibility. | 삭제/이동 대상이 아니다. Operations의 anchor surface로 더 강화해야 한다. |
| System / Data Health | `Ops Review` was renamed to `System / Data Health` in navigation and routes users to Ingestion / Archive tools for execution or replay. | 유지하되 Operations에서의 역할은 "inspect / triage"로 제한한다. |
| Archive screens | Run History and Candidate Library already have archive/recovery titles and warning copy. | 즉시 제거할 근거는 없다. 다만 top navigation에 primary lane과 같은 레벨로 계속 노출되는 점은 UX debt다. |

### Updated Weaknesses

- `Operations Overview`가 이미 존재하지만, 구현 문구 안에 "1차~5차 완료" 같은 개발 이력이 남아 있어 사용자용 운영 콘솔보다 작업 기록처럼 보일 수 있다.
- top navigation에서는 archive pages가 여전히 primary pages와 같은 레벨이다. 화면 안에서는 demotion이 되었지만, 첫 인상에서는 demotion이 충분하지 않다.
- `Operations`의 product identity가 아직 `Portfolio Monitoring + System/Data Health + Archive/Recovery`라는 구조 설명에 머문다. 실제 사용자는 "오늘 포트폴리오 상태가 변했나", "데이터가 믿을 만한가", "과거 실행을 복구해야 하나" 순서로 읽어야 한다.
- Portfolio Monitoring을 제외한 기능의 필요성은 "primary operations"가 아니라 "supporting operations"로 봐야 한다. 삭제 기준은 기능이 낡았는지가 아니라 active workflow에서 대체 경로가 있는지, audit/replay 손실이 없는지다.

### Keep / Improve / Remove Guidance

| Surface | Current decision | Reason |
| --- | --- | --- |
| Portfolio Monitoring | Keep and improve as primary | Final Review 이후의 유일한 user-facing monitoring surface다. |
| Operations Overview | Keep, but redesign as current-state cockpit | 이미 구현됐지만 개발 이력/설명보다 live operating queue와 portfolio state를 앞세워야 한다. |
| System / Data Health | Keep as support-primary | 데이터/실행 신뢰도 확인은 monitoring 판단 전에 필요하지만, execution screen은 아니다. |
| Archive: Backtest Runs | Keep as archive/recovery; consider hiding behind Overview later | run reproduction, form restore, validation handoff가 있어 삭제하면 감사/복구 능력을 잃는다. |
| Archive: Candidates | Keep as archive/recovery until legacy registry read paths are retired | legacy/current/pre-live snapshot inspection value가 남아 있다. |
| Development roadmap/audit expanders in Operations Overview | Remove or move to Reference/docs in a future UI pass | 제품 화면에서 task closeout처럼 보이는 정보는 Operations identity를 흐린다. |

## 2026-07-19 Reaudit

Portfolio Monitoring React Command Center V1 완료 후 현재 코드와 실제 사용 여부를 다시 확인했다. 이 재감사는 2026-06-07의 `Operations Overview`와 `System / Data Health` 유지 권고를 대체한다.

### Implemented Facts

| Surface | Current implementation | Current role |
| --- | --- | --- |
| `Operations Overview` | `app/web/operations_overview.py`가 Portfolio Monitoring 요약, evidence health, run-history 상태, 두 화면 링크를 다시 조합한다. | 독립 작업을 완료하지 못하는 중간 landing / 중복 summary다. |
| `Portfolio Monitoring` | DB-backed group/item lifecycle, 공통 기준 성과, contribution, item detail, diagnosis, macro/history/calibration을 React one-shell에서 소유한다. | 선정 후 추적을 실제로 수행하는 유일한 user-facing Operations surface다. |
| `System / Data Health` | `app/web/ops_review.py`가 run history, failure CSV, logs, artifacts, runtime marker를 검사한다. | 개발자·운영자용 내부 진단 화면이다. |
| `Workspace > Ingestion > 실행 기록 / 결과` | session result, persistent run history, recent logs, failure CSV를 이미 한 화면에서 제공한다. | 수집 실행과 실패 확인·재실행 근거를 함께 소유하는 대체 경로다. |

### User Evidence

- 2026-07-19 사용자 확인: 앱 안에서 failure CSV, 로그 파일, artifact 경로를 직접 검사하지 않는다.
- 사용자는 `Operations Overview`와 `System / Data Health`가 왜 있는지 이해하기 어렵다고 명시했다.

### Revised Classification And Decision

| Surface | Classification | Decision | Reason |
| --- | --- | --- | --- |
| `Portfolio Monitoring` | User-facing product surface | Keep as the sole visible Operations page | 실제 포트폴리오 추적 업무를 끝낼 수 있고 최신 React 제품 화면을 갖췄다. |
| `Operations Overview` | Redundant transitional surface | Remove from navigation and delete its dedicated UI/model/tests | Portfolio Monitoring과 run health를 한 번 더 요약하지만 독립 행동이나 판단을 완결하지 않는다. |
| `System / Data Health` | Internal ops console | Remove from user navigation and delete its dedicated UI | 사용하지 않는 개발 진단이며 필요한 수집 결과 확인 기능은 Ingestion에 중복 구현돼 있다. |
| Ingestion result/history/log/failure section | Mixed data-operations support | Preserve without a new diagnostic panel | 제거되는 System/Data Health의 대체 경로이며 기존 기능을 그대로 사용한다. |

### Product Implication

Operations의 제품 의미를 `Portfolio Monitoring` 하나로 좁힌다. Portfolio Monitoring에는 system run count, raw log, artifact path를 이식하지 않는다. 데이터가 없어 실제 추적을 계산할 수 없는 경우에만 해당 item/workspace 문맥에서 짧은 상태와 `Workspace > Ingestion` 이동 안내를 제공하며, 진단 수치 자체를 새 주인공으로 만들지 않는다.
