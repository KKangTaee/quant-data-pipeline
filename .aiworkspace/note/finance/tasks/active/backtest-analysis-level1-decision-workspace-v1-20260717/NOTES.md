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
