# Web Backtest UI Flow

## 목적

이 문서는 Streamlit Backtest 화면의 single strategy, compare, candidate review, history, saved portfolio 흐름을 설명한다.
UI form, payload 복원, candidate review, history replay, saved portfolio replay를 수정할 때 먼저 확인한다.

## 핵심 파일

| 파일 | 역할 |
|---|---|
| `app/web/streamlit_app.py` | top navigation과 page entry |
| `app/web/pages/backtest.py` | Backtest page 대부분의 UI / state / render logic |
| `app/web/runtime/backtest.py` | UI payload를 실행 가능한 runtime call로 변환 |
| `app/web/runtime/candidate_registry.py` | current candidate / review note / pre-live registry JSONL read / append helper |
| `app/web/runtime/portfolio_proposal.py` | portfolio proposal draft JSONL read / append helper |
| `.note/finance/BACKTEST_RUN_HISTORY.jsonl` | local run history. 보통 commit하지 않음 |
| `.note/finance/SAVED_PORTFOLIOS.jsonl` | saved portfolio persistence |
| `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | proposal draft persistence. 첫 proposal 저장 시 생성 |

## 화면 흐름

Backtest page는 현재 여섯 panel 중심으로 본다.

- `Single Strategy`: 하나의 전략을 실행하고 latest result를 확인한다.
- `Compare & Portfolio Builder`: 여러 전략을 같은 기간으로 비교하고 weighted portfolio를 만든다.
- `Candidate Review`: current candidate registry의 후보를 검토 보드로 읽고 compare 또는 Pre-Live Review로 넘긴다.
- `History`: 저장된 실행 기록을 inspect하고, 가능한 경우 run again 또는 load into form을 수행한다.
- `Pre-Live Review`: current candidate를 실전 전 운영 상태로 기록하고 저장된 Pre-Live record를 확인한다.
- `Portfolio Proposal`: current candidate 여러 개를 목적 / 역할 / 비중 근거와 함께 proposal draft로 저장하고 monitoring review / pre-live feedback / paper tracking feedback으로 다시 읽는다.

## 현재 Reference Guide 제품 흐름

`Reference > Guides`의 사용자-facing 흐름은 아래 순서로 읽는다.

```text
Ingestion / Data Trust
  -> Single Strategy Backtest
  -> Real-Money Signal
  -> Hold / Blocker Resolution
  -> Compare
  -> Candidate Draft
  -> Candidate Review Note
  -> Current Candidate Registry
  -> Candidate Board / Compare / Pre-Live Review
  -> Portfolio Proposal
  -> Live Readiness / Final Approval
```

구분:

- `Candidate Draft`는 latest run 또는 history run을 후보처럼 읽는 저장 전 초안이다.
- `Candidate Review Note`는 사람이 판단과 next action을 남기는 기록이다.
- `Current Candidate Registry`는 후보로 남기기로 한 row의 저장소다.
- `Pre-Live Review`는 실제 돈 없이 paper / watchlist / hold / re-review 상태를 기록하는 운영 단계다.
- `Portfolio Proposal`은 후보 묶음 제안이며, live trading approval이 아니다.
- `Live Readiness / Final Approval`은 Phase 30 이후 별도 phase 후보로 남긴다.

현재 Guides 화면은 네 묶음으로 정리한다.

| 묶음 | 내용 |
|---|---|
| `핵심 개념 가이드` | 실전 승격 흐름, Real-Money Contract, GTAA Risk-Off 후보군, interval, Compare 대상 선정법 해석 |
| `1~11 단계 실행 흐름` | 테스트에서 상용화 후보 검토까지의 단계별 흐름. 각 단계는 expander로 접어 읽는다 |
| `단계 통과 기준` | 4->5, 5->6처럼 다음 단계로 넘길지 판단하는 stop/go 기준. 각 기준은 expander로 접어 읽는다 |
| `문서와 파일` | 현재 먼저 볼 문서, 주요 registry / guide / log 파일, live approval이 아님을 구분하는 운영 경계 |

## Phase 30 Portfolio Proposal 계약

Phase 30 두 번째 작업 이후 Portfolio Proposal은 단순 weighted portfolio 저장값이 아니라,
후보 묶음의 목적과 검토 근거를 함께 담는 제안 초안으로 본다.

상세 계약은 아래 문서를 기준으로 한다.

- `.note/finance/phase30/PHASE30_PORTFOLIO_PROPOSAL_CONTRACT_SECOND_WORK_UNIT.md`

Phase 30 네 번째 작업 이후 기본 저장 위치는
`.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`이다.
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

현재 `app/web/pages/backtest.py`는 Backtest page 대부분을 담고 있으며,
2026-04-28 기준 16k lines 이상이다.
기능을 바로 크게 옮기기보다 아래 순서로 제품 경계가 분명한 부분부터 나눈다.

| 우선순위 | 분리 후보 | 대표 책임 | 이유 |
|---|---|---|---|
| 1 | Candidate Review module | Candidate Board, Intake Draft, Review Notes, registry draft UI | Phase 29 기능 묶음이 독립적이고 `CANDIDATE_REVIEW_NOTES.jsonl` 경계가 분명하다 |
| 2 | Pre-Live Review module | Pre-Live draft, status / tracking plan, registry inspect | `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` 경계가 분명하다 |
| 3 | Registry runtime helpers | current candidate / review note / pre-live / proposal registry I/O, compare prefill conversion | Candidate Review / Compare / Pre-Live / Proposal이 공통 persistence pattern을 쓴다 |
| 4 | History module | run history display, selected record, run again, load into form | `BACKTEST_RUN_HISTORY.jsonl` inspect / replay 책임이 크다 |
| 5 | Saved Portfolio / Weighted module | saved portfolio display, replay, weighted builder/result | Phase 30 portfolio proposal과 이어질 가능성이 높다 |
| 6 | Result display helpers | latest result, charts, data trust, real-money details | 공용 display helper가 많지만 workflow module 안정화 뒤가 안전하다 |
| 7 | Strategy forms | strategy-specific form rendering and state keys | 가장 크지만 state key와 form semantics가 많아 가장 나중에 신중히 분리한다 |

분리 원칙:

- 먼저 함수 이동만 하고 behavior를 바꾸지 않는다.
- module split 후에는 `python3 -m py_compile app/web/pages/backtest.py app/web/streamlit_app.py`를 기본 확인한다.
- Streamlit session state key는 이름을 바꾸지 않는 것을 기본으로 한다.
- registry file path와 append-only semantics는 helper 이동 후에도 유지한다.
- 한 번에 여러 workflow를 옮기지 않는다.

Phase 30 third work unit status:

- `app/web/runtime/candidate_registry.py`로 registry JSONL read / append helper를 먼저 분리했다.
- 분리된 대상은 current candidate registry, candidate review notes, pre-live candidate registry의 file path constant와 I/O helper다.
- `app/web/runtime/portfolio_proposal.py`로 proposal draft registry read / append helper도 추가했다.
- Candidate Review UI, Pre-Live UI, Compare prefill 변환, Streamlit session state는 아직 `app/web/pages/backtest.py`에 남아 있다.
- 따라서 이 작업은 전체 Backtest UI refactor가 아니라 첫 helper split이다.

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
  -> 6단계 Candidate Draft 진입 평가
  -> comparison table / overlay / focused strategy 표시
  -> Weighted Portfolio Builder로 전달
```

현재 UX 기준:

- common date / timeframe / option은 공유 입력으로 둔다.
- strategy-specific advanced inputs는 strategy별 box 안에서 보이게 한다.
- variant 변경은 버튼 없이 즉시 아래 옵션이 바뀌는 방향이 선호된다.
- 최대 compare 전략 수는 operator가 읽을 수 있는 범위로 유지한다.

Compare 결과 상단에는 `6단계 Candidate Draft 진입 평가` 박스를 둔다.

목적:

- Compare 결과 중 어떤 전략을 6단계 `Candidate Draft`로 넘길지 명시적으로 선택하게 한다.
- Compare 실행 정상 여부, 선택 후보의 Data Trust, Real-Money gate, 상대 비교 근거를 10점으로 요약한다.
- Data Trust는 Draft Score를 강제로 `6.4` 같은 값으로 누르는 cap이 아니라, 별도 `OK / WARNING / BLOCKED` gate로 같이 표시한다.
- 이 평가는 current candidate registry 저장, Pre-Live 승인, live trading approval이 아니라 후보 검토 초안으로 넘길 수 있는지 보는 신호다.

기준:

- `Compare Run`: 2개 이상 전략이 정상 비교됐는지
- `Data Trust`: 선택 후보의 결과 기간, 가격 최신성, excluded / malformed ticker가 해석 가능한지
- `Real-Money Gate`: `Promotion != hold`, `Deployment != blocked`, 핵심 blocker 없음인지
- `Relative Evidence`: CAGR, End Balance, Maximum Drawdown, Sharpe 중 설명 가능한 상대 근거가 있는지

점수 해석:

- `8.0 / 10` 이상이면 6단계 Candidate Draft로 깔끔하게 진행 가능하다.
- `6.5 / 10` 이상이면 조건부 진행 가능하되 Review Note에 약점과 확인 항목을 남긴다.
- 짧은 실제 종료일 불일치, warning, excluded / malformed ticker 같은 Data Trust 이슈는 score를 cap하지 않고 warning으로 표시한다.
- 가격 최신성 error 또는 결과 기간이 크게 비는 Data Trust blocked 상태, Real-Money blocker, 비교 실패, 상대 근거 없음은 5단계 Compare에서 먼저 재확인한다.

실행:

- 통과 또는 조건부 통과 상태에서는 `Send Selected Strategy To Candidate Draft` 버튼으로 `Candidate Review > Candidate Intake Draft`로 보낼 수 있다.
- 보내진 draft는 아직 registry 저장이 아니며, 6단계에서 operator decision과 next action을 남겨야 한다.

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

## Weighted Portfolio / Saved Portfolio 흐름

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

저장된 portfolio는 live trading 승인 기록이 아니다.
후보 조합을 다시 재현하고 검증하기 위한 operator workflow artifact다.

## Candidate Review 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Candidate Review
  -> Candidate Board에서 후보 역할 / 다음 행동 확인
  -> Inspect Candidate에서 후보 상세 확인
  -> Open Candidate In Pre-Live Review 또는 Send To Compare
```

Latest / History result handoff:

```text
Latest Backtest Run 또는 History selected record
  -> Review As Candidate Draft
  -> Backtest > Candidate Review > Candidate Intake Draft
  -> result snapshot / Real-Money signal / data trust snapshot 확인
  -> optional Save Candidate Review Note
  -> CANDIDATE_REVIEW_NOTES.jsonl
  -> optional Prepare Current Candidate Registry Row
  -> explicit Append To Current Candidate Registry
```

구분:

- Candidate Review는 후보를 투자 추천으로 확정하는 화면이 아니다.
- Candidate Review는 current candidate, near miss, scenario를 먼저 읽는 중간 검토 화면이다.
- `Send To Compare`는 후보 row의 `compare_prefill`을 우선 사용하고,
  기존 strict annual seed 후보는 registry id 기반 기본값을 사용한다.
- GTAA seed 후보처럼 `compare_prefill`은 없지만 전략 `contract`가 남아 있는 경우에는
  해당 `contract`를 compare override로 변환해 form에 채운다.
- 후보 row에 `compare_prefill`도 없고 변환 가능한 `contract`도 없으면,
  사용자가 해결할 수 있는 설정 문제가 아니라 해당 후보 row의 compare 재진입 정보가 부족한 상태다.
- Candidate Intake Draft는 registry에 저장된 후보가 아니라 검토 초안이다.
- Candidate Review Note는 초안을 보고 남기는 operator decision 기록이다.
- Candidate Review Note를 저장해도 current candidate registry에 자동 등록되지 않는다.
- Review Note를 registry row로 남기려면 `Review Notes` 탭에서 row preview를 확인한 뒤
  `Append To Current Candidate Registry`를 명시적으로 눌러야 한다.
- `Suggested Next Step`은 다음 검토 행동 제안이지 live trading 승인이나 최종 투자 판단이 아니다.
- Pre-Live Review로 넘겨도 저장 전 초안일 뿐이며, 실제 저장은 `Save Pre-Live Record`로 한다.

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
- `History > Selected History Run > Saved Input & Context`

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
- `History > Selected History Run > History Real-Money / Guardrail Scope`
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

## History 흐름

History는 compact summary 중심이다.
모든 selection history row를 그대로 저장하지 않는다.

대표 action:

- `Inspect`: 저장된 record를 읽는다.
- `Run Again`: 저장된 payload로 다시 실행한다.
- `Load Into Form`: 저장된 입력값을 single strategy form에 복원한다.

Phase 28 이후 History의 selected record 영역에는
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

## Pre-Live Review 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Pre-Live Review
  -> current candidate 선택
  -> Real-Money 신호와 기본 Pre-Live 상태 확인
  -> operator reason / next action / review date 수정
  -> 저장 전 JSON draft 확인
  -> Save Pre-Live Record
  -> PRE_LIVE_CANDIDATE_REGISTRY.jsonl append
  -> Pre-Live Registry tab에서 active record 확인
```

구분:

- current candidate registry는 후보 자체를 정의한다.
- pre-live registry는 그 후보를 실전 전 어떻게 관찰하거나 보류할지 기록한다.
- `Save Pre-Live Record`는 live trading 승인 버튼이 아니다.
- `paper_tracking`도 실제 돈을 넣는다는 뜻이 아니라 paper 관찰 상태다.

## Portfolio Proposal 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Portfolio Proposal
  -> Create Proposal Draft
  -> current candidate 여러 개 선택
  -> proposal objective / type / status / capital scope 입력
  -> 후보별 proposal role / target weight / weight reason 입력
  -> target weight total / blocker 확인
  -> Portfolio Proposal JSON Preview 확인
  -> Save Portfolio Proposal Draft
  -> PORTFOLIO_PROPOSAL_REGISTRY.jsonl append
  -> Monitoring Review tab에서 blocker / review gap 확인
  -> Pre-Live Feedback tab에서 current pre-live status 비교
  -> Paper Tracking Feedback tab에서 current result snapshot 성과 비교
  -> Proposal Registry tab에서 JSON inspect
```

구분:

- Portfolio Proposal은 current candidate 여러 개를 묶은 proposal draft다.
- saved portfolio는 재현 가능한 weight setup이고, proposal은 그 후보 묶음의 목적과 검토 이유를 남긴다.
- `Save Portfolio Proposal Draft`는 live trading 승인 버튼이 아니다.
- proposal 저장은 current candidate registry나 pre-live registry를 자동 변경하지 않는다.
- 현재 proposal UI는 optimizer가 아니며, target weight는 manual / equal-weight 초안 기준이다.
- `Monitoring Review`의 `blocked`, `needs_review`, `review_ready`는 review 요약이며 live approval 상태가 아니다.
- `Pre-Live Feedback`은 proposal snapshot과 현재 Pre-Live registry를 비교하는 읽기 전용 surface다.
- `Paper Tracking Feedback`은 proposal evidence snapshot과 현재 Pre-Live result snapshot의 CAGR / MDD를 비교하는 읽기 전용 surface다.
- 현재 `Paper Tracking Feedback`은 실제 paper PnL 시계열 자동 계산이 아니라 Pre-Live record에 저장된 최신 snapshot 비교다.

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
