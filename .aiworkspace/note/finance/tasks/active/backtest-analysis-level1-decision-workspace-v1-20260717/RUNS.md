# Runs

## 2026-07-17 Design Audit

- finance canonical docs와 Backtest UI ownership 문서 확인
- current Level1 Streamlit surface와 supported strategy entry 확인
- browser에서 current Single Strategy / Portfolio Mix 흐름 확인
- visual companion으로 entry, single, Mix, result, advanced settings, strategy catalog,
  saved Mix 대안 비교
- 사용자 승인 결정을 `DESIGN.md`에 통합

구현 command, test result, Browser QA 결과는 detailed PLAN 실행부터 차수별로
추가한다.

## 2026-07-17 Detailed Plan Audit

- `writing-plans` 절차로 5차 / 9 Task 구현 계획 작성
- 32개 acceptance criteria를 truth, read model, Single, Mix, closeout Task에 배치
- 108개 Markdown code fence 균형 확인
- placeholder / undefined fixture / 보호 파일 검사 명령 self-review 완료
- `git diff --check`와 staged protected-path audit은 계획 commit 직전에 fresh 실행

## 2026-07-18 Execution Baseline

- `.venv`에는 pytest가 없어 `uv run --with pytest`로 repository 변경 없이 runner 주입
- existing boundary + service baseline: 845 passed, 11 failed, 35 subtests passed
- 기존 실패 범위: Sentiment React contract 1건, 이전 Practical Validation / Final Review
  source contract 10건; Level1 소유 파일 변경 전 baseline debt로 기록

## 2026-07-18 Task 1 RED -> GREEN

- RED: 새 `backtest_analysis_decision_workspace` service import 부재로 collection 실패
- GREEN: `3 passed`
- compile: strategy catalog / decision workspace service 통과
- `git diff --check`: 통과

## 2026-07-18 Task 2 RED -> GREEN

- RED: readiness projection / root dedup import 부재로 collection 실패
- GREEN focused: `6 passed`
- existing handoff regression: `3 passed, 829 deselected`
- target compile / `git diff --check`: 통과

## 2026-07-18 Task 3 RED -> GREEN

- RED 1: complete workspace builder import 부재로 collection 실패
- GREEN 1: decision / KPI / error projection 포함 `8 passed`
- RED 2: date가 포함된 configuration / meta / saved Mix JSON 직렬화 실패
- GREEN 2: JSON-ready projection 보강 후 `9 passed`
- target compile / `git diff --check`: 통과

## 2026-07-18 Task 4 RED -> GREEN

- RED: Level1 React source 부재로 boundary test 2건 실패
- React production build: Vite 5.4.21, 175 modules transformed, 성공
- GREEN boundary: `2 passed, 24 deselected`
- ResizeObserver / two-surface / intent-only / 760px contract 확인
- build / node_modules는 `.gitignore` 적용, stage 제외

## 2026-07-18 Task 5 RED -> GREEN

- RED: adapter / fragment / stale marker / fingerprint stamp 부재 4건 실패
- 추가 RED: failed execution이 이전 성공 bundle을 지우는 회귀 재현
- 추가 RED: legacy `Advanced Inputs` / `Promotion Policy Signal` label 재현
- GREEN focused + boundary: `41 passed`
- existing single / latest run / history regression: `4 passed, 828 deselected`
- target py_compile / import smoke / `git diff --check`: 통과

## 2026-07-18 Task 6 RED -> GREEN

- RED: explicit handoff handler 부재 2건과 decision-first 상세 근거 분리 부재 1건 실패
- GREEN focused decision / boundary: `44 passed`
- 관련 service contract: `4 passed, 828 deselected`
- 계획 선택 회귀: `20 passed, 856 deselected`
- React production build: Vite 5.4.21, 175 modules transformed, 성공
- target py_compile / `git diff --check`: 통과
- stale 결과는 삭제·숨김 없이 참고용 상세 근거로 유지하고 Level2 인계만 차단

## 2026-07-18 Task 7 RED -> GREEN

- RED: pure Mix role / weight, legacy role inference, Mix read-model 계약 3건 실패
- GREEN pure contract: `3 passed`
- Mix / saved portfolio 관련 회귀: `12 passed, 837 deselected`
- web-owned weighted Mix Gate를 pure service로 이동하고 직접 caller를 public API로 전환
- weighted bundle / saved replay에 component roles를 추가하되 legacy role-less record는 추론으로 호환
- target py_compile / `git diff --check`: 통과

## 2026-07-18 Task 8 RED -> GREEN

- RED: distinct Mix action handlers 부재와 inner mode / role UI 부재 2건 실패
- GREEN focused Task 8: `7 passed, 876 deselected`
- decision + boundary 전체: `51 passed`
- Portfolio / Mix service 회귀: `60 passed, 772 deselected`
- React production build: Vite 5.4.21, 175 modules transformed, 성공
- save Mix와 Level2 source handoff를 별도 Python adapter로 분리하고 mocked persistence로 상호 비호출 확인
- 역할 / 비중 / source context fingerprint를 weighted result와 history context에 기록
- target py_compile / `git diff --check`: 통과

## 2026-07-18 Task 9 Runtime QA Findings RED -> GREEN

- fresh pre-doc focused: decision workspace `20 passed`, boundary `31 passed`
- fresh pre-doc service: `821 passed, 11 failed, 35 subtests passed`
- 11 failures는 implementation 전 baseline과 동일한 Sentiment React 1건,
  Practical Validation / Final Review legacy source contract 10건이다.
- stale Level1 expectation 3건은 새 current contract로 정렬 후 focused
  `3 passed, 829 deselected`를 확인했다.
- Browser RED 1: GTAA component 선택 뒤 callback nested rerun warning 노출
- GREEN 1: callback rerun suppression test 추가 후 focused + boundary `52 passed`
- Browser RED 2: Equal Weight 새 실행 직후 `이전 설정 결과` 판정
- GREEN 2: runner / read model selection fingerprint shape 통일 후 fresh result,
  GTAA 변경 뒤 stale result 보존을 실제 실행으로 확인
- Browser RED 3: Streamlit dark theme에서 밝은 Level1 card 제목 / KPI 대비 소실
- GREEN 3: light color-scheme / scoped text token 적용, focused + boundary
  `53 passed`, React Vite 5.4.21 `175 modules transformed`
- target 12-module py_compile: 통과

## 2026-07-18 Task 9 Browser QA

- desktop 1440x1000: fixed Level1 title, Single / Mix entry, purpose catalog,
  Risk-On development/no handoff, contextual disclosures, context-preserving run,
  decision -> KPI -> reason -> detail, fresh -> stale preservation 확인
- Equal Weight actual run: CAGR 0.116, MDD -0.173, Sharpe 1.002, volatility 0.117;
  실행 직후 fresh, GTAA 선택 뒤 `이전 설정 결과`
- Mix actual run: GTAA + Equal Weight, role Core/Core, 50/50, total 100%,
  weighted CAGR 9.23%, Mix setup save action과 Gate-blocked handoff 분리 확인
- 760x1000: outer 760/760, context iframe 717/717, decision iframe 717/717,
  internal overflow 0, grids single-column, button text normal wrap, CTA 675/675,
  ResizeObserver height desktop 1047/586 -> 760px 1442/820 확인
- screenshots (generated, unstaged):
  `backtest-analysis-level1-decision-workspace-desktop-qa.png`,
  `backtest-analysis-level1-decision-workspace-760-qa.png`

## 2026-07-18 Completion Verification

- decision workspace focused: `21 passed, 3 warnings`
- refactor boundary / visual contract: `32 passed, 3 warnings`
- full service contracts: `821 passed, 11 failed, 3 warnings, 35 subtests passed`
- service의 11 failures는 execution baseline과 동일한 Sentiment React 1건,
  Practical Validation / Final Review legacy source contract 10건이며 Level1 신규
  failure는 0건이다.
- React production build: Vite 5.4.21, `175 modules transformed`, 성공
  - `build/index.html` 0.42 kB
  - `build/assets/index-DWUGOc0n.css` 5.74 kB
  - `build/assets/index-DIdElWXi.js` 328.41 kB
- target 12-module `py_compile`: exit 0, output 없음
- Browser QA screenshots와 runtime JSONL은 generated / protected artifact로
  stage하지 않는다.

## 2026-07-18 6차 Task 10 RED -> GREEN

- RED: `backtest_single_settings_workspace` import 부재로 collection 실패
- GREEN focused: single settings / duplicate picker / current-work ownership `3 passed`
- decision + boundary 전체: `56 passed, 3 warnings`
- React production build: Vite 5.4.21, `175 modules transformed`
- settings shell / strategy / family dispatch py_compile: 통과
- `git diff --check`: 통과

## 2026-07-18 6차 Task 11 RED -> GREEN

- RED: 전술 전략 6종의 공통 설정 계층과 compact ticker 계약 `2 failed, 1 passed`
- GREEN: 계층 / compact ticker focused `3 passed, 56 deselected`
- strategy / prefill / payload 관련 회귀 `27 passed, 864 deselected`
- decision + boundary 전체 `59 passed, 3 warnings`
- 6개 form과 common renderer `py_compile`: 통과
- `git diff --check`: 통과
- widget key / payload key / handler는 유지하고 사용자 흐름만 핵심 설정 -> Universe
  -> 선택·보유 -> 비용·위험으로 통일

## 2026-07-18 6차 Task 12 RED -> GREEN

- RED: strict factor 7개 concrete renderer에 공통 계층이 없어 hierarchy contract 실패
- GREEN hierarchy: `1 passed, 36 deselected`
- strict factor / Quality / Value / Quality+Value / prefill focused:
  `14 passed, 855 deselected`
- strict 관련 service contract 확대: `28 passed, 804 deselected`
- refactor boundary 전체: `37 passed, 3 warnings`
- strict factor `py_compile` / `git diff --check`: 통과
- annual / quarterly widget key, strategy key, factor array, Universe 계약과 handler는
  유지하고 300종목 원문·PIT·coverage 근거는 `Universe 근거`로 이동

## 2026-07-18 6차 Task 13 Browser QA

- desktop 1440x1000: 중복 Strategy dropdown 없음, Quality + Value Annual / Quarterly
  segmented control, 단일 current settings summary, 공통 4-section order, compact
  300-ticker summary와 collapsed full evidence를 확인했다.
- 실제 Equal Weight 실행 완료 `2.997s`; actual KPI는 CAGR `0.116`, MDD `-0.173`,
  Sharpe `1.002`, volatility `0.117`이다.
- 실제 Quality + Value Snapshot (Strict Annual) 실행 완료 `22.321s`.
- 실행 후 strategy 변경 시 result는 `이전 설정 결과`로 보존되고 자동 Level2
  handoff는 일어나지 않았다. Risk-On은 `개발 중이므로 현재 Level2로 보낼 수 없음`을
  유지했다.
- GTAA, Global Relative Strength, Dual Momentum, Risk Parity 선택과 공통 summary /
  section render를 확인했다.
- 760x1000: outer width `760/760`, active context / decision iframe `717/717`, outer
  horizontal overflow `0`, catalog와 settings가 one-column로 줄바꿈됨을 확인했다.
- screenshots generated / unstaged:
  `backtest-analysis-level1-single-settings-desktop-qa.png`,
  `backtest-analysis-level1-single-settings-760-qa.png`.

## 2026-07-18 6차 Task 13 Fresh Verification

- Level1 decision workspace: `23 passed, 3 warnings`
- refactor boundary / visual contract: `37 passed, 3 warnings`
- full service contracts: `821 passed, 11 failed, 3 warnings, 35 subtests passed`
- 11 failures는 기존 baseline과 동일한 Sentiment React 1건, Practical Validation /
  Final Review legacy source contract 10건이며 이번 Level1 신규 failure는 0건이다.
- React production build, target form py_compile, `git diff --check`: 통과.

## 2026-07-18 6차 Task 13 Code Review

- review range: `e2d489a9..54a66cbe`
- Critical / Important / Minor finding: `0 / 0 / 0`, verdict `Ready to merge: Yes`
- reviewer fresh verification: decision + boundary `60 passed`, 관련 service
  `31 passed, 801 deselected`, diff-check / 11개 영향 Python AST parse 통과.
- 기준/HEAD AST 비교에서 payload key/value와 `_handle_backtest_run()` 호출은 동일했다.
  허용값이 하나였던 fixed `timeframe` / `option` widget만 계획대로 동일 payload 상수로
  바뀐 의도적 예외다.
- 지정 range와 closeout staging 모두 registry / run history / saved / `.superpowers/` /
  screenshot을 제외한다.

## 2026-07-18 7차 Task 14~19 RED -> GREEN

- Task 14 pure schema foundation: 9개 user choice, field type/range/option/visibility,
  validation error와 draft key를 Streamlit-free service로 만들었다.
- Task 15 tactical/allocation: Equal Weight, GTAA, GRS, Risk Parity Trend, Dual Momentum,
  Risk-On Momentum 5D의 exact legacy payload key/value parity를 고정했다.
- Task 16 strict factor: Quality / Value / Quality+Value Annual·Quarterly와 replay-only
  Quality Snapshot의 factor/universe/overlay/guardrail payload parity를 고정했다.
- Task 17 Python adapter: current catalog option, prefill/draft, intent dedup/allow-list,
  callable runner 확인과 same-schema fallback을 연결했다.
- Task 18 React settings: profile, variant, 4-section schema renderer, 7 control type,
  advanced disclosure, pending lock, ResizeObserver와 760px responsive CSS를 구현했다.
- Task 19 primary cutover: `backtest_single_strategy.py`에서 legacy form dispatch를 제거하고
  React settings -> validated Python intent -> existing runner 경로로 전환했다.
- 구현 단위 commit: `9c7deb90`, `f7fbb3ca`, `b1d18fe4`, `444a50fd`, `9e04fade`,
  `98bdfb50`.

## 2026-07-18 7차 Task 20 QA Findings RED -> GREEN

- Browser RED 1: current Quality picker에 replay-only `기존 스냅샷`이 노출되고 Python
  current catalog allow-list와 불일치했다.
- GREEN 1: primary variant options를 current `family_variant_options()`로 제한하고 focused
  analysis tests `29 passed`; commit `3a327c60`.
- Browser RED 2: React가 보존한 hidden direct-ticker default를 validator가 inactive field로
  거부해 actual 실행이 기록되지 않았다.
- GREEN 2: Python adapter가 schema dependency로 visible submitted branch만 projector에
  전달하고 unknown key rejection은 유지했다. focused analysis tests `30 passed`; commit
  `0e65bbb4`.
- 새 서버 직후 QA tab의 pending 고착은 console의 WebSocket `/health` 오류로 browser
  disconnect임을 구분했다. 안정된 서버에 reload한 뒤 같은 intent로 actual run을 완료했다.

## 2026-07-18 7차 Task 20 Browser QA

- desktop 1440x1000: Quality+Value, Quality, Value, GTAA, GRS, Dual Momentum,
  Risk Parity Trend, Equal Weight, Risk-On Momentum 5D 모두 profile 1개, 공통 section 4개,
  CTA 1개를 확인했다. Quality에는 Annual/Quarterly 2개만 노출된다.
- actual Equal Weight: `equal_weight`, 2016-01-01~2026-07-18, 4 ticker, `2.955s`.
- actual GTAA: `gtaa`, 2016-01-01~2026-07-18, `3.160s`.
- actual Quality+Value Annual: `quality_value_snapshot_strict_annual`,
  2021-07-18~2026-07-18, `22.492s`.
- 세 실행 모두 새 Run History row와 Level1 decision projection을 만들었고 실행 자체가
  Level2 source를 등록하지 않는 explicit handoff separation을 유지했다.
- 760x1000: settings main `clientWidth=717`, `scrollWidth=717`, 첫 grid single column
  `675px`, section 4개, CTA 1개, variant control wrap과 iframe height sync를 확인했다.
- screenshots generated / unstaged:
  `backtest-analysis-level1-react-settings-desktop-qa.png`,
  `backtest-analysis-level1-react-settings-760-qa.png`.

## 2026-07-18 7차 Task 20 Fresh Verification

- pure settings service: `43 passed`.
- Level1 decision / adapter: `30 passed, 3 warnings`.
- refactor boundary / visual contract: `40 passed, 3 warnings`.
- focused total: `113 passed`; warning은 기존 edgar deprecation 3건이다.
- full service contracts: `821 passed, 11 failed, 35 subtests passed, 3 warnings`.
  11 failures는 pre-7차 baseline과 같은 Sentiment React 1건, Final Review 4건,
  Practical Validation 6건이며 신규 Level1 failure는 0건이다.
- React production build: Vite 5.4.21, `175 modules transformed`, 성공.
  `index.html` 0.42 kB, CSS 9.29 kB, JS 333.78 kB.
- target 5-module `py_compile`: exit 0, output 없음.
- post-doc `git diff --check`: exit 0, output 없음.
