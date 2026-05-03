# Web Backtest UI Flow

## 목적

이 문서는 Streamlit Backtest 화면의 single strategy, compare, candidate review, Pre-Live 운영 기록, portfolio proposal, Operations-owned backtest history, Candidate Library, saved weighted portfolio 흐름을 설명한다.
UI form, payload 복원, candidate review, history replay, candidate replay, saved weighted portfolio replay를 수정할 때 먼저 확인한다.

## 핵심 파일

| 파일 | 역할 |
|---|---|
| `app/web/streamlit_app.py` | top navigation과 page entry |
| `app/web/overview_dashboard.py` | `Workspace > Overview`에서 Backtest registry 기반 후보 Top 3, candidate funnel, next actions, recent activity dashboard render |
| `app/web/overview_dashboard_helpers.py` | Overview dashboard용 current candidate / Pre-Live / proposal / history / saved portfolio 집계와 candidate priority scoring helper |
| `app/web/backtest_common.py` | Backtest 공용 preset, session state, panel routing, universe / real-money / guardrail input, status label helper |
| `app/web/backtest_single_strategy.py` | `Single Strategy` 화면 orchestration. strategy 선택, prefill notice, form dispatch, latest result 연결 |
| `app/web/backtest_single_forms.py` | Single Strategy strategy-specific form render. Equal Weight, GTAA, GRS, Risk Parity, Dual Momentum, Quality / Value 계열 |
| `app/web/backtest_single_runner.py` | Single Strategy payload 실행 dispatch, DB-backed runtime 호출, latest bundle state 저장, run history append |
| `app/web/backtest_compare.py` | `Compare & Portfolio Builder` 화면 render, compare 실행, weighted portfolio builder, saved portfolio replay / load, candidate handoff |
| `app/web/backtest_result_display.py` | Backtest 결과 공용 display. summary, chart, data trust, real-money detail, selection history, compare result helper |
| `app/web/backtest_history.py` | `Operations > Backtest Run History` 화면 render, selected record inspect, run again / load into form / candidate draft handoff |
| `app/web/backtest_history_helpers.py` | History table row, replay payload, replay parity, Real-Money / Guardrail scope helper |
| `app/web/backtest_candidate_library.py` | `Operations > Candidate Library` 화면 render. 저장된 current / Pre-Live 후보 inspect와 저장 contract 기반 result curve rebuild |
| `app/web/backtest_candidate_library_helpers.py` | Candidate Library registry join, table row, replay payload 생성, ETF / strict annual equity 후보 replay runtime dispatch helper |
| `app/web/pages/backtest.py` | Backtest page entry, workflow navigation, panel dispatch shell. 주요 panel 본문은 `app/web/backtest_*.py` module이 담당 |
| `app/web/backtest_ui_components.py` | Backtest UI 공용 status card, artifact pipeline, compact badge strip, stage brief strip, route/readiness panel render helper |
| `app/web/backtest_candidate_review.py` | Candidate Review / Candidate Packaging / Pre-Live 운영 기록 화면 render logic |
| `app/web/backtest_candidate_review_helpers.py` | Candidate Review 판단, Review Note / registry 변환, Pre-Live status 추천 / draft 변환 / Portfolio Proposal 진입 readiness score helper |
| `app/web/backtest_portfolio_proposal.py` | 단일 후보 Live Readiness 직행 평가, 다중 후보 Portfolio Proposal 후보 선택 / 목적 / 역할 / 비중 설계, Phase 31 Portfolio Risk / Validation Pack, 저장된 proposal feedback section render logic |
| `app/web/backtest_portfolio_proposal_helpers.py` | Portfolio Proposal row 생성, 단일 후보 direct readiness / proposal save readiness 평가, Phase 31 validation input / result / overlap first pass, monitoring / Pre-Live / paper feedback table helper |
| `app/web/runtime/backtest.py` | UI payload를 실행 가능한 runtime call로 변환 |
| `app/web/runtime/candidate_registry.py` | current candidate / review note / pre-live registry JSONL read / append helper |
| `app/web/runtime/portfolio_proposal.py` | portfolio proposal draft JSONL read / append helper |
| `.note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl` | local run history. 보통 commit하지 않음 |
| `.note/finance/saved/SAVED_PORTFOLIOS.jsonl` | saved portfolio persistence |
| `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | proposal draft persistence. 첫 proposal 저장 시 생성 |

## 화면 흐름

Backtest page는 후보 검토 주 흐름만 보여준다.

Backtest 주 흐름:

- `Single Strategy`: 하나의 전략을 실행하고 latest result를 확인한다.
- `Compare & Portfolio Builder`: 여러 전략을 같은 기간으로 비교하고 weighted portfolio를 만든다.
- `Candidate Review`: Candidate Packaging 단일 흐름에서 Draft 확인, Review Note 저장, registry 저장, Pre-Live 운영 기록 저장, Portfolio Proposal 이동 판단을 순서대로 처리한다.
- `Portfolio Proposal`: Candidate Review를 통과한 단일 후보는 추가 proposal 저장 없이 Live Readiness 직행 가능 여부를 확인한다. 여러 후보를 묶을 때만 목적 / 역할 / 비중이 있는 포트폴리오 초안을 저장하고, 같은 다중 후보 작성 흐름 안에서 저장된 proposal monitoring / pre-live feedback / paper tracking feedback을 확인한다.

Operations 보조 화면:

- `Operations > Backtest Run History`: 저장된 실행 기록을 inspect하고, 가능한 경우 run again, load into form, candidate draft handoff를 수행한다. 후보 검토 흐름의 주 단계가 아니라 과거 실행을 다시 열기 위한 운영 / 재현 도구로 둔다.
- `Operations > Candidate Library`: `CURRENT_CANDIDATE_REGISTRY.jsonl`과 `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을 읽어 저장된 후보를 다시 열어 본다. registry에는 compact snapshot만 남으므로, 그래프 / result table이 필요할 때 저장 contract로 DB-backed result curve를 재생성한다. 후보 등록 단계가 아니라 보관함 / 재검토 도구다.

## 현재 Reference Guide 제품 흐름

`Reference > Guides`의 사용자-facing 흐름은 아래 순서로 읽는다.

```text
Ingestion / Data Trust
  -> Single Strategy Backtest
  -> Real-Money Signal
  -> Hold / Blocker Resolution
  -> Compare
  -> Candidate Packaging
     -> Draft 확인 / Review Note 저장 / Registry 저장 / Pre-Live 운영 기록 / Portfolio Proposal 이동 판단
  -> Compare 재검토 또는 Portfolio Proposal
  -> Portfolio Proposal
     -> 후보 선택 / 목적 / 역할 / 비중 설계 / Live Readiness 진입 평가 / Proposal 저장
     -> Portfolio Risk / Live Readiness Validation Pack
  -> Live Readiness / Final Approval
```

구분:

- `Candidate Packaging`은 Draft 확인, Review Note 저장, Registry 저장, Pre-Live 운영 기록, Portfolio Proposal 이동 판단을 하나로 묶은 사용자-facing 6단계다.
- `Candidate Draft`는 latest run 또는 `Operations > Backtest Run History`에서 보낸 history run을 후보처럼 읽는 저장 전 초안이며, Candidate Packaging 안에서 쓰인다.
- `Registry 저장`은 저장된 판단 기록을 Current Candidate / Near Miss / Scenario / Stop 중 어디까지 남길지 정하고, 통과한 row만 Current Candidate Registry에 append하는 Candidate Packaging 내부 작업이다.
- `Pre-Live 운영 기록`은 저장된 후보를 실제 돈 없이 paper / watchlist / hold / re-review 중 어떻게 관찰할지 기록하는 Candidate Packaging 내부 작업이다.
- `Portfolio Proposal 이동 판단`은 Pre-Live 운영 record를 저장하기 전에 저장 가능 여부와 저장 후 Proposal 이동 가능 여부를 같이 보여주는 Candidate Packaging의 최종 route 확인이다.
- `Portfolio Proposal`은 후보 묶음 제안이며, live trading approval이 아니다. 단일 후보는 기본 100% proposal로 빠르게 지나갈 수 있고, 여러 후보를 묶을 때는 역할 / 비중을 명시한다.
- `Portfolio Risk / Live Readiness Validation Pack`은 Phase 31에서 추가된 읽기 전용 검증 surface다. 단일 후보, 작성 중 proposal, 저장된 proposal을 route / score / blocker / component risk / Phase 32 handoff로 읽는다.
- `Live Readiness / Final Approval`은 Phase 30 이후 별도 phase 후보로 남긴다.

현재 Guides 화면은 네 묶음으로 정리한다.

| 묶음 | 내용 |
|---|---|
| `핵심 개념 가이드` | 실전 승격 흐름, Real-Money Contract, GTAA Risk-Off 후보군, interval, Compare 대상 선정법 해석 |
| `1~7 단계 실행 흐름` | 테스트에서 상용화 후보 검토까지의 단계별 흐름. 각 단계는 expander로 접어 읽는다 |
| `단계 통과 기준` | 4->5, 5->6, 6->7처럼 다음 단계로 넘길지 판단하는 stop/go 기준과 Candidate Packaging 기준. 각 기준은 expander로 접어 읽는다 |
| `문서와 파일` | 현재 먼저 볼 문서, 주요 registry / guide / log 파일, live approval이 아님을 구분하는 운영 경계 |

## Phase 30 Portfolio Proposal 계약

Phase 30 두 번째 작업 이후 Portfolio Proposal은 단순 weighted portfolio 저장값이 아니라,
후보 묶음의 목적과 검토 근거를 함께 담는 제안 초안으로 본다.

상세 계약은 아래 문서를 기준으로 한다.

- `.note/finance/phases/phase30/PHASE30_PORTFOLIO_PROPOSAL_CONTRACT_SECOND_WORK_UNIT.md`

Phase 30 네 번째 작업 이후 기본 저장 위치는
`.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`이다.
첫 proposal draft를 저장할 때 파일이 생성되며,
append / load helper는 `app/web/runtime/portfolio_proposal.py`가 담당한다.

Proposal UI가 최소 표시해야 하는 묶음:

- proposal objective
- component candidates and proposal roles
- target weights and weight reasons
- construction method and date alignment
- risk constraints
- evidence snapshot
- open blockers
- operator decision

Portfolio Proposal은 `SAVED_PORTFOLIOS.jsonl`의 replay 계약을 대체하지 않는다.
Saved Portfolio는 재현 가능한 weight setup이고,
Portfolio Proposal은 그 setup이나 candidate set을 왜 제안 후보로 보는지 설명하는 검토 단위다.

## `backtest.py` 리팩토링 경계

2026-04-30 리팩토링 이후 `app/web/pages/backtest.py`는 약 100 lines의 page shell이다.
Backtest workflow의 실제 body는 `app/web/backtest_*.py` module로 분리한다.

| 우선순위 | 분리 후보 | 대표 책임 | 이유 |
|---|---|---|---|
| 1 | Candidate Review module | Candidate Packaging flow, review note save, registry draft UI, Pre-Live 운영 기록, Portfolio Proposal 이동 판단 | 완료: render flow는 `app/web/backtest_candidate_review.py`, 판단 / 변환 / Pre-Live helper는 `app/web/backtest_candidate_review_helpers.py`로 분리. Streamlit auto page discovery를 피하려고 `pages/` 밖에 둔다 |
| 2 | Pre-Live Review tab/module | 별도 Pre-Live tab | 제거: Pre-Live 운영 기록은 Candidate Review 3번 구간으로 통합했고, 별도 `backtest_pre_live_review*.py` 파일은 삭제했다 |
| 3 | Registry runtime helpers | current candidate / review note / pre-live / proposal registry I/O, compare prefill conversion | Candidate Review / Compare / Pre-Live / Proposal이 공통 persistence pattern을 쓴다 |
| 4 | History module | run history display, selected record, run again, load into form | 완료: render flow는 `app/web/backtest_history.py`, replay / parity helper는 `app/web/backtest_history_helpers.py`로 분리. `Operations > Backtest Run History`에서 사용한다 |
| 5 | Portfolio Proposal module | proposal 후보 선택, 목적 / 역할 / 비중 설계, Live Readiness 진입 평가, saved proposal feedback | 완료: render flow는 `app/web/backtest_portfolio_proposal.py`, proposal row / readiness / feedback helper는 `app/web/backtest_portfolio_proposal_helpers.py`로 분리 |
| 6 | Single Strategy module split | strategy-specific forms, runtime dispatch, latest result 연결 | 완료: `backtest_single_strategy.py`, `backtest_single_forms.py`, `backtest_single_runner.py`로 분리 |
| 7 | Compare / Portfolio Builder module split | compare form / 실행 / weighted portfolio / saved portfolio replay | 완료: `backtest_compare.py`로 분리. 향후 더 세분화할 경우 weighted / saved portfolio를 별도 module로 뺄 수 있다 |
| 8 | Result display helpers | latest result, charts, data trust, real-money details | 완료: 공용 display는 `backtest_result_display.py`로 분리 |
| 9 | Backtest common helper | preset, session state, 입력 컴포넌트, status label | 완료: `backtest_common.py`가 transitional shared module로 관리한다. 향후 규모가 다시 커지면 `backtest_state.py`, `backtest_strategy_inputs.py`, `backtest_presets.py`로 추가 분리한다 |

분리 원칙:

- 먼저 함수 이동만 하고 behavior를 바꾸지 않는다.
- module split 후에는 `python3 -m py_compile app/web/pages/backtest.py app/web/backtest_*.py app/web/streamlit_app.py`를 기본 확인한다.
- Streamlit session state key는 이름을 바꾸지 않는 것을 기본으로 한다.
- registry file path와 append-only semantics는 helper 이동 후에도 유지한다.
- 한 번에 여러 workflow를 옮기지 않는다.

Phase 30 third work unit status:

- `app/web/runtime/candidate_registry.py`로 registry JSONL read / append helper를 먼저 분리했다.
- 분리된 대상은 current candidate registry, candidate review notes, pre-live candidate registry의 file path constant와 I/O helper다.
- `app/web/runtime/portfolio_proposal.py`로 proposal draft registry read / append helper도 추가했다.
- Candidate Review는 `app/web/backtest_candidate_review.py`와 `app/web/backtest_candidate_review_helpers.py`로 분리되어, `backtest.py`에는 panel wrapper와 cross-panel handoff call만 남아 있다.
- 긴 route/status 문자열은 `app/web/backtest_ui_components.py`의 wrapping card / route panel을 사용해 `st.metric` 말줄임을 피한다.
- Backtest shell은 중복 제목을 제거하고, `Single Strategy -> Compare & Portfolio Builder -> Candidate Review -> Portfolio Proposal`을 주 workflow navigation으로 보여준다. `History`는 메인 흐름에서 제외하고 `Operations > Backtest Run History` page로 연다.
- Backtest Run History는 `app/web/backtest_history.py`와 `app/web/backtest_history_helpers.py`로 분리되어, `backtest.py`에는 History 화면 render / replay helper 본문이 남아 있지 않다.
- Portfolio Proposal은 `app/web/backtest_portfolio_proposal.py`와 `app/web/backtest_portfolio_proposal_helpers.py`로 분리되어, `backtest.py`에는 panel wrapper만 남아 있다.
- Single Strategy는 `app/web/backtest_single_strategy.py`, `app/web/backtest_single_forms.py`, `app/web/backtest_single_runner.py`로 분리되어, form render와 runtime dispatch를 page shell에서 제거했다.
- Compare / Portfolio Builder는 `app/web/backtest_compare.py`로 분리되어, compare 실행, weighted portfolio builder, saved portfolio replay / load, current-candidate compare prefill을 page shell에서 제거했다.
- Latest result / compare result / Real-Money detail / selection history display는 `app/web/backtest_result_display.py`가 담당한다.
- 공용 preset, session state, 입력 컴포넌트, status label은 `app/web/backtest_common.py`가 담당한다. 이 파일은 다음 리팩토링에서 더 잘게 나눌 수 있는 transitional shared module이다.
- 따라서 `app/web/pages/backtest.py`는 Backtest page shell과 workflow navigation만 유지한다.

## Single Strategy 흐름

```text
strategy 선택
  -> strategy-specific form 입력
  -> _handle_backtest_run(...)
  -> app/web/runtime/backtest.py run_*_backtest_from_db(...)
  -> latest result bundle 저장
  -> result table / summary / selection history / real-money surface 표시
  -> history record 저장
```

주의:

- `Load Into Form`은 입력값만 복원한다.
- 복원 후 결과를 갱신하려면 사용자가 다시 실행해야 한다.
- selection history가 있는 전략은 latest result의 `Selection History Table` / `Interpretation Summary`에서 상세를 본다.

## Real-Money Compare 진입 평가 흐름

`Real-Money > 현재 판단`에는 `5단계 Compare 진입 평가` 박스를 둔다.

목적:

- `Promotion`, `Deployment`, blocker 정보를 10점 척도로 요약한다.
- 사용자가 4단계 Hold 해결을 마치고 5단계 Compare로 넘어갈 수 있는지 먼저 판단하게 한다.
- 이 평가는 live trading approval이나 주문 지시가 아니라 Compare 진입 보조 신호다.

기준:

- `Promotion Decision != hold`
- `Deployment Readiness / Deployment Status != blocked`
- 핵심 blocker 없음

점수 해석:

- `8.0 / 10` 이상이면 깔끔하게 5단계 Compare로 진행 가능한 상태다.
- `8.0 / 10` 미만이어도 위 핵심 기준을 만족하면 Compare로는 넘길 수 있지만, 개선 항목을 같이 확인한다.
- 위 핵심 기준을 만족하지 못하면 점수와 무관하게 4단계에서 blocker를 먼저 해결한다.

표시:

- `Readiness Score`: 10점 만점의 Compare 진입 점수
- `판정`: `5단계 Compare 진행 가능`, `5단계 Compare 진행 가능, 개선 항목 동시 확인`, `4단계에서 먼저 blocker 해결`
- `다음 행동`: Compare로 넘길지, blocker를 먼저 해결할지 설명
- `점수 계산 기준 보기`: Promotion / Deployment / Core Blocker별 점수 근거

## Compare 흐름

```text
strategy multi-select
  -> Compare Period & Shared Inputs
  -> strategy별 box에서 variant / advanced inputs 설정
  -> Run Strategy Comparison
  -> strategy별 result bundle 실행
  -> 6단계 Candidate Packaging 진입 평가
  -> comparison table / overlay / focused strategy 표시
  -> Weighted Portfolio Builder로 전달
```

현재 UX 기준:

- common date / timeframe / option은 공유 입력으로 둔다.
- strategy-specific advanced inputs는 strategy별 box 안에서 보이게 한다.
- variant 변경은 버튼 없이 즉시 아래 옵션이 바뀌는 방향이 선호된다.
- 최대 compare 전략 수는 operator가 읽을 수 있는 범위로 유지한다.

Compare 결과 상단에는 `6단계 Candidate Packaging 진입 평가` 박스를 둔다.

목적:

- Compare 결과 중 어떤 전략을 6단계 `Candidate Packaging`으로 넘길지 명시적으로 선택하게 한다.
- Compare 실행 정상 여부, 선택 후보의 Data Trust, Real-Money gate, 상대 비교 근거를 10점으로 요약한다.
- Data Trust는 Draft Score를 강제로 `6.4` 같은 값으로 누르는 cap이 아니라, 별도 `OK / WARNING / BLOCKED` gate로 같이 표시한다.
- 이 평가는 current candidate registry 저장, Pre-Live 승인, live trading approval이 아니라 후보 검토 초안으로 넘길 수 있는지 보는 신호다.

기준:

- `Compare Run`: 2개 이상 전략이 정상 비교됐는지
- `Data Trust`: 선택 후보의 결과 기간, 가격 최신성, excluded / malformed ticker가 해석 가능한지
- `Real-Money Gate`: `Promotion != hold`, `Deployment != blocked`, 핵심 blocker 없음인지
- `Relative Evidence`: CAGR, End Balance, Maximum Drawdown, Sharpe 중 설명 가능한 상대 근거가 있는지

점수 해석:

- `8.0 / 10` 이상이면 6단계 Candidate Packaging으로 깔끔하게 진행 가능하다.
- `6.5 / 10` 이상이면 조건부 진행 가능하되 Review Note에 약점과 확인 항목을 남긴다.
- 짧은 실제 종료일 불일치, warning, excluded / malformed ticker 같은 Data Trust 이슈는 score를 cap하지 않고 warning으로 표시한다.
- 가격 최신성 error 또는 결과 기간이 크게 비는 Data Trust blocked 상태, Real-Money blocker, 비교 실패, 상대 근거 없음은 5단계 Compare에서 먼저 재확인한다.

실행:

- 통과 또는 조건부 통과 상태에서는 `Send Selected Strategy To Candidate Packaging` 버튼으로 `Candidate Review > 1. Draft 확인`으로 보낼 수 있다.
- 보내진 draft는 아직 registry 저장이 아니며, Candidate Packaging 안에서 operator decision과 next action을 남겨야 한다.

## Strategy Capability Snapshot 흐름

Phase 28 이후 `Single Strategy`와 `Compare & Portfolio Builder`의 strategy box에는
`Strategy Capability Snapshot` 접힘 영역을 둔다.

목적:

- annual strict, quarterly strict, price-only ETF 전략이 서로 다른 이유를 UI에서 먼저 설명한다.
- cadence, data trust, selection history, Real-Money/Guardrail, history/replay 지원 범위를 표로 보여준다.
- 기능이 없는 것처럼 보이는 부분이 버그인지, 아직 annual 중심으로 남긴 의도적 차이인지 구분하게 한다.

현재 기준:

- strict annual은 가장 성숙한 Real-Money / Guardrail surface로 설명한다.
- strict quarterly prototype은 Data Trust와 Portfolio Handling은 지원하지만, Real-Money promotion / Guardrail 판단은 아직 annual strict 중심으로 설명한다.
- Global Relative Strength는 재무제표 selection history 대상이 아니라 price-only ETF relative strength strategy로 설명한다.

## Data Trust Summary 흐름

Phase 27 이후 `Latest Backtest Run` 상단에는 `Data Trust Summary`를 둔다.

목적:

- 요청 종료일과 실제 결과 종료일을 먼저 비교한다.
- price freshness, common latest price, latest-date spread를 결과 해석 전에 보여준다.
- excluded ticker와 malformed price row가 있으면 `Data Quality Details`에서 확인하게 한다.

첫 적용 대상:

- `Global Relative Strength` single strategy 실행 전 `Price Freshness Preflight`
- `Latest Backtest Run`의 공통 `Data Trust Summary`

## Candidate Library 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  + PRE_LIVE_CANDIDATE_REGISTRY.jsonl
  -> Operations > Candidate Library
  -> 후보 선택
  -> Stored Snapshot / Replay Contract / Pre-Live Record 확인
  -> Rebuild Result Curve
  -> Single Strategy와 같은 Summary / Equity Curve / Extremes / Result Table 확인
```

Candidate Library는 workflow 단계가 아니다.
Candidate Review에서 저장한 후보를 나중에 다시 열어보고,
registry snapshot과 실제 재실행 결과가 같은 설정으로 복원되는지 확인하는 보조 화면이다.

현재 replay 지원 범위는 price-only ETF 후보 family와 strict annual equity 후보 family다.

- Equal Weight
- GTAA
- Global Relative Strength
- Risk Parity Trend
- Dual Momentum
- Quality Snapshot (Strict Annual)
- Value Snapshot (Strict Annual)
- Quality + Value Snapshot (Strict Annual)

## Weighted Portfolio / Saved Weighted Portfolio 흐름

```text
compare result bundles
  -> weight 입력
  -> make_monthly_weighted_portfolio(...)
  -> weighted result
  -> optional save
  -> Load Saved Setup Into Compare or Replay Saved Portfolio
```

구분:

- `Load Saved Setup Into Compare`: 저장된 compare 구성과 weight를 form에 다시 채운다.
- `Replay Saved Portfolio`: 저장 당시 context로 compare와 weighted portfolio를 다시 실행한다.

저장된 weighted portfolio는 live trading 승인 기록이 아니다.
후보 조합을 다시 재현하고 검증하기 위한 operator workflow artifact다.
저장된 후보 자체의 그래프 재검토는 `Operations > Candidate Library`에서 처리한다.

## Candidate Review 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Candidate Review
  -> 3. 운영 기록 저장 및 Portfolio Proposal 이동에서 선택 후보 확인
  -> Save Pre-Live Record 또는 Open Compare Picker
  -> 저장된 Pre-Live record가 PORTFOLIO_PROPOSAL_READY이면 Open Portfolio Proposal
```

Latest / Operations history result handoff:

```text
Latest Backtest Run 또는 Operations > Backtest Run History selected record
  -> Review As Candidate Draft
  -> Backtest > Candidate Review > 1. Draft 확인 / Review Note 저장
  -> result snapshot / Real-Money signal / data trust snapshot 확인
  -> Candidate Packaging 저장 준비 확인
  -> Save Candidate Review Note
  -> CANDIDATE_REVIEW_NOTES.jsonl
  -> 2. Registry 저장에서 registry 후보 범위 판단
  -> Prepare Current Candidate Registry Row
  -> explicit Append To Current Candidate Registry
  -> 3. 운영 기록 저장 및 Portfolio Proposal 이동에서 선택 후보 확인
  -> PRE_LIVE_READY면 같은 화면에서 운영 기록 저장 및 다음 단계 판단
  -> Save Pre-Live Record
  -> PRE_LIVE_CANDIDATE_REGISTRY.jsonl append
  -> 저장된 record가 PORTFOLIO_PROPOSAL_READY이면 Portfolio Proposal로 이동
```

구분:

- Candidate Review는 후보를 투자 추천으로 확정하는 화면이 아니다.
- Candidate Review는 Candidate Packaging 작업 공간이며 한 화면 안에서 Draft 확인, Registry 저장, Pre-Live 운영 기록, Portfolio Proposal 이동 판단을 순서대로 처리한다.
- 상단의 `Candidate Packaging 산출물 흐름`은 Draft, Review Note, Current Candidate, Pre-Live Record, Proposal Ready를 카드로 보여준다.
- 각 큰 단계는 긴 설명문이나 card grid 대신 얇은 `왜 / 결과` brief strip으로 목적과 산출물을 먼저 보여준다.
- `Send To Compare`는 후보 row의 `compare_prefill`을 우선 사용하고,
  기존 strict annual seed 후보는 registry id 기반 기본값을 사용한다.
- GTAA seed 후보처럼 `compare_prefill`은 없지만 전략 `contract`가 남아 있는 경우에는
  해당 `contract`를 compare override로 변환해 form에 채운다.
- 후보 row에 `compare_prefill`도 없고 변환 가능한 `contract`도 없으면,
  사용자가 해결할 수 있는 설정 문제가 아니라 해당 후보 row의 compare 재진입 정보가 부족한 상태다.
- `1. Draft 확인`은 registry에 저장된 후보가 아니라 Candidate Packaging의 검토 초안을 다룬다.
- Candidate Review Note는 초안을 보고 남기는 operator decision 기록이며,
  현재 UI에서는 Draft 수신 정보와 operator reason / next action이 준비되어야 저장 버튼이 활성화된다.
- Candidate Review Note를 저장해도 current candidate registry에 자동 등록되지 않는다.
- `2. Registry 저장`은 `저장 범위 판단`으로 Current Candidate / Near Miss / Scenario / Stop 범위를 먼저 보여준다.
- `저장 범위 판단`은 route/readiness panel을 사용해 Scope, Scope Score, Blockers, 판정, 다음 행동을 표시한다.
- Registry scope의 추천 type, 허용 type, Review Decision은 compact badge strip으로 보여주고, 판단 기준 표와 기존 저장 기록은 기본 접힘 영역에 둔다.
- Registry row 저장값은 기본적으로 `Registry ID`, `Record Type`, `Candidate Title`, `Registry Notes`, 다음 단계에서 찾을 label만 펼쳐 보여주고, strategy family / name / role 같은 고급 식별값은 접힘 영역에 둔다.
- 범위 판단과 맞지 않는 record type은 append를 막는다.
- Review Note를 registry row로 남기려면 `2. Registry 저장`에서 row preview를 확인한 뒤
  같은 Candidate Packaging 안에서 `Append To Current Candidate Registry`를 명시적으로 눌러야 한다.
- 같은 Review Note가 이미 append된 경우에는 중복 append를 기본 차단하고, 의도적 revision 저장 체크박스를 켠 경우에만 다시 저장한다.
- append 성공 직후에는 새 registry row의 `registry_id` / `revision_id`를 session state에 남기고, `3. 운영 기록 저장 및 Portfolio Proposal 이동`에서 해당 후보를 자동 선택한다.
- Candidate selection label은 `Strategy Family | Role | Title | id=<registry_id>` 형식이다. 같은 family와 title이 반복되어도 `registry_id`로 방금 저장한 row를 찾을 수 있게 한다.
- `3. 운영 기록 저장 및 Portfolio Proposal 이동`은 먼저 선택 후보가 운영 기록으로 갈 current candidate인지, Compare로 돌아갈 후보인지 확인한다.
- `PRE_LIVE_READY`는 같은 화면에서 Pre-Live 운영 record를 저장할 수 있다는 뜻이고, `COMPARE_REVIEW_READY`는 실패가 아니라 Compare 재검토 경로다.
- `운영 기록 저장 및 다음 단계 판단`은 Operator Final Status, Operator Reason, Next Action, Review Date를 바탕으로 공통 route/readiness panel과 compact badges를 함께 보여준다. 이 판정 박스는 입력 영역보다 위에 렌더링해, 저장 가능 여부를 먼저 읽고 아래에서 운영 기록을 작성하는 흐름으로 보이게 한다.
- 공통 route/readiness panel은 긴 enum route를 underscore 기준으로 줄바꿈하고, 좁은 화면에서는 verdict 영역을 아래로 내려 가로 넘침 없이 읽히게 한다.
- Save / Open 버튼은 판단 기준과 JSON보다 먼저 보이게 하고, 상세 기준 / Pre-Live JSON / 선택 후보 raw detail은 하나의 `상세 보기` expander 안에 둔다.
- Pre-Live 운영 상태 영역은 Candidate Review 관점에서 필요한 promotion / shortlist / deployment / suggested status만 badge strip으로 보여주고, 추천 근거, 저장 후보 식별값, 판단 기준 표는 접힘 영역에 둔다.
- `Suggested Next Step`은 다음 검토 행동 제안이지 live trading 승인이나 최종 투자 판단이 아니다.
- `Save Pre-Live Record`는 live trading 승인이 아니라 `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`에 paper / watchlist / hold 같은 운영 상태를 남기는 append-only 기록이다.
- `Open Portfolio Proposal`은 같은 후보의 현재 선택 상태가 저장된 Pre-Live record와 맞고 route가 `PORTFOLIO_PROPOSAL_READY`일 때 활성화된다.

Phase 28 이후 Saved Portfolio 영역에는
`Saved Portfolio Replay / Load Parity Snapshot`을 둔다.
이 표는 저장 포트폴리오를 다시 열거나 재실행하기 전에 아래 값이 남아 있는지 보여준다.

- compare 공용 입력: start / end / timeframe / option
- selected strategy list
- weights percent / date alignment
- strategy override map
- strategy별 핵심 override: cadence, universe, factor, overlay, handling, benchmark, guardrail, score 설정

## Compare / Weighted Data Trust 흐름

Phase 28 이후 compare와 weighted portfolio 결과도 component별 data trust를 표시한다.

표시 위치:

- `Strategy Comparison > Data Trust`
- `Weighted Portfolio Result > Component Data Trust`
- `Operations > Backtest Run History > Selected History Run > Saved Input & Context`

보는 값:

- 요청 종료일과 실제 결과 종료일
- result row 수
- price freshness status
- common latest price / newest latest price / latest-date spread
- excluded ticker 수
- malformed ticker 수
- warnings 수
- 간단한 interpretation

의미:

- compare 결과가 서로 같은 데이터 조건에서 나온 것인지 먼저 확인한다.
- weighted portfolio는 composite 결과이므로, 구성 전략별 데이터 상태를 먼저 확인한다.
- 이 표는 성과 비교표가 아니라 데이터 조건 확인표다.

## Real-Money / Guardrail Scope 흐름

Phase 28 이후 compare, history, saved portfolio에는
전략별 Real-Money / Guardrail 지원 범위를 같은 언어로 보여주는 표를 둔다.

표시 위치:

- `Strategy Comparison > Real-Money / Guardrail`
- `Operations > Backtest Run History > Selected History Run > History Real-Money / Guardrail Scope`
- `Saved Portfolios > Saved Portfolio Real-Money / Guardrail Scope`

현재 기준:

- annual strict는 full strict equity Real-Money / Guardrail 기준 surface다.
- strict quarterly prototype은 cadence / replay / portfolio handling 검증 단계이며, annual strict 수준의 promotion surface로 보지 않는다.
- Global Relative Strength는 ETF operability + cost / benchmark first pass이며, dedicated ETF underperformance / drawdown guardrail은 아직 없다.
- GTAA, Risk Parity Trend, Dual Momentum은 ETF Real-Money + ETF guardrail first pass로 본다.
- Equal Weight는 실전 후보가 아니라 baseline이다.

의미:

- 모든 전략에 같은 실전 검증 UI를 강제로 붙였다는 뜻이 아니다.
- 전략별 성격에 맞는 검증 범위를 보여줘서 사용자가 annual / quarterly / ETF first-pass를 혼동하지 않게 한다.

## Backtest Run History 흐름

`Operations > Backtest Run History`는 compact summary 중심이다.
모든 selection history row를 그대로 저장하지 않는다.

대표 action:

- `Inspect`: 저장된 record를 읽는다.
- `Run Again`: 저장된 payload로 다시 실행한다.
- `Load Into Form`: 저장된 입력값을 single strategy form에 복원한다.

Phase 28 이후 Backtest Run History의 selected record 영역에는
`History Replay / Load Parity Snapshot`을 둔다.
이 표는 선택한 record에 재실행 / form 복원에 필요한 핵심 값이 남아 있는지 보여준다.

주요 확인 항목:

- strategy key, 입력 기간, timeframe, option
- universe / ticker / preset
- actual result start / end, result row count
- price freshness, excluded ticker, malformed price row
- strict family factor cadence, universe contract, overlay, portfolio handling
- annual strict real-money / guardrail / promotion settings
- GRS score, cash ticker, trend window, ETF operability inputs
- strategy별 Real-Money / Guardrail scope

## Candidate Review 안의 Pre-Live 운영 기록 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Candidate Review > 3. 운영 기록 저장 및 Portfolio Proposal 이동
  -> Packaging 확인 후보 선택
     -> 2. Registry 저장에서 방금 append한 후보 자동 선택
     -> 또는 current candidate 직접 선택
  -> 선택 후보 확인
  -> 운영 기록 저장 및 다음 단계 판단
     -> PORTFOLIO_PROPOSAL_READY / WATCHLIST_ONLY / PRE_LIVE_HOLD / REJECTED / SCHEDULED_REVIEW
  -> Save Pre-Live Record
  -> PRE_LIVE_CANDIDATE_REGISTRY.jsonl append
  -> 저장된 record와 현재 선택 상태가 맞으면 Portfolio Proposal로 이동
  -> 하단 보조 도구에서 active Pre-Live record 확인
```

구분:

- current candidate registry는 후보 자체를 정의한다.
- pre-live registry는 그 후보를 실전 전 어떻게 관찰하거나 보류할지 기록한다.
- Pre-Live 운영 기록은 별도 탭이 아니라 Candidate Review 3번 구간 안의 `선택 후보 확인 -> 운영 기록 저장 및 다음 단계 판단 -> 저장 및 이동` 순서형 화면으로 본다.
- Candidate Packaging에서 방금 저장한 후보는 자동 선택되지만, 사용자가 Candidate Review에서 다른 current candidate를 직접 고르는 것도 허용한다.
- `System Suggested Status`는 선택한 current candidate의 Real-Money 신호와 blocker에서 계산한 추천값이고, `Operator Final Status`가 실제 Pre-Live registry에 저장되는 운영 판단이다.
- 운영자가 추천값과 다른 status를 선택하면 UI는 경고를 보여주며, 의도적 override 근거를 `Operator Reason`에 남기도록 안내한다.
- `운영 기록 저장 및 다음 단계 판단`은 전략 성과 점수가 아니라 Pre-Live record가 다음 단계에서 읽을 수 있을 만큼 identity, result snapshot, Real-Money signal, status, reason, next action, review date, tracking plan을 갖췄는지 보는 route 확인이다.
- 이 route 확인은 `저장 범위 판단`과 같은 공통 판정 패턴을 사용하되, 독립된 큰 단계가 아니라 저장 버튼 위의 최종 확인으로 배치한다.
- `Save Pre-Live Record`는 live trading 승인 버튼이 아니다.
- `paper_tracking`도 실제 돈을 넣는다는 뜻이 아니라 paper 관찰 상태다.

## Portfolio Proposal 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Portfolio Proposal
  -> 1. Proposal 후보 확인
  -> 후보 1개 선택
     -> 단일 후보 직행 평가
     -> Live Readiness 직행 route/readiness panel 확인
     -> proposal draft 저장 없이 향후 Live Readiness 입력으로 사용
  -> 후보 2개 이상 선택
     -> 2. 목적 / 역할 / 비중 설계
     -> 3. Proposal 저장 및 다음 단계 판단
     -> Live Readiness 진입 평가 route/readiness panel 확인
     -> Portfolio Risk / Live Readiness Validation Pack 확인
     -> Portfolio Proposal JSON Preview 확인
     -> Save Portfolio Proposal Draft
     -> PORTFOLIO_PROPOSAL_REGISTRY.jsonl append
     -> 4. 저장된 Portfolio Proposal 확인에서 validation / monitoring / Pre-Live / paper feedback / raw JSON inspect
```

구분:

- Portfolio Proposal은 current candidate 하나를 다시 저장하는 단계가 아니다.
- 단일 후보는 `LIVE_READINESS_DIRECT_READY` / `LIVE_READINESS_DIRECT_REVIEW_REQUIRED` / `LIVE_READINESS_DIRECT_BLOCKED` route로 기존 current candidate와 Pre-Live record가 다음 단계 입력으로 충분한지 본다.
- 여러 후보는 `LIVE_READINESS_CANDIDATE_READY` / `PROPOSAL_DRAFT_READY` / `PROPOSAL_BLOCKED` route로 proposal draft 저장 가능성과 Live Readiness 후보성을 본다.
- `Proposal Components`는 비교 기능이 아니라 포트폴리오에 넣을 구성 후보 선택이다. 비교는 `Compare & Portfolio Builder`에서 수행한다.
- `2. 목적 / 역할 / 비중 설계`에서는 active weight가 있는 proposal에 최소 1개 `core_anchor`가 필요하다. `return_driver`, `diversifier`, `defensive_sleeve`, `satellite`은 중심 후보를 보완하는 역할이고, `watch_only`는 보통 0% 관찰 후보로 둔다.
- target weight 합계가 100%가 아니거나 core anchor가 없으면 `PROPOSAL_BLOCKED`가 정상적으로 뜬다. UI는 이때 criteria 이름만 보여주지 않고, 비중 합계 조정 / core anchor 지정 같은 수정 안내를 함께 보여준다.
- saved portfolio는 재현 가능한 weight setup이고, proposal은 그 후보 묶음의 목적과 검토 이유를 남긴다.
- `Save Portfolio Proposal Draft`는 live trading 승인 버튼이 아니다.
- proposal 저장은 current candidate registry나 pre-live registry를 자동 변경하지 않는다.
- 현재 proposal UI는 optimizer가 아니며, target weight는 manual / equal-weight 초안 기준이다.
- 단일 후보 직행 평가는 role `core_anchor`, weight `100%`, capital scope `paper_only`를 자동 전제로 둔다.
- `Save Portfolio Proposal Draft`는 여러 후보를 묶는 포트폴리오 초안 작성 흐름에서만 노출한다. 단일 후보 direct path에는 proposal 저장 목록을 붙이지 않는다.
- saved proposal의 validation / monitoring / Pre-Live feedback / paper tracking feedback은 다중 후보 작성 흐름의 `4. 저장된 Portfolio Proposal 확인` 안에서 읽는다.
- 현재 `Paper Tracking Feedback`은 실제 paper PnL 시계열 자동 계산이 아니라 Pre-Live record에 저장된 최신 snapshot 비교다.
- Phase 31 이후 `Validation Pack`은 단일 후보 direct path, 작성 중 proposal, 저장된 proposal에서 모두 같은 검증 언어를 사용한다.
- validation route는 `READY_FOR_ROBUSTNESS_REVIEW`, `PAPER_TRACKING_REQUIRED`, `NEEDS_PORTFOLIO_RISK_REVIEW`, `BLOCKED_FOR_LIVE_READINESS`로 구분한다.
- component table은 role, weight, family, benchmark, universe, factor set, Pre-Live, Data Trust, Promotion, Deployment를 같이 보여준다.
- 이 validation은 Phase 32 robustness 검증 handoff를 위한 surface이며, live approval이나 새 approval registry 저장이 아니다.

## Streamlit form 주의

Streamlit `st.form()` 내부 widget은 submit 전까지 app state가 즉시 rerun되지 않는다.
따라서 variant 선택처럼 아래 UI를 즉시 바꿔야 하는 값은 form 밖에 두는 것이 낫다.
반대로 한 번에 제출되어야 하는 detailed contract 입력은 form 내부에 유지할 수 있다.

## 갱신해야 하는 경우

- Backtest panel 구조가 바뀔 때
- strategy-specific form 위치나 payload key가 바뀔 때
- compare / weighted / saved portfolio 계약이 바뀔 때
- history record schema나 replay 가능 범위가 바뀔 때
- `Load Into Form`, `Run Again`, `Replay Saved Portfolio` semantics가 바뀔 때
