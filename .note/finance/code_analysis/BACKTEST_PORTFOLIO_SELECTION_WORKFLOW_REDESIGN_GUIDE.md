# Backtest Portfolio Selection Workflow Redesign Guide

## 목적

이 문서는 Backtest 화면의 후보 선정 흐름을 현재 5개 상단 단계에서 더 단순한 3단계 흐름으로 재정리하기 전에 필요한 코드 분석과 구현 가이드다.

현재 사용자가 지적한 핵심 문제는 다음과 같다.

- `Candidate Review`가 이름상으로는 검증 단계처럼 보이지만, 실제로는 Review Note / Current Candidate / Pre-Live record를 순서대로 저장하는 포장 UI에 가깝다.
- `Compare & Portfolio Builder`에서도 비중 조합을 만들 수 있고, `Portfolio Proposal`에서도 다시 후보를 골라 비중을 설정할 수 있어 사용자가 두 기능의 차이를 이해하기 어렵다.
- 저장된 Mix는 이미 백테스트와 Mix 검증을 통과했더라도, `Portfolio Proposal` / `Final Review`가 여전히 Current Candidate / Pre-Live 존재를 강하게 기대해 마지막 단계에서 다시 막힐 수 있다.
- 메모 입력 지점이 Review Note, Current Candidate context, Pre-Live, Final Review로 반복되어 사용자가 어떤 판단을 어디에 남겨야 하는지 흐려진다.

이 문서는 아직 구현 지시서가 아니라, 구현 전 기준 문서다. 실제 코드 수정은 사용자가 이 가이드의 방향을 확인한 뒤 진행한다.

## 목표 흐름

목표 사용자 흐름은 아래 3단계다.

| 단계 | 화면 이름 | 역할 |
|---|---|---|
| 1 | `Backtest Analysis` | Single Strategy / Compare / Saved Mix replay에서 백테스트, 1차 검증, 비중 조합을 수행한다. 통과한 결과를 실전 검증 후보로 선택한다. |
| 2 | `Practical Validation` | 1단계에서 선택한 단일 전략, Compare 후보, 저장된 비중 조합, 기존 registry 후보를 실전 투입 전 관점으로 검증한다. 중간 메모 저장을 강제하지 않는다. |
| 3 | `Final Review` | 최종 실전 후보로 선정할지, 보류 / 재검토 / 거절할지 판단한다. 사용자 최종 메모와 최종 decision record는 여기서만 남긴다. |

`Selected Portfolio Dashboard`는 Backtest 단계가 아니라 Operations 영역의 사후 확인 화면으로 유지한다.

## 사용자 End-to-End Flow

이 redesign이 끝났을 때 사용자는 아래 흐름으로 프로그램을 사용한다.

| 순서 | 위치 | 사용자가 하는 일 | 저장되는 데이터 |
|---|---|---|---|
| 1 | `Backtest > Backtest Analysis` | Single Strategy를 실행하거나, Compare에서 여러 전략을 비교하거나, 저장된 Mix를 재실행한다. | 일반 실행 이력은 `run_history`에 남지만 generated artifact로 취급한다. |
| 2 | `Backtest > Backtest Analysis` | 성과 / MDD / Sharpe / benchmark / rolling validation / Data Trust / Real-Money signal을 보고 실전 검증 후보로 선택한다. | 선택한 후보 원본은 `PORTFOLIO_SELECTION_SOURCES.jsonl`에 저장한다. |
| 3 | `Backtest > Practical Validation` | 선택한 후보가 실전 투입 전 조건을 충족하는지 본다. 단일 전략, Compare 후보, Saved Mix 모두 같은 방식으로 검증한다. | 검증 결과는 `PRACTICAL_VALIDATION_RESULTS.jsonl`에 저장한다. 사용자 최종 메모는 아직 저장하지 않는다. |
| 4 | `Backtest > Final Review` | 최종 후보로 선정할지, 보류 / 거절 / 재검토할지 판단한다. 투자 추천이나 live approval이 아니라 최종 후보 판단 record다. | 최종 판단과 사용자 최종 메모는 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에 저장한다. |
| 5 | `Operations > Selected Portfolio Dashboard` | Final Review에서 선정된 후보의 최신 성과를 다시 확인하고, original period 이후 성과 유지 여부와 review signal을 본다. | 사용자가 명시적으로 저장할 때만 `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`에 monitoring snapshot을 남긴다. |
| 6 | `Operations > Selected Portfolio Dashboard` | 필요하면 실제 또는 가상 배정 금액 기준으로 allocation check를 한다. | allocation check는 monitoring log 안의 optional snapshot으로 저장한다. 주문, 자동매매, live approval은 만들지 않는다. |

사용자가 이해해야 하는 흐름은 아래 한 줄이다.

```text
Backtest Analysis에서 만들고 고른다
Practical Validation에서 실전 검증한다
Final Review에서 최종 판단한다
Selected Portfolio Dashboard에서 선정 후 상태를 다시 본다
```

중요한 경계:

- 비중을 새로 만들거나 수정하는 작업은 `Backtest Analysis`가 맡는다.
- `Practical Validation`은 이미 선택된 후보를 검증하는 단계다. 여기서 다시 weight builder를 크게 제공하지 않는다.
- 사용자 최종 메모는 `Final Review`에만 남긴다.
- 사후관리는 최종 선정 이후의 성과 재확인과 review signal 확인이지, 주문 실행이나 live approval이 아니다.

## 현재 코드의 실제 흐름

### 상단 화면 라우팅

현재 Backtest 상단 선택자는 실제 `st.tabs`가 아니라 `segmented_control` 또는 `radio` 기반 selector다.

| 파일 | 현재 책임 |
|---|---|
| `app/web/backtest_common.py` | `BACKTEST_PANEL_OPTIONS`, `BACKTEST_WORKFLOW_PANEL_OPTIONS`, `_init_backtest_state()`, `_request_backtest_panel()`, `_activate_backtest_workflow_panel()`로 상단 panel label과 session route를 관리한다. |
| `app/web/pages/backtest.py` | `_render_backtest_panel_selector()`로 selector를 그리고, `render_backtest_tab()`에서 active panel 문자열을 기준으로 각 workspace renderer를 호출한다. |

현재 route label은 아래 5개가 session contract처럼 쓰이고 있다.

```text
Single Strategy
Compare & Portfolio Builder
Candidate Review
Portfolio Proposal
Final Review
```

따라서 이 5개 문자열을 바로 3개 label로 치환하면 기존 handoff가 깨진다. `backtest_requested_panel = "Candidate Review"` 같은 기존 요청이 거부되거나, `render_backtest_tab()`의 fallback이 잘못된 화면을 렌더링할 수 있다.

### Single Strategy handoff

| 파일 | 현재 흐름 |
|---|---|
| `app/web/backtest_single_runner.py` | 실행 성공 시 `st.session_state.backtest_last_bundle`에 result bundle을 저장한다. |
| `app/web/backtest_result_display.py` | `Review As Candidate Draft` 버튼이 `_candidate_review_draft_from_bundle()`로 draft를 만들고 `_queue_candidate_review_draft()`로 Candidate Review로 보낸다. |
| `app/web/backtest_candidate_review_helpers.py` | draft 생성과 Candidate Review queue helper를 제공한다. |

현재 session handoff key:

```text
backtest_last_bundle
backtest_candidate_review_draft
backtest_candidate_review_draft_notice
backtest_requested_panel = "Candidate Review"
```

### Compare 개별 후보 handoff

| 파일 | 현재 흐름 |
|---|---|
| `app/web/backtest_compare.py` | Compare 실행 후 `backtest_compare_bundles`, `backtest_compare_source_context`, `backtest_weighted_bundle` 등을 채운다. |
| `app/web/backtest_compare.py` | `_render_candidate_draft_readiness_box()`가 선택한 전략 bundle을 Candidate Review draft로 queue한다. |

현재 버튼과 문구는 `5단계 Compare`, `6단계 Candidate Review`, `Send Selected Strategy To Candidate Review`를 전제로 한다.

### Saved Mix handoff

| 파일 | 현재 흐름 |
|---|---|
| `app/web/backtest_compare.py` | `_render_save_weighted_portfolio_panel()`이 reusable saved portfolio setup을 저장한다. |
| `app/web/backtest_compare.py` | `_run_saved_portfolio_record()`가 저장된 비중 조합을 replay해 `backtest_compare_bundles`, `backtest_weighted_bundle`, `backtest_saved_portfolio_replay_id`를 채운다. |
| `app/web/backtest_compare.py` | `_build_saved_mix_proposal_prefill_payload()`가 Portfolio Proposal prefill payload를 만든다. |
| `app/web/backtest_compare.py` | `_render_saved_mix_validation_board()`가 `portfolio_proposal_saved_mix_prefill`을 설정하고 `Portfolio Proposal`로 이동한다. |

Saved Mix는 이미 Candidate Review를 건너뛰고 Portfolio Proposal로 간다. 이 방향 자체는 맞지만, 현재는 Proposal 화면으로 이동한 뒤 다시 Current Candidate 기반 기능과 섞이기 때문에 사용자에게 목적이 흐려진다.

### Candidate Review의 실제 성격

Candidate Review는 투자 검증 단계라기보다 저장 가능한 후보 포장 단계다.

| 함수 | 실제 역할 |
|---|---|
| `_build_candidate_intake_readiness_evaluation()` | draft가 Review Note로 저장될 만큼 완성됐는지 본다. |
| `_build_candidate_review_note_from_draft()` | draft를 `CANDIDATE_REVIEW_NOTES.jsonl` row로 변환한다. |
| `_build_candidate_registry_scope_evaluation()` | Review Note를 Current Candidate / near miss / scenario로 올릴 수 있는지 본다. |
| `_build_current_candidate_registry_row_from_review_note()` | Review Note를 `CURRENT_CANDIDATE_REGISTRY.jsonl` row로 변환한다. |
| `_build_candidate_board_operating_evaluation()` | 저장된 candidate row가 Pre-Live 또는 Compare 재검토로 갈지 본다. |
| `_build_pre_live_draft_from_current_candidate()` | Current Candidate row를 Pre-Live record draft로 변환한다. |
| `_build_pre_live_operating_readiness_evaluation()` | Pre-Live record 저장과 Portfolio Proposal 이동 가능 여부를 본다. |

저장 파일:

| 파일 | 현재 의미 |
|---|---|
| `.note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl` | 후보 검토 노트. 사용자가 별도 reason / next action을 입력한다. |
| `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl` | 현재 후보 / near-miss / scenario registry. Candidate Library와 replay helper가 읽는다. |
| `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | paper tracking / watchlist / hold / reject 같은 운영 상태 record. |

이 세 저장소는 compatibility와 기존 후보 조회를 위해 유지해야 하지만, 새 주 흐름에서 사용자가 순서대로 직접 저장해야 하는 필수 단계로 보이면 안 된다.

### Portfolio Proposal의 실제 성격

`Portfolio Proposal`은 두 가지 역할이 섞여 있다.

| 경로 | 현재 의미 |
|---|---|
| Current Candidate Components | `CURRENT_CANDIDATE_REGISTRY.jsonl`에서 후보를 고르고 비중을 설정해 proposal을 만든다. |
| Saved Mix prefill | Compare에서 검증한 저장된 비중 조합을 proposal row로 저장할 수 있게 한다. |
| Validation Pack | proposal 또는 단일 후보를 practical portfolio 후보로 볼 수 있는지 검증한다. |
| Saved Proposal review | 저장된 proposal의 blocker, component, paper feedback을 다시 확인한다. |

사용자가 느끼는 충돌은 여기서 발생한다.

- Compare에서 이미 비중 조합을 만들었는데 Portfolio Proposal에서 다시 비중 조합 UI가 보인다.
- Saved Mix는 이미 완성된 조합인데 Proposal Components에는 보이지 않는다.
- Proposal 저장이 Final Review 전 필수처럼 느껴지지만, 실제 사용자는 Final Review에서 최종 메모를 남기고 싶어 한다.

### Final Review의 현재 기대 schema

| 파일 | 현재 책임 |
|---|---|
| `app/web/backtest_final_review.py` | Final Review UI를 렌더링하고 최종 판단 row를 저장한다. |
| `app/web/backtest_final_review_helpers.py` | source option, validation, evidence pack, paper observation snapshot, final decision row를 만든다. |
| `app/web/runtime/final_selected_portfolios.py` | 최종 선정 row를 읽어 Selected Portfolio Dashboard용 read model과 recheck를 만든다. |

현재 Final Review source는 사실상 두 종류다.

```text
single_candidate
portfolio_proposal
```

즉, session에만 있는 Saved Mix validation source나 Compare에서 막 선택한 후보를 직접 읽지 않는다. 결국 Practical Validation에서 Final Review로 넘기려면, 기존 source option 계약에 맞는 row를 만들거나 Final Review가 새 session source를 읽을 수 있게 해야 한다.

## 핵심 병목

### 1. Stage label과 internal route가 분리되어 있지 않다

현재 `Single Strategy`, `Compare & Portfolio Builder`, `Candidate Review`, `Portfolio Proposal`, `Final Review` label은 화면 이름이면서 동시에 route key다.

3단계 UX로 바꾸려면 아래를 분리해야 한다.

| 개념 | 예시 |
|---|---|
| visible stage | `Backtest Analysis`, `Practical Validation`, `Final Review` |
| internal workspace | `single_strategy`, `compare_builder`, `saved_mix_replay`, `current_candidate_validation`, `saved_mix_validation`, `legacy_registry_tools` |
| source kind | `latest_backtest_run`, `compare_focused_strategy`, `saved_portfolio_mix`, `current_candidate`, `portfolio_proposal` |

### 2. Candidate Review는 validation보다 storage workflow에 가깝다

기존 Candidate Review helper 중 readiness 판정은 재사용 가치가 있지만, UI 자체는 반복 메모 / 반복 저장을 만든다.

따라서 새 주 흐름에서는 아래처럼 재배치한다.

| 기존 요소 | 새 위치 |
|---|---|
| draft completeness 판정 | Practical Validation source intake check |
| Current Candidate Registry 저장 | 선택적 legacy / compatibility 저장 |
| Review Note 저장 | 필수 단계에서 제거. 필요하면 audit note로만 보조 제공 |
| Pre-Live record 저장 | Practical Validation의 paper observation / operating status 입력으로 흡수 |
| Portfolio Proposal 이동 버튼 | Practical Validation 안의 Final Review 이동으로 대체 |

### 3. Saved Mix는 final source로 충분한 정보를 갖지만, 현재 검증 helper가 legacy registry 존재를 기대한다

Saved Mix payload에는 `saved_portfolio_id`, `saved_portfolio_name`, `compare_context`, `portfolio_context`, `weighted_summary`, `weighted_period`, `components`가 있다.

하지만 Final Review / Portfolio Risk helper는 current candidate와 pre-live row를 찾으려 한다. Saved Mix component가 synthetic id이면 다음 문제가 생긴다.

- `has_current_candidate = False`
- `has_pre_live_record = False`
- paper/pre-live gap 때문에 최종 선정 route가 막힐 수 있음
- Selected Dashboard recheck가 `registry_id` 기반 replay에서 막힐 수 있음

이 문제는 데이터 부족이 아니라 source contract mismatch다. Saved Mix 전용 검증을 통과했다면 그 검증 결과를 Practical Validation source contract로 Final Review에 넘겨야 한다.

### 4. Final memo는 Final Review로 모으는 편이 맞다

현재는 Review Note, Pre-Live, Proposal, Final Review에 사용자 입력이 흩어진다. 새 흐름에서는 다음처럼 단순화한다.

| 입력 | 위치 |
|---|---|
| 백테스트 설정 / 조합 설정 | Backtest Analysis |
| 검증 checklist / blocker 확인 | Practical Validation |
| 최종 판단 이유 / 제약 / 다음 행동 | Final Review |

## 목표 설계

### Stage / route 설계

상단 visible stage는 3개로 줄인다.

```text
Backtest Analysis
Practical Validation
Final Review
```

다만 기존 route label은 바로 제거하지 않는다. 호환 layer를 둔다.

| legacy route | 새 visible stage | 새 internal mode |
|---|---|---|
| `Single Strategy` | `Backtest Analysis` | `single_strategy` |
| `Compare & Portfolio Builder` | `Backtest Analysis` | `compare_builder` |
| `Candidate Review` | `Practical Validation` | `selected_candidate_validation` 또는 `legacy_registry_tools` |
| `Portfolio Proposal` | `Practical Validation` | `portfolio_validation` |
| `Final Review` | `Final Review` | `final_review` |

권장 session key:

```text
backtest_active_stage
backtest_requested_stage
backtest_analysis_mode
backtest_practical_validation_mode
backtest_practical_validation_source
backtest_practical_validation_notice
```

기존 key는 compatibility로 유지한다.

```text
backtest_active_panel
backtest_workflow_active_panel
backtest_requested_panel
backtest_candidate_review_draft
portfolio_proposal_saved_mix_prefill
```

### Practical Validation source contract

Practical Validation은 저장소 이름이 아니라 “검증 대상 source”를 중심으로 동작해야 한다.

권장 최소 source shape:

```json
{
  "schema_version": 1,
  "source_kind": "latest_backtest_run | compare_focused_strategy | saved_portfolio_mix | current_candidate | portfolio_proposal",
  "source_id": "...",
  "source_title": "...",
  "source_created_at": "...",
  "period": {
    "start": "...",
    "end": "...",
    "actual_start": "...",
    "actual_end": "..."
  },
  "summary": {
    "cagr": null,
    "mdd": null,
    "sharpe": null,
    "benchmark_cagr": null,
    "benchmark_mdd": null
  },
  "data_trust": {
    "status": "pass | warn | review | blocked",
    "warnings": []
  },
  "real_money_signal": {
    "route": "...",
    "blockers": [],
    "review_gaps": []
  },
  "components": [
    {
      "component_id": "...",
      "registry_id": null,
      "title": "...",
      "strategy_family": "...",
      "strategy_key": "...",
      "target_weight": 100.0,
      "benchmark": "...",
      "universe": [],
      "baseline_cagr": null,
      "baseline_mdd": null,
      "baseline_sharpe": null,
      "data_trust_status": "...",
      "replay_contract": {}
    }
  ],
  "construction": {
    "source": "single_strategy | compare_mix | saved_mix | legacy_proposal",
    "target_weight_total": 100.0,
    "rebalance_cadence": "..."
  },
  "validation": {
    "route": "READY_FOR_FINAL_REVIEW | NEEDS_REVIEW | BLOCKED",
    "score": null,
    "checks": [],
    "blockers": [],
    "review_gaps": []
  },
  "paper_observation": {
    "mode": "inline_paper_observation",
    "route": "PAPER_OBSERVATION_READY | PAPER_OBSERVATION_REVIEW | PAPER_OBSERVATION_BLOCKED",
    "baseline_snapshot": {},
    "review_cadence": "monthly_or_rebalance_review",
    "review_triggers": []
  }
}
```

중요한 점:

- `registry_id`는 있으면 유지하지만, Saved Mix처럼 registry row가 없는 source는 synthetic id만으로 Final Review를 막지 않는다.
- Selected Dashboard recheck를 살리려면 `replay_contract` 또는 saved mix replay context를 component에 보존해야 한다.
- 최종 메모는 source contract에 넣지 않고 Final Review decision row에만 저장한다.

### 저장소 재설계: Compatibility Mode vs Clean V2 Mode

이 문서의 첫 분석은 기존 JSONL을 가능한 한 유지하는 compatibility 관점이 강했다. 그러나 대규모 개편을 전제로 하면 기존 JSONL을 main source로 계속 끌고 갈 필요는 없다.

두 가지 선택지가 있다.

| 모드 | 설명 | 장점 | 단점 |
|---|---|---|---|
| `Compatibility Mode` | 기존 `CURRENT_CANDIDATE_REGISTRY`, `PRE_LIVE`, `PORTFOLIO_PROPOSAL` 등을 계속 읽고, 새 3단계 workflow를 그 위에 얹는다. | 기존 후보 / proposal / final decision을 바로 다시 볼 수 있다. | 기존 저장 단계와 join 조건이 계속 남아 UX와 코드가 복잡하다. |
| `Clean V2 Mode` | 기존 JSONL은 archive로 보관하고, 새 workflow 전용 JSONL을 새로 만든다. | 3단계 workflow와 저장 구조가 일치한다. 반복 메모 / 반복 저장 문제가 줄어든다. | 기존 JSONL을 새 UI의 main source로 자동 이관하지 않는다. 필요하면 legacy viewer로만 본다. |

이 redesign의 권장안은 `Clean V2 Mode`다.

이유:

- 사용자가 지적한 문제는 기존 저장소를 너무 적극적으로 재사용하면서 생긴 workflow 복잡성이다.
- `Review Note -> Current Candidate -> Pre-Live -> Proposal -> Final Decision` 체인을 계속 유지하면 3단계 UI로 바꿔도 내부 개념이 다시 새어 나온다.
- 기존 JSONL은 연구 기록으로 가치가 있지만, 새 UX의 source-of-truth가 될 필요는 없다.

### 기존 JSONL archive 정책

Clean V2 Mode를 선택하면 기존 registry 파일은 삭제하지 않고 archive한다.

권장 위치:

```text
.note/finance/archive/legacy_portfolio_workflow_v1/20260510/registries/
```

archive 대상:

```text
.note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl
.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl
.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl
.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl
.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl
.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl
```

archive 후 main workflow는 이 파일들을 필수 join 조건으로 사용하지 않는다.

허용되는 사용:

- legacy inspector에서 과거 후보를 읽는다.
- 필요하면 수동 migration helper로 특정 record를 새 `PORTFOLIO_SELECTION_SOURCES.jsonl`에 복사한다.
- 과거 분석의 감사 기록으로 보관한다.

금지할 사용:

- 새 Practical Validation 통과 조건으로 old Current Candidate row 존재를 요구한다.
- 새 Final Review 통과 조건으로 old Pre-Live row 존재를 요구한다.
- Saved Mix가 old proposal registry에 없다는 이유만으로 막는다.

### Clean V2 저장 파일

Clean V2 Mode에서는 아래 파일들이 새 main source-of-truth다.

| 파일 | 저장 시점 | 역할 |
|---|---|---|
| `.note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl` | Backtest Analysis에서 사용자가 `실전 검증 후보로 선택`을 누를 때 | 단일 전략, Compare focused strategy, Saved Mix를 같은 source contract로 저장한다. |
| `.note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl` | Practical Validation에서 사용자가 `검증 결과 저장` 또는 `Final Review로 보내기`를 누를 때 | blocker, review gap, data trust, real-money signal, robustness, paper observation 기준을 저장한다. 사용자 최종 메모는 저장하지 않는다. |
| `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` | Final Review에서 사용자가 최종 판단을 저장할 때 | select / hold / reject / re-review 판단과 최종 사용자 메모, 선택된 component, evidence snapshot을 저장한다. |
| `.note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` | Selected Portfolio Dashboard에서 사용자가 monitoring snapshot 저장을 명시할 때 | 선정 이후 performance recheck, review signal, optional allocation check snapshot을 저장한다. |
| `.note/finance/saved/SAVED_PORTFOLIO_MIXES.jsonl` | Backtest Analysis에서 사용자가 reusable mix setup을 저장할 때 | 다시 실행 가능한 비중 조합 설정을 저장한다. 검증 결과나 최종 판단이 아니다. |

`run_history/*.jsonl`은 계속 local generated artifact다. 재실행 convenience에는 쓰지만, 후보 선정 workflow의 영구 source-of-truth로 보지 않는다.

### Clean V2 record 관계

새 저장 구조는 아래처럼 단순하게 연결한다.

```text
PORTFOLIO_SELECTION_SOURCES
  -> PRACTICAL_VALIDATION_RESULTS
    -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2
      -> SELECTED_PORTFOLIO_MONITORING_LOG
```

권장 id 관계:

| record | 주요 id | 참조 |
|---|---|---|
| Selection Source | `selection_source_id` | source run / saved mix / replay contract를 내부 snapshot으로 보존 |
| Practical Validation Result | `validation_id` | `selection_source_id` 참조 |
| Final Decision V2 | `decision_id` | `selection_source_id`, `validation_id` 참조 |
| Monitoring Log | `monitoring_id` | `decision_id`, 선택적으로 `selection_source_id` 참조 |

중요한 점:

- `selection_source_id`가 새 workflow의 후보 기준 id다.
- 기존 `registry_id`는 있으면 legacy reference로만 보존한다.
- Selected Portfolio Dashboard는 `decision_id`를 기준으로 선정 포트폴리오를 읽는다.
- replay는 old registry join이 아니라 selection source의 `replay_contract` 또는 saved mix context를 우선 사용한다.

### Clean V2에서 저장하지 않는 것

새 workflow는 아래를 기본 저장하지 않는다.

| 저장하지 않는 것 | 이유 |
|---|---|
| 별도 Review Note | 최종 판단 전 중간 메모가 반복되기 때문이다. |
| 별도 Pre-Live record | Practical Validation의 paper observation snapshot으로 충분하다. |
| 별도 Portfolio Proposal draft | Compare / Saved Mix에서 이미 비중 조합을 만들었고, Final Review evidence에 구성 정보를 담을 수 있다. |
| Paper Tracking Ledger 필수 저장 | Final Review 전 필수 단계처럼 보이면 workflow가 다시 길어진다. |

필요하면 advanced export나 legacy compatibility로 만들 수 있지만, main workflow의 필수 단계로 두지 않는다.

### Practical Validation 화면 구조

`Practical Validation`은 기존 Candidate Review와 Portfolio Proposal을 합친 새 주 화면이다.

권장 submode:

| submode | 역할 |
|---|---|
| `Selected Source` | Backtest Analysis에서 넘어온 단일 전략 / Compare 후보 / Saved Mix를 바로 검증한다. |
| `Saved Mix` | 저장된 비중 조합을 직접 선택해 재실행 / 검증 / Final Review 이동을 제공한다. |
| `Current Candidate Components` | 기존 Current Candidate Registry 후보를 조합하거나 단일 후보로 검증하는 compatibility 경로다. |
| `Saved Proposals` | 기존 저장 proposal을 읽는 compatibility 경로다. |
| `Legacy Registry Tools` | Review Note / Current Candidate / Pre-Live raw inspector가 필요할 때만 접어둔다. |

기본 화면은 `Selected Source`다. 사용자가 Compare에서 저장된 Mix를 검증하고 이동했다면, Current Candidate Components 대신 해당 Mix 검증 결과가 먼저 보여야 한다.

### Weight editing 위치

비중을 새로 실험하는 행위는 `Backtest Analysis`에 둔다.

| 행위 | 위치 |
|---|---|
| 여러 전략을 비교한다 | Backtest Analysis |
| 전략별 비중을 조정하고 Mix를 만든다 | Backtest Analysis |
| 저장된 Mix를 재실행한다 | Backtest Analysis 또는 Practical Validation의 Saved Mix source loader |
| 이미 선택된 Mix가 실전 검증에 충분한지 본다 | Practical Validation |
| 최종 판단과 메모를 남긴다 | Final Review |

Practical Validation에서 비중을 다시 수정할 수 있게 하면 `Compare`와 같은 기능이 반복된다. 따라서 새 주 흐름에서는 Practical Validation의 비중 수정은 기본적으로 막고, 필요하면 “Backtest Analysis에서 조합 수정”으로 돌려보내는 편이 낫다.

기존 `Portfolio Proposal`의 multi-candidate weight builder는 compatibility 또는 advanced path로 남긴다.

### Final Review source 확장

Final Review는 아래 source를 읽을 수 있어야 한다.

| source | 처리 |
|---|---|
| session Practical Validation source | 사용자가 방금 검증한 source를 최우선으로 보여준다. |
| saved portfolio proposal row | 기존 proposal registry 호환 유지 |
| current candidate row | 기존 단일 후보 호환 유지 |

기존 `single_candidate` / `portfolio_proposal` source type은 유지하되, 새 source type을 추가한다.

```text
practical_validation_source
saved_mix_validation
```

Final Review decision row에는 아래가 반드시 들어가야 한다.

- `source_type`
- `source_id`
- `source_title`
- `selected_components`
- `decision_evidence_snapshot`
- `risk_and_validation_snapshot`
- `paper_tracking_snapshot` 또는 inline paper observation snapshot
- `operator_reason`
- `operator_constraints`
- `operator_next_action`
- `decision_route`
- `selected_practical_portfolio`

## 구현 파일별 가이드

### 새로 두는 것이 좋은 파일

| 파일 | 책임 |
|---|---|
| `app/web/backtest_workflow_routes.py` | visible stage, legacy route, internal mode mapping을 한 곳에서 관리한다. |
| `app/web/backtest_analysis.py` | Single Strategy / Compare & Portfolio Builder를 `Backtest Analysis` stage 안에서 렌더링하는 wrapper다. |
| `app/web/backtest_practical_validation.py` | 새 2단계 화면. selected source, saved mix, current candidate compatibility, saved proposal compatibility를 렌더링한다. |
| `app/web/backtest_practical_validation_helpers.py` | source contract 변환, validation input 생성, Final Review handoff payload 생성을 담당한다. |

새 파일을 두는 이유는 기존 `backtest_candidate_review.py`와 `backtest_portfolio_proposal.py`를 한 번에 덮어쓰면 regression 위험이 크기 때문이다. 기존 파일은 legacy / compatibility surface로 남기고, 새 3단계 주 흐름을 얇은 orchestration layer로 만든 뒤 점진적으로 내부 helper를 재사용한다.

### 수정 대상 파일

| 파일 | 수정 방향 |
|---|---|
| `app/web/backtest_common.py` | 3개 visible stage와 legacy route mapping을 추가한다. 기존 panel key는 바로 삭제하지 않는다. |
| `app/web/pages/backtest.py` | 상단 selector를 3단계 기준으로 바꾸고, `Backtest Analysis` / `Practical Validation` / `Final Review` renderer로 dispatch한다. |
| `app/web/backtest_result_display.py` | `Candidate Review Handoff`를 Practical Validation handoff로 바꾼다. Single result를 새 source contract로 queue한다. |
| `app/web/backtest_compare.py` | Compare 개별 후보와 Saved Mix의 handoff를 Practical Validation source로 바꾼다. 기존 saved mix replay와 cadence-aware validation은 유지한다. |
| `app/web/backtest_history.py` | history replay는 Backtest Analysis stage로 보내고, candidate draft handoff는 Practical Validation source로 바꾼다. |
| `app/web/backtest_candidate_review_helpers.py` | draft 변환과 readiness helper 일부를 재사용한다. `_queue_candidate_review_draft()`는 legacy wrapper로 유지하거나 Practical Validation queue를 호출하도록 바꾼다. |
| `app/web/backtest_portfolio_proposal.py` | 기존 UI는 compatibility로 유지한다. saved mix proposal prefill에서 새 Practical Validation source 생성도 지원한다. 누락된 paper threshold constant import 위험도 함께 고친다. |
| `app/web/backtest_portfolio_proposal_helpers.py` | validation helper가 source kind에 따라 Current Candidate / Pre-Live 미존재를 hard blocker로 볼지 review gap으로 볼지 분기할 수 있게 한다. |
| `app/web/backtest_final_review.py` | session Practical Validation source를 source option으로 보여준다. |
| `app/web/backtest_final_review_helpers.py` | 새 source type validation, evidence pack, final decision row 생성을 지원한다. |
| `app/web/runtime/final_selected_portfolios.py` | saved mix / practical validation source에서 온 selected component의 replay contract fallback을 지원한다. |
| `app/web/overview_dashboard_helpers.py` | funnel / next action 문구를 3단계 기준으로 바꾼다. |
| `app/web/reference_guides.py` | 1~10단계 guide와 Candidate Review 중심 설명을 3단계 기준으로 재작성한다. |

### 문서 수정 대상

| 문서 | 수정 방향 |
|---|---|
| `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md` | 3단계 workflow 기준의 실제 화면 / handoff 흐름으로 갱신한다. |
| `.note/finance/code_analysis/SCRIPT_STRUCTURE_MAP.md` | 새 파일이 생기면 책임 map에 추가한다. |
| `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md` | Backtest UI 현재 시스템 설명을 새 3단계 기준으로 갱신한다. |
| `.note/finance/FINANCE_DOC_INDEX.md` | 새 guide 문서와 workflow 설명을 index에 연결한다. |
| `.note/finance/QUESTION_AND_ANALYSIS_LOG.md` | 사용자의 UX 문제 제기와 최종 설계 판단을 기록한다. |
| `.note/finance/WORK_PROGRESS.md` | 구현 시작, 주요 milestone, 완료 상태를 append한다. |
| `README.md` | top-level Backtest workflow 설명이 바뀌면 갱신한다. |

## 단계별 구현 순서

### 0단계. 분석 문서 고정

현재 단계다.

- 현 코드의 route / session key / JSONL dependency를 문서화한다.
- 새 3단계 workflow의 구현 순서를 정한다.
- 실제 제품 코드는 아직 수정하지 않는다.

### 1단계. Legacy archive + Clean V2 storage foundation

목표는 기존 JSONL을 새 workflow의 필수 source-of-truth에서 분리하고, 새 저장소를 먼저 세우는 것이다.

작업:

- 기존 registry JSONL을 `.note/finance/archive/legacy_portfolio_workflow_v1/<date>/registries/`로 archive한다.
- `.note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl` helper를 추가한다.
- `.note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl` helper를 추가한다.
- `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` helper를 추가한다.
- `.note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` helper를 추가한다.
- `.note/finance/saved/SAVED_PORTFOLIO_MIXES.jsonl` helper를 추가한다.
- legacy registry helper는 삭제하지 않고 legacy inspector / one-time import 용도로만 남긴다.

검증:

- 빈 V2 JSONL 상태에서 앱이 시작되어야 한다.
- 기존 JSONL이 없어도 Backtest Analysis -> Practical Validation -> Final Review route가 막히지 않아야 한다.
- legacy archive 파일은 main UI validation 조건으로 사용되지 않아야 한다.

### 2단계. Route foundation and stage separation

목표는 화면 이름 변경 전에 route와 stage를 분리하는 것이다.

작업:

- `backtest_workflow_routes.py`를 추가한다.
- visible stage 3개와 legacy route 5개의 mapping을 정의한다.
- `_request_backtest_panel()`이 legacy route 요청을 새 stage / internal mode로 해석할 수 있게 한다.
- `backtest_active_panel` 계열 기존 key는 유지한다.
- `Portfolio Proposal`의 paper threshold constant import 누락 같은 독립 NameError 위험을 먼저 고친다.

검증:

- 기존 5개 route 요청이 모두 동작해야 한다.
- Single -> Candidate Review legacy handoff가 깨지지 않아야 한다.
- Saved Mix -> Portfolio Proposal legacy handoff가 깨지지 않아야 한다.

### 3단계. Backtest Analysis stage 도입

작업:

- `backtest_analysis.py` wrapper를 추가한다.
- 상단 selector에는 `Backtest Analysis`, `Practical Validation`, `Final Review`를 보여준다.
- `Backtest Analysis` 내부에서 `Single Strategy`, `Compare & Portfolio Builder`를 submode로 제공한다.
- Compare 내부 `개별 전략 비교`, `저장된 비중 조합` mode는 유지한다.
- History `Load Into Form`은 `Backtest Analysis` stage + Single submode로 이동하게 한다.

검증:

- Single Strategy 실행과 결과 표시가 기존처럼 동작한다.
- Compare 실행, weighted mix 저장, saved mix replay가 기존처럼 동작한다.
- 기존 session prefill이 새 stage에서도 복원된다.

### 4단계. Practical Validation source queue 도입

작업:

- `backtest_practical_validation_helpers.py`에 source builder를 둔다.
- Single result bundle, Compare focused bundle, Saved Mix replay payload, History record를 공통 Practical Validation source로 변환한다.
- `_queue_practical_validation_source(source)`를 추가한다.
- 기존 `_queue_candidate_review_draft()`는 바로 삭제하지 않고 compatibility wrapper로 둔다.

권장 queue key:

```text
backtest_practical_validation_source
backtest_practical_validation_notice
backtest_requested_stage = "Practical Validation"
backtest_practical_validation_mode = "Selected Source"
```

검증:

- Single result에서 `실전 검증 후보로 선택` 버튼이 Practical Validation으로 이동해야 한다.
- Compare 개별 후보에서 같은 이동이 되어야 한다.
- Saved Mix validation board에서 같은 이동이 되어야 한다.

### 5단계. Practical Validation UI 구현

작업:

- `backtest_practical_validation.py`를 추가한다.
- 기본 화면은 session selected source를 보여준다.
- Saved Mix source loader를 제공한다.
- Current Candidate Components와 Saved Proposals는 compatibility submode로 제공한다.
- Review Note / Pre-Live 저장은 기본 플로우에서 빼고 advanced / legacy inspector로 접는다.
- 검증 결과는 blocker / review gap / data trust / real-money signal / paper observation 기준으로 보여준다.
- 최종 메모 입력은 받지 않고, `Final Review로 이동`만 제공한다.

검증:

- 저장된 Mix `GTAA SPY Low-MDD 60 + EW Growth/Sector/Gold 40`가 Current Candidate 없이도 Practical Validation source로 표시되어야 한다.
- Current Candidate가 없는 saved mix synthetic component가 hard blocker로만 처리되지 않아야 한다.
- 비중 수정은 기본 화면에서 반복 제공하지 않아야 한다.

### 6단계. Final Review source 확장

작업:

- `Final Review` source option에 session Practical Validation source를 추가한다.
- 새 source type을 validation helper가 읽도록 한다.
- Practical Validation에서 확인한 inline paper observation / validation snapshot을 Final Review decision evidence pack으로 넘긴다.
- Final memo는 Final Review에서만 받는다.

검증:

- 방금 Practical Validation을 통과한 source가 Final Review 첫 option으로 보여야 한다.
- 기존 current candidate / saved proposal source도 계속 보여야 한다.
- 저장된 final decision row가 Selected Dashboard에서 읽을 수 있어야 한다.

### 7단계. Selected Portfolio Dashboard replay fallback

작업:

- `selected_components`에 실제 `registry_id`가 없더라도 source snapshot을 표시할 수 있어야 한다.
- replay가 가능한 경우에는 `replay_contract` 또는 saved mix context로 recheck를 시도한다.
- replay contract가 부족하면 recheck failure를 blocker가 아니라 “snapshot-only component”로 표시한다.

검증:

- Current Candidate 기반 final decision은 기존처럼 recheck된다.
- Saved Mix 기반 final decision은 최소한 snapshot / allocation / baseline evidence가 표시된다.
- 가능한 경우 saved mix replay contract로 performance recheck가 동작한다.

### 8단계. Guide / docs sync

작업:

- `reference_guides.py`의 1~10단계 설명을 3단계 기준으로 재작성한다.
- Candidate Review / Portfolio Proposal / Pre-Live 설명은 legacy registry / compatibility로 낮춘다.
- `WEB_BACKTEST_UI_FLOW.md`, `SCRIPT_STRUCTURE_MAP.md`, `FINANCE_COMPREHENSIVE_ANALYSIS.md`, `FINANCE_DOC_INDEX.md`, `README.md`를 갱신한다.

검증:

- 사용자-facing guide가 `Candidate Review 저장 -> Portfolio Proposal 저장 -> Final Review`를 필수 경로처럼 설명하지 않아야 한다.
- Saved Mix 경로는 `Mix 검증 -> Practical Validation -> Final Review`로 읽혀야 한다.

## 검증 계획

### 정적 검증

```bash
python3 -m py_compile \
  app/web/pages/backtest.py \
  app/web/backtest_common.py \
  app/web/backtest_analysis.py \
  app/web/backtest_practical_validation.py \
  app/web/backtest_practical_validation_helpers.py \
  app/web/backtest_result_display.py \
  app/web/backtest_compare.py \
  app/web/backtest_history.py \
  app/web/backtest_final_review.py \
  app/web/backtest_final_review_helpers.py
```

추가로 변경 범위에 따라 아래도 실행한다.

```bash
python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

### Streamlit 수동 QA

| 경로 | 기대 결과 |
|---|---|
| Single Strategy 실행 -> 실전 검증 후보 선택 | Practical Validation에 단일 source가 표시된다. |
| Compare 개별 전략 실행 -> 실전 검증 후보 선택 | Practical Validation에 선택 전략 source가 표시된다. |
| Compare saved mix replay -> Mix 재실행 및 검증 -> Final Review 이동 | Current Candidate 없이도 Practical Validation source와 Final Review source가 이어진다. |
| 기존 Current Candidate 선택 | compatibility 경로에서 기존 후보 검증이 가능하다. |
| 기존 saved proposal 선택 | 기존 proposal이 Final Review에서 계속 읽힌다. |
| Final Review selected decision 저장 | Selected Portfolio Dashboard가 final decision을 읽는다. |
| 빈 V2 registry에서 새 후보 선택 | 기존 JSONL 없이 `Selection Source -> Practical Validation -> Final Review`가 이어진다. |
| legacy archive 이후 앱 시작 | legacy registry가 없어도 main workflow가 crash하지 않는다. |
| monitoring snapshot 저장 | Final Review에서 선정된 후보만 monitoring log에 저장된다. |

### 저장소 hygiene

커밋 대상에서 제외할 파일:

```text
.note/finance/run_history/*.jsonl
WEB_APP_RUN_HISTORY
temp CSV
.playwright-mcp
```

## 권장하지 않는 접근

### 5개 label을 바로 3개 label로 치환

이 방식은 위험하다.

이유:

- 기존 handoff가 `backtest_requested_panel`에 legacy label을 직접 넣는다.
- History replay가 `Single Strategy` route를 기대한다.
- Saved Mix handoff가 `Portfolio Proposal` route를 기대한다.
- `render_backtest_tab()`의 fallback이 잘못된 화면을 렌더링할 수 있다.

먼저 stage와 internal route를 분리해야 한다.

### Candidate Review 코드를 바로 삭제

이 방식도 위험하다.

이유:

- Current Candidate Registry와 Pre-Live Registry를 읽는 Candidate Library, Overview, Proposal, Final Review helper가 남아 있다.
- 기존 JSONL row와 replay helper는 계속 호환되어야 한다.
- Candidate Review helper의 readiness / conversion logic은 Practical Validation source builder에서 재사용할 수 있다.

Candidate Review UI는 main workflow에서 내리고, helper와 legacy inspector만 남기는 순서가 안전하다.

Clean V2 Mode에서도 기존 JSONL 파일은 archive할 수 있다. 여기서 위험하다는 뜻은 `backtest_candidate_review_helpers.py` 같은 코드 자산을 분석 없이 삭제하는 것이다.

### Practical Validation에서 다시 weight builder를 크게 제공

이 방식은 사용자의 혼란을 유지한다.

비중 실험과 조합 저장은 `Backtest Analysis`에서 끝내고, Practical Validation은 이미 선택된 source를 실전 검증하는 화면으로 제한하는 편이 목적이 분명하다.

## Clean V2에서도 남길 compatibility

Clean V2 Mode는 기존 JSONL을 main source-of-truth에서 내리는 것이지, 과거 기록을 무시하거나 코드 자산을 한 번에 삭제하는 뜻이 아니다.

| compatibility | Clean V2에서의 위치 | 이유 |
|---|---|---|
| old registry JSONL | archive / legacy inspector | 과거 분석 기록으로 보관한다. 새 validation의 필수 조건으로 쓰지 않는다. |
| candidate review helper 일부 | Practical Validation source builder 내부 재사용 | result snapshot, data trust, settings snapshot 변환 로직은 재사용 가치가 있다. |
| legacy route label | transition mapping | 기존 session handoff와 history replay 안정성 때문에 route mapping은 한동안 유지한다. |
| old final decision schema | legacy selected dashboard reader | 기존 선정 기록을 볼 수는 있게 하되, 새 선정은 V2 decision file에 저장한다. |
| saved portfolio setup | one-time import 또는 legacy saved setup viewer | 사용자가 만든 과거 mix setup을 필요할 때 새 `SAVED_PORTFOLIO_MIXES.jsonl`로 복사할 수 있게 한다. |

## 열려 있는 설계 판단

구현 전에 사용자가 확인해야 하는 선택지는 아래다.

| 판단 | 권장안 |
|---|---|
| 저장소 모드 | 대규모 개편이면 `Clean V2 Mode`를 권장한다. 기존 JSONL은 archive하고 새 workflow 저장소를 main source로 둔다. |
| 기존 Candidate Review / Portfolio Proposal 화면을 완전히 숨길지 | 첫 구현에서는 main workflow에서 내리고 Practical Validation의 legacy / advanced section으로 접는다. |
| Practical Validation 중간 결과를 JSONL로 저장할지 | Clean V2에서는 저장한다. 단, 사용자 메모 저장이 아니라 구조화된 validation evidence 저장이다. 최종 사용자 메모는 Final Review에만 둔다. |
| Saved Mix final source의 replay를 어디까지 보장할지 | 최소 snapshot display는 보장하고, 가능한 경우 saved mix replay contract로 recheck fallback을 구현한다. |
| 기존 Portfolio Proposal multi-candidate builder를 어디에 둘지 | 새 주 흐름에서는 Backtest Analysis에서 비중 조합을 만들게 하고, 기존 builder는 compatibility / advanced path로 둔다. |
| monitoring log를 저장할지 | 기본 dashboard 조회는 read-only다. 사용자가 명시적으로 저장할 때만 monitoring snapshot을 append한다. |

## 결론

이번 redesign은 단순 label 변경이 아니다.

핵심은 다음 세 가지다.

1. 상단 visible stage와 내부 workspace route를 분리한다.
2. 기존 JSONL을 archive하고 Clean V2 저장소를 새 source-of-truth로 둔다.
3. Candidate Review / Portfolio Proposal의 저장 중심 workflow를 Practical Validation 중심 workflow로 재배치한다.
4. Saved Mix와 Compare 후보가 Current Candidate / Pre-Live registry 없이도 Final Review까지 이어질 수 있는 source contract를 만든다.

이 순서로 진행하면 기존 registry를 계속 끌고 가는 복잡성을 줄이면서도 사용자는 다음처럼 이해할 수 있다.

```text
Backtest Analysis에서 만들고 검증한다
Practical Validation에서 실전 투입 전 조건을 본다
Final Review에서 최종 판단과 메모를 남긴다
Selected Portfolio Dashboard에서 선정 이후 상태를 다시 확인한다
```
