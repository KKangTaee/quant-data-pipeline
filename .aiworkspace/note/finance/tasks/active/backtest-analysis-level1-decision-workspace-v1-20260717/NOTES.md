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
