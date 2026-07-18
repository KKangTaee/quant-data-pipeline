# Notes

## 2026-07-17 Current Audit

- Level1의 올바른 역할은 단일 전략 또는 weighted Mix candidate source를 만들고
  Level1 data / execution readiness를 확인한 뒤 명시적으로 Level2에 넘기는 것이다.
- 현재 primary 전략 실행, 결과 KPI / chart, Data Trust, factor readiness, policy
  signal, handoff 기능은 존재한다.
- 핵심 문제는 기능 부재보다 혼합된 information architecture와 duplicated state /
  explanation ownership이다.
- `app/web/backtest_result_display.py`와 `app/web/backtest_compare/page.py`는 큰 기존
  surface이므로 한 번에 runtime까지 재작성하지 않고 read model / adapter 경계부터
  도입한다.
- `Risk-On Momentum 5D`는 연구용이 아니라 개발 도중 미완성된 전략이다.
- 실행 성공, saved Mix, Level2 candidate는 서로 다른 persistence contract다.

## Approved Visual Decisions

- 목적 분기형 entry
- 마지막 workspace 복원
- single S1 / Mix M1 four-step shell
- R1 decision-first result
- G1 contextual advanced settings
- C1 purpose-grouped catalog
- P1 saved Mix inside Mix Step 1
- T2 read model + one-shell

시각 companion 산출물은 `.superpowers/brainstorm/57312-1784291161/`에 있으며
generated artifact이므로 commit하지 않는다.

## 2026-07-17 Design Self-Review

- C1 목적 그룹에 포함되는 초기 운영 전략과 development 전략을 명시했다.
- Strict Annual / Quarterly variant는 strategy card가 아니라 Step 2 설정으로
  유지하도록 경계를 명시했다.
- 전체 화면 reset 회귀를 막기 위해 같은 frontend bundle 안에서 stable context와
  mutable result를 별도 mount로 두는 physical render contract를 추가했다.
- 합의된 A / B / S1 / M1 / R1 / G1 / C1 / P1 / T2 결정과 out-of-scope를
  acceptance criteria에 대조했고 추가 미결정 사항은 발견하지 않았다.

## 2026-07-17 Detailed Plan Self-Review

- 5차 roadmap을 9개 distinct implementation unit으로 분해하고 각 unit에 정확한
  소유 파일, RED 테스트, GREEN 명령, 한국어 commit을 지정했다.
- Single / Mix 공통 read model의 complete builder가 모든 projected variable을
  계산한 뒤 반환하도록 계획 예시를 보강했다.
- Mix legacy replay 예시는 실제 입력으로 교체했고, saved Mix 저장과 Level2 handoff가
  서로 다른 handler를 사용하도록 검증 단위를 고정했다.
- saved Mix 저장 adapter가 기존 `source_strategy_names`와
  `compare_source_context`를 잃지 않도록 persistence compatibility를 보강했다.
- protected path 검사 명령은 match 시 즉시 실패하는 명시적 shell condition으로
  고정했다.
- placeholder, 불균형 code fence, undefined test fixture를 재검사했고 남은 항목은
  발견하지 않았다.

## 2026-07-18 Task 5 Execution Decision

- Streamlit form 안의 widget 변경값은 submit 전 Python에 전달되지 않는다.
- 각 form의 payload builder를 복제해 draft를 만들지 않고 모든 single 실행이 통과하는
  shared runner에서 normalized draft와 fingerprint를 기록한다.
- 새 실행 실패 시 이전 성공 bundle은 유지되고 새 draft fingerprint와 달라져 stale이
  되므로 설계의 보존·차단 contract를 만족한다.

## 2026-07-18 Task 9 Browser Findings

- React component `on_change` callback은 이미 Streamlit rerun lifecycle 안에서
  실행된다. callback에서 다시 `st.rerun(scope="app")`을 호출하면 no-op 경고가
  사용자 화면에 노출되므로 callback consume path는 `rerun_scope="none"`을 사용한다.
- Single draft fingerprint는 current read model과 같은 selection shape
  (`strategy_choice`만)로 계산해야 한다. 실행 path만 `strategy_name`을 selection에
  중복 포함하면 방금 실행한 result도 즉시 stale이 된다.
- Streamlit dark theme는 custom component iframe body / heading에 밝은 text color를
  주입한다. Level2/3와 같은 밝은 card language를 쓰는 Level1 component는
  `color-scheme: light`와 workspace-scoped heading / KPI color를 명시해야 한다.
- 실제 Equal Weight 실행은 context mount를 유지한 채 fresh result를 만들었고,
  GTAA 선택 뒤 같은 result가 `이전 설정 결과`로 보존되는 것을 확인했다.
- 실제 GTAA + Equal Weight Mix는 role `Core / Core`, weight `50 / 50`, total 100%,
  weighted result와 `Mix 저장` action을 표시했다. Gate가 막힌 상태에서는 invalid
  Level2 CTA를 만들지 않는다.

## 2026-07-18 6차 Single Settings Corrective Audit

- React `select_strategy` intent와 legacy Streamlit `Strategy` selectbox가 같은
  `backtest_strategy_choice`를 쓰면서 picker가 중복 노출된다.
- Single runtime은 7개 form 파일의 13개 renderer로 구성되며 shared runner 이전의
  widget / payload / validation / prefill은 strategy-specific이다.
- full React editor는 이 계약을 이중 구현하므로 Python shared settings shell이
  가장 작은 안전한 corrective boundary다.
- 기존 boundary test는 label rename만 확인해 실제 information hierarchy 누락을
  잡지 못했다. 6차는 duplicate picker, section ordering, Korean first-read,
  compact universe, submit copy를 RED contract로 먼저 고정한다.

## 2026-07-18 6차 Single Settings Runtime Decision

- strategy 선택은 React purpose catalog 하나만 소유하고 Python은 선택값의 유효성,
  family variant와 form dispatch를 소유한다.
- Strict Annual / Quarterly는 별도 strategy card가 아니라 현재 family 설정의
  segmented control이며, 변경 시 같은 current settings summary를 갱신한다.
- 전체 ticker와 PIT / statement / coverage 진단을 첫 화면에 펼치면 설정 결정과
  근거 확인이 섞인다. first-read는 대표 ticker 요약만 보여주고 전체 원문은
  `전체 종목 보기`, 데이터 계약은 `Universe 근거`로 둔다.
- 실제 QA 서버가 `fileWatcherType none`으로 떠 있어 최초 확인 화면은 이전 build였다.
  동일 worktree 8505 프로세스를 재시작한 뒤 새 코드 기준으로 Browser QA를 다시 했다.

## 2026-07-18 7차 All-Strategy UI Audit

- 6차 wrapper는 모든 전략에 적용됐지만 `single_settings_section()`이 native
  `st.container(border=True)`이므로 React one-shell과 같은 visual component가 아니다.
- form 파일의 native widget / form / expander 호출은 최소 167개이며 shared ETF /
  factor helper가 추가 legacy UI와 영문 copy를 렌더링한다.
- actual GTAA DOM에서 `Score Horizons`, `Promotion Policy Signal`, `Minimum Price`와
  raw English prose가 재현됐다. Equal Weight도 같은 native field surface를 사용한다.
- Quality + Value가 상대적으로 정돈되어 보인 것은 기존 strict-factor disclosure가
  많은 first-read detail을 감췄기 때문이며 별도 React settings architecture가 아니다.
- variant가 없는 전략은 multiline HTML 안의 빈 variant row가 Markdown block 경계를
  만들어 maturity `<span>`을 code text로 노출한다. plain React text badge로 제거한다.
- 7차는 6차의 full React editor out-of-scope 결정을 명시적으로 뒤집는 승인된 범위
  확장이다. strategy runtime, DB, Level2 / Level3 Gate는 확장하지 않는다.

## 2026-07-18 7차 Runtime Decisions And QA Corrections

- settings contract는 9개 user choice와 12개 primary concrete variant를 제공한다.
  pure service의 legacy `Quality / Snapshot`은 history/replay 호환을 위해 유지하지만
  current catalog allow-list에 없으므로 primary variant picker에는 노출하지 않는다.
- React는 schema의 field/value를 보존하는 editor이므로 숨은 branch 기본값도 intent에
  포함될 수 있다. Python adapter가 current dependency value로 visible branch를 다시
  계산해 payload projector에 넘기고, unknown key는 그대로 validator에 전달해 거부한다.
- strategy/variant 전환, field visibility, type/range/option, exact runner payload,
  callable handler와 intent dedup은 Python owner다. React는 profile/section/control을
  렌더링하고 `select_strategy_variant` / `run_single_strategy` intent만 보낸다.
- 새 서버 직후 disconnected Browser tab에서는 React local pending만 남을 수 있다.
  console의 WebSocket/health error로 QA 환경 문제를 구분한 뒤 안정된 서버에 reload해
  actual execution을 재검증했다.
- actual run은 실행 성공과 Run History append까지만 수행했다. Level2 source 등록은
  decision Gate 뒤 명시적 handoff action으로 계속 분리되어 있다.

## 2026-07-18 8차 Multi-Select Design Self-Review

- native `<select multiple>`의 modifier-key interaction 문제와 Python 배열 계약을 분리해
  renderer만 교체하는 최소 변경 경계를 확인했다.
- 실제 schema option 수는 compact 4·14개, large ticker 1,031개이므로 20개 임계값이
  현재 전략 전체에서 checkbox-card와 검색형 목록을 안정적으로 구분한다.
- compact 전체 선택, large 검색 결과 전체 선택, 전체 선택 해제의 서로 다른 범위를
  명시했고 모든 결과는 schema catalog 순서로 정규화한다.
- React intent, Python visible branch / validation / payload projector, runner와 persistence는
  변경하지 않으며 required 0개 선택은 기존 실행 전 검증이 소유한다.
- desktop / 760px, keyboard focus, initial DOM 상한, actual Quality / GTAA / large ticker QA를
  acceptance에 포함했다. placeholder, 미결정 UX, 범위 충돌은 발견하지 않았다.

## 2026-07-18 8차 Written Design Approval And Plan Self-Review

- 사용자가 adaptive C안의 written design을 승인해 같은 worktree에서 inline execution으로
  이어가기로 했다.
- Task 21은 source contract RED를 먼저 확인한 뒤 catalog-order helper, compact/search control,
  CSS와 React build를 하나의 reviewable implementation unit으로 묶었다.
- Task 22는 actual Quality/GTAA/large option desktop·760px QA, fresh full verification,
  finance docs와 root handoff sync, protected-path audit만 소유한다.
- option identity, helper signature, threshold, CSS selector와 test token을 대조했고 모두
  일치한다. placeholder, 조건부 소유 파일, 불균형 code fence는 남기지 않았다.

## 2026-07-18 8차 Runtime Decisions And QA Findings

- compact와 search control은 같은 `normalizeMultiSelectValues()`를 사용해 클릭 순서가
  아니라 schema catalog 순서로 array를 만든다. 설정 edit는 local draft만 바꾸고 submit
  전에는 component intent나 Python rerun을 만들지 않는다.
- actual Quality에서 modifier 없이 두 항목을 추가해 5→6→7과 기존 선택 유지, Quality
  한정 clear/select-all, Value selection 보존을 확인했다.
- actual GTAA는 6·12개월을 제거한 뒤 modifier 없이 다시 추가해 2→3→4와 1개월 선택
  유지를 확인했다. 첫 strategy 전환 직후 한 번 Quality로 복귀했지만 controlled retry는
  GTAA가 5초 이상 유지됐고 이후 전체 interaction에서 재발하지 않았다.
- defensive asset은 1,031 options 중 첫 100 row와 remaining 931 안내만 렌더링했다.
  SPY 검색 결과 1개, add 후 catalog-order 4-item summary, chip remove 후 3-item 복귀를 확인했다.
- Browser runtime의 Tab key 전달은 iframe input에서 focus를 이동시키지 못해 actual focus-ring
  visual은 자동 판독하지 못했다. `:focus-visible` source contract와 production CSS build는
  통과했으며 이는 남은 수동 accessibility QA gap이다.

## 2026-07-18 9차 Preset Application Audit And Design

- current React editor에서 GTAA preset을 `GTAA Universe`에서
  `GTAA SPY Low-MDD Style Top-2 ADV20`으로 바꿨을 때 preset name만 바뀌고 `top=3`,
  `interval=1`, score horizon `1/3/6/12`가 그대로 남는 회귀를 actual Browser에서 재현했다.
- legacy `GTAA_PRESET_PARAMETER_DEFAULTS`와 native form은 같은 preset에 `top=2`,
  `interval=4`, score horizon `1/6`, `IEF/TLT`, `ADV20=20M`을 적용한다.
- 다른 strategy preset 대부분은 universe-only catalog이고, Quality strict managed preset은
  target size만 추가로 소유한다. 모든 preset에 임의 tuning을 만들면 근거 강도를 과장한다.
- 승인된 C안은 schema defaults로 strategy / variant base profile을 만들고, legacy note 또는
  canonical parameter map에 이미 명시된 GTAA 값만 evidence-backed override로 적용한다.
- preset change는 preset-owned field를 base + override로 재설정하지만 date range와 manual
  ticker draft는 보존한다. saved replay / prefill explicit values는 initial profile보다 우선한다.
- React와 fallback은 Python read model의 patch와 feedback label만 기계적으로 사용하고
  strategy-specific 값, validation, payload, Gate를 계산하지 않는다.

## 2026-07-18 9차 Written Design Approval And Plan Self-Review

- 사용자가 9차 written design을 승인했고 기존 선택대로 현재 worktree / 세션에서 inline
  `executing-plans`로 Task 23~25를 순차 실행한다.
- Task 23은 canonical GTAA evidence map, 모든 named preset family의 complete profile,
  initial prefill precedence와 Python fallback을 하나의 Python-owned contract로 묶는다.
- Task 24는 strategy name이나 preset 숫자가 없는 generic React reducer와 feedback만 소유한다.
- Task 25는 Equal Weight, GTAA base/U3/Top-2, GRS, Risk Parity, Dual Momentum,
  Quality + Value Annual과 manual-to-preset transition을 desktop / 760px에서 확인한다.
- plan의 profile type / runtime key / helper signature / React type / test token을 교차 대조했고
  placeholder, 근거 없는 tuning, 보호 대상 stage, Level2/3 scope 확장은 남기지 않았다.

## 2026-07-18 9차 Runtime Decisions And Browser Findings

- preset profile은 date와 manual ticker를 제외한 schema field 기본값 전체를 소유한다.
  preset 변경 시 이전 preset이나 사용자 tuning이 섞이지 않도록 base profile부터 다시 적용한다.
- `GTAA_PRESET_PARAMETER_DEFAULTS`는 기존 legacy form에 이미 기록된 U1/U3/U5와 Low-MDD
  설정만 확장했다. Equal Weight, GRS, Risk Parity, Dual Momentum, strict factor preset에는
  근거 없는 전략별 숫자를 만들지 않고 strategy/variant 기본 규칙을 적용한다.
- fallback callback은 profile이 실제로 소유한 field id만 widget state에 쓰며, Streamlit
  `date_input`의 `date` 타입과 manual ticker state는 건드리지 않는다.
- 8505 첫 QA에서 old Python process와 새 ignored React build가 섞여 `preset_profiles`가
  없는 TypeError가 한 번 발생했다. `fileWatcherType none` 서버의 stale-process 문제였고,
  current code로 새 8521 QA server를 띄운 뒤 app error 없이 같은 interaction을 검증했다.
- GTAA Top-2는 `top=2`, `interval=4`, horizon `1/6`으로, U3는 `top=2`, `interval=3`,
  horizon `1/3/6`으로 바뀌면서 사용자가 바꾼 시작일은 유지됐다. Equal Weight, GRS,
  Quality+Value는 사용자 수정값을 각 전략 기본값으로 reset했다.

## 2026-07-18 10차 Result Evidence Audit And Design

- `_render_last_run()`이 bundle 존재 확인 전에 decision surface를 mount해 실행 전 Step 3가
  노출된다. 이 surface를 단순히 숨기는 것이 아니라 no-run/fresh/stale/running/error lifecycle을
  pure read model로 만들기로 했다.
- current result detail은 expander·tab·metric·dataframe·chart가 한 Python renderer에 누적돼
  같은 값이 raw decimal과 percentage로 중복되고 다음 행동보다 기술 구조가 먼저 보인다.
- Level1 technical handoff readiness는 실행 성공, settings/result fingerprint, core result identity,
  callable handler만 소유한다. benchmark, ETF operability, liquidity, rolling/split/OOS, cost realism은
  Level2가 최신 데이터와 evidence로 검증할 질문이다.
- current holdings는 broker account가 아니라 마지막 valuation row의 backtest-simulated allocation,
  target은 마지막 valid signal/rebalance row의 latest available signal target으로 정의했다.
- explicit weight가 없을 때는 supported `Next Balance / total` contract가 있을 때만 Python이
  계산한다. cash-only, non-rebalance latest row, partial Mix, missing holdings는 추정 대신 명시적
  상태로 표현한다.
- approved single-page hierarchy는 KPI, combined strategy/benchmark chart, current/target holdings,
  Level1 handoff와 Level2 questions, 4개 purpose evidence group, user tables, technical appendix 순서다.
- 새 `app/services/backtest_analysis_result_workspace.py`가 모든 분류·Gate·format·weight·question을
  소유하고 React와 Python fallback은 같은 JSON-ready read model을 표시한다.

## 2026-07-18 10차 Written Design Approval And Plan Self-Review

- 사용자가 written design을 승인해 기존 요청대로 현재 세션에서 Task 26~30을 inline
  `executing-plans`로 순차 실행한다.
- 순환 import를 피하려고 새 result service는 decision service가 아니라 strategy catalog의
  maturity 원본을 직접 읽고, existing decision surface cutover는 run identity가 준비되는
  Task 29까지 미룬다.
- Level1 identity는 `run_result_id`, successful Level2 registration identity는
  `validation_result_id`로 분리한다. run id는 bundle뿐 아니라 Run History와 single/weighted
  Practical Validation source까지 additive field로 보존한다.
- lifecycle/readiness/question의 display label, lane label, summary는 Python이 제공하며 React는
  state나 raw status를 한국어 의미로 재분류하지 않는다.
- result column 다양성, cash-only/non-rebalance, partial Mix, first/rerun failure를 pure matrix로
  검증하고 실제 desktop/760px QA로 no-run hidden과 stale→running→fresh를 확인한다.
- Task 26 pure truth, Task 27 read model, Task 28 dedicated React/fallback, Task 29 runtime cutover,
  Task 30 QA/docs는 서로 독립된 RED/GREEN과 한국어 commit을 가진다.

## 2026-07-18 10차 Runtime Decisions And Browser Findings

- Level1 technical gate는 성공한 실행, current configuration fingerprint 일치, core result identity,
  callable Level2 handoff handler만 소유한다. 수익률이나 Level2 검증 질문은 Gate를 대신하지 않는다.
- `run_result_id`는 실행 bundle, Run History와 handoff source에 보존하고,
  `validation_result_id`는 성공한 Level2 validation append 뒤에만 생긴다.
- current holdings는 마지막 valuation row의 simulated allocation, target holdings는 마지막 유효
  signal / rebalance row의 latest available target이다. broker 계좌나 주문 제안이 아니다.
- 실제 Equal Weight 실행 뒤 GTAA로 설정을 바꾸면 기존 결과는 `이전 설정 결과 · 참고용`으로
  남고 Level2 CTA는 사라졌다. 새 실행 전 결과를 삭제하거나 과거 결과를 인계하지 않는다.
- 760px에서 result iframe 내부 holdings grid가 811px까지 넓어지는 회귀를 Browser에서 찾았다.
  root는 grid/card의 implicit min-width였고 workspace/card/grid에 `min-width: 0`, body overflow
  boundary를 적용한 뒤 iframe `clientWidth=scrollWidth=717`을 확인했다.
- local server가 `runOnSave=false`여서 Python process restart 전에는 old code / new build가 섞일
  수 있었다. current source로 재시작한 뒤 fresh no-run, execution, stale, responsive QA를 다시 했다.

## 2026-07-18 11차 Result Interpretation Design Decisions

- 사용자는 투자금 control보다 normalized return이면 충분하다고 판단했다. `100 -> 124.9`가
  `+24.9%`라는 관계를 명확히 설명하고 달러 환산은 범위에서 제외한다.
- chart는 실제 날짜 x tick, pointer-only tooltip/crosshair와 Benchmark ticker/contract label을
  표시한다. React는 normalized return이나 Benchmark 의미를 계산하지 않는다.
- next rebalance는 last `Rebalancing=true` row와 explicit cadence가 있을 때만 month-end window로
  표시한다. exact trading date, holiday adjustment 또는 irregular signal date는 추측하지 않는다.
- `기술 부록`은 사용자용 `계산 및 데이터 기준`으로 바꾸고 raw column/meta는 secondary disclosure에
  보존한다. Python이 label/explanation/status를 제공하고 React/fallback은 표시만 한다.

## 2026-07-18 11차 Written Design Approval And Implementation Plan

- 사용자가 written design을 승인해 Task 31~34 implementation plan을 작성했다.
- Task 31은 common chart timeline/date tick/normalized return/Benchmark identity, Task 32는
  holdings schedule과 calculation/data basis, Task 33은 pointer-only SVG/React/fallback,
  Task 34는 Browser QA/verification/docs closeout을 소유한다.
- no-dollar, no-chart-dependency, no-exact-trading-date, Python-owned semantics와 protected path
  constraints를 모든 task에 공통 적용한다.

## 2026-07-18 11차 Implementation And Runtime Decisions

- strategy와 Benchmark를 union timeline에 정렬하되 Benchmark가 없는 날짜에 값을 만들지 않는다.
  desktop 6개 / compact 3개 실제 날짜 tick과 pointer 위치별 지수·누적수익 label은 Python이 제공한다.
- runtime metadata의 `ticker` / `equal_weight` contract는 각각 `대표 ETF 비교` / `후보군 동일 비중
  비교`로 번역해 내부 코드가 첫 화면에 노출되지 않게 했다.
- holdings 일정은 현재 평가일, 최신 신호일, 마지막 리밸런싱, cadence, 다음 월말 예상으로 분리했다.
  cadence가 없으면 `다음 일정 확인 필요`로 남기며 exact trading date를 추측하지 않는다.
- Browser QA에서 SVG 빈 영역은 point/path 밖에서 hover를 받지 않는 것을 찾아 transparent pointer
  capture rect를 추가했다. 실제 hover에서 crosshair와 `2021-01-29 / 전략 +72.2% / SPY +91.0%`
  tooltip이 나타나고 차트 밖에서는 사라지는 것을 확인했다.
- `계산 및 데이터 기준`은 계산 기준, 데이터 기준, 결과 추적 세 section을 먼저 보여주고 원본
  field/meta는 별도 disclosure에 유지한다. keyboard disclosure와 ResizeObserver 높이 동기화를 확인했다.

## 2026-07-18 12차 Current Selection And Factor Presentation Decisions

- 잘못된 GTAA 요약의 원인은 strategy catalog selection과 마지막 실행 bundle configuration을 같은
  context summary에 투영한 것이었다. Single summary를 비우고 현재 title은 catalog selection만
  사용하며, 과거 bundle 자체는 stale reference로 보존한다.
- factor 계산 계약은 이미 raw key 배열을 요구하므로 option의 `value`는 유지하고 `label`만
  Python map에서 한국어 의미와 표준 약어로 만든다. React가 snake_case를 번역하지 않는다.
- native multi-select 개선 뒤 남은 잘림은 option grid의 auto-fit 폭과 direct text node가 원인이었다.
  명시적 label span, `min-width: 0`, `overflow-wrap: anywhere`, 2열/1열 breakpoint로 해결했다.
- reset blue notice, price refresh yellow notice, refresh job table은 같은 stale 상태를 세 번 설명했다.
  Python lifecycle이 `settings_changed`, `price_refresh`, `rerun_failed`를 분류하고 React/fallback은
  하나의 `reference_message`만 표시한다.
- 기존 8505 server는 `runOnSave=false`와 `fileWatcherType none`으로 실행돼 current source를 반영하지
  않았다. 8511 fresh server로 source/build pair를 맞춰 Browser QA하고 종료했다.

## 2026-07-19 13차 Top Shell Audit And Design Decisions

- page entry의 `st.title("Backtest")`와 caption은 `streamlit_app.py`가 소유하고, 별도 workflow
  heading/caption과 red underline `st.pills`는 `backtest_page.py`가 소유한다. 같은 목적을 두 번
  설명하는 구조이며 entry caption에는 현재 product route에 없는 Pre-Live / Portfolio Proposal이 남아 있다.
- stage key, current stage와 legacy normalization은 기존 Python route/state owner가 보존한다. 새
  React shell은 session을 직접 읽거나 route/Gate를 계산하지 않고 validated `select_stage` intent만 보낸다.
- 최상단 추천 기능은 operational count가 아니라 `현재 단계에서 끝낼 일` context card다. Level 내부
  action/Gate와 중복되지 않으면서 단계 소유권을 first-read에서 설명한다.
- desktop은 hero 2열과 stage rail 3열, 760px은 hero 1열과 rail 3열, 520px 이하는 rail 1열을 사용한다.
  ResizeObserver, button semantic, aria-current, reduced-motion과 overflow 0을 acceptance contract로 둔다.
- visual companion은 `.superpowers/brainstorm/31090-1784412863/`에 생성했으며 generated/protected
  artifact이므로 stage하거나 commit하지 않는다.
