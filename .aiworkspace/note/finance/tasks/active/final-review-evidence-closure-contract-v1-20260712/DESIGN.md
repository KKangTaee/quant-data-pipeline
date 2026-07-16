# Final Review Evidence Closure Contract V1 Design

## 이걸 하는 이유?

Final Review의 `남은 판단 근거`는 검증 사실과 개선 방법을 읽기 쉽게 보여주지만, 사용자가 각 항목을 어떻게 끝내야 하는지는 보장하지 않는다. 현재 화면에는 2단계에서 해결 가능한 자료 부족, runtime 또는 evidence adapter 개발이 필요한 제품 공백, 자동으로 제거할 수 없는 방법론 한계, 사용자의 최종 판단, Monitoring 추적 조건이 같은 `REVIEW`로 섞여 있다.

이 상태에서는 Level3 후보가 다음 문제를 가질 수 있다.

- `세부 설명 준비 안 됨`처럼 제품 contract 누락을 사용자 판단 항목으로 보여준다.
- 실제 action이 없는 항목도 `2단계에서 개선`하라고 안내한다.
- 같은 원인이 여러 module과 trace에서 반복되고 고정 감점이 중복될 수 있다.
- Level3에는 근거를 새로 수집하거나 검증할 책임이 없는데, 항목을 수용·이관·보류로 종결하는 장치도 부족하다.

완료 기준은 `남은 근거 0개`가 아니라 `미정 상태 0개`다. Final Review에 올라온 모든 항목은 `해소 완료`, `한계 수용`, `Monitoring 이관`, `개발 후 재검토`, `선정 차단` 중 하나로 끝나야 한다.

## Approved Product Goal

사용자가 승인한 방향은 다음과 같다.

1. 현재 제품으로 해결 가능한 근거는 Practical Validation에서 해결하고 새 validation을 저장한 뒤에만 Final Review로 보낸다.
2. 해결할 수 없는 핵심 근거는 Final Review 승격을 막고 `개발 후 재검토` 상태로 남긴다.
3. 자동으로 없앨 수 없는 비핵심 한계만 Final Review에 전달한다.
4. Final Review는 전달된 한계를 수용·보류 사유에 반영하거나 Monitoring 조건으로 이관해 workflow를 종결한다.
5. React는 표시와 intent만 담당하고 replay, 분류, Gate, 점수, 저장은 Python boundary가 소유한다.

## Current Evidence And Root Cause

### Latest GRS Validation

분석 기준 row는 `validation_selection_rebuilt_grs_macro_top3_ma200_c52d1dac_3772e077`이다.

- validation 저장: `2026-07-12T14:10:37`
- latest replay 실행: `2026-07-12T14:10:12`
- 요청 종료일: `2026-07-10`
- 실제 결과 종료일: `2026-05-29`
- period gap: `42일`
- replay / period status: `REVIEW`
- pre-final enrichment gate: `blocking=false`

`최신 데이터로 전략을 다시 돌렸는가`는 실제로 실행됐지만 requested/actual period가 다르다. Final Review에서 `세부 설명 준비 안 됨`으로 보이는 이유는 `latest_replay` module을 stored curve provenance와 연결하는 trace adapter가 없기 때문이다. evidence 부재가 아니라 presentation contract 부재다.

### GRS Period Alignment

read-only DB 확인과 동일 runtime 재현 결과:

- BIL 2026년 6월 마지막 가격일: `2026-06-26`
- SPY / QQQ / GLD / IEF / TLT 2026년 6월 마지막 가격일: `2026-06-30`
- current GRS month-end alignment 결과 종료일: `2026-05-29`

GRS는 ticker별 month-end row를 만든 뒤 exact date로 정렬한다. BIL의 `2026-06-26`과 다른 ticker의 `2026-06-30`이 맞지 않아 6월 row가 제거된다. GTAA의 latest-common valuation 보강 패턴은 GRS에 적용되지 않는다.

### Data Coverage

같은 validation의 주요 audit 상태:

| Audit | Status | Evidence |
|---|---|---|
| Price DB window coverage | PASS | 대상 7종 100% window row 존재 |
| Provider snapshot freshness | PASS | provider 4개 영역 확인 |
| PIT price window coverage | REVIEW | replay / period가 REVIEW |
| Universe / listing evidence | REVIEW | 7종 중 4종 actual, 3종 partial |
| Survivorship / delisting control | REVIEW | historical delisting 포함 근거 미입증 |

현재 pre-final enrichment gate는 operability, holdings/exposure, macro처럼 existing Python collector가 실행할 수 있는 provider gap만 blocker로 만든다. price period alignment와 lifecycle / survivorship는 plan에 없으므로 `REVIEW`로 Final Review에 올라온다.

### Score Duplication

현재 최신 GRS row의 Level2 impact는 다음처럼 생성된다.

- Latest Runtime Replay: `pv_data_caution`, `missing_contract`, `-6`
- Data Coverage: `pv_data_caution`, `derived`, `-6`

PIT price window가 같은 replay period gap을 다시 포함하므로 하나의 원인이 두 module에서 감점될 수 있다. `-6`은 42일 gap에서 계산한 값이 아니라 role별 고정 정책이다.

## Considered Approaches

### A. Copy And Layout Only

관측값과 설명을 보강하되 기존 REVIEW / Gate / score policy를 유지한다.

- 장점: 구현이 작다.
- 단점: 실제 action이 없는 2단계 안내와 중복 감점, 미정 상태가 그대로 남는다.
- 결정: 채택하지 않는다.

### B. All REVIEW Must Pass

모든 REVIEW를 Level2 blocker로 바꾸고 0개가 될 때까지 승격하지 않는다.

- 장점: stage ownership이 단순하다.
- 단점: historical universe source처럼 현재 미구현인 비핵심 근거 때문에 대부분 후보가 영구 차단될 수 있다.
- 결정: 채택하지 않는다.

### C. Actionability And Terminal-State Contract

각 root issue를 해결 가능성, 중요도, 소유 단계, 실제 action, 종결 상태로 분류한다.

- 장점: 해결 가능한 문제는 Level2에서 닫고, 비핵심 한계는 Final Review에서 명시적으로 종결할 수 있다.
- 단점: audit, Gate, score, UI가 같은 contract를 읽도록 정렬해야 한다.
- 결정: 채택한다.

## Core Invariants

1. Final Review eligible candidate의 `unresolved_actionable_count`는 항상 0이다.
2. `missing_contract`는 사용자 경고가 아니라 product defect다. 필수 module이면 승격을 막고 숫자 감점을 만들지 않는다.
3. 하나의 `root_issue_id`는 Final Review score / card / closure에서 한 번만 반영한다.
4. 실제 실행 handler가 없는 issue에는 action button을 표시하지 않는다.
5. Final Review는 provider fetch, replay, DB ingestion을 실행하지 않는다.
6. Final Review에 보이는 모든 non-PASS item은 저장 시 terminal state를 가져야 한다.

## Evidence Closure Contract

Python service가 audit/module row를 다음 contract로 정규화한다.

```text
root_issue_id
title
observed
expected
cause
derived_checks[]
resolution_class
owner_stage
actionable_now
action_id
completion_criteria
applicability
criticality
gate_effect
accepted_reason
monitoring_condition
terminal_state
```

### resolution_class

| Value | Meaning |
|---|---|
| `resolve_now` | 현재 Python action과 재검증으로 해결 가능 |
| `engineering_required` | runtime, source, adapter 또는 validator 개발 필요 |
| `accepted_limit` | 자동으로 없앨 수 없는 비핵심 방법론 한계 |
| `final_decision` | 사용자가 선택·보류 사유에 반영해야 함 |
| `monitoring_transfer` | 선정 후 Monitoring 조건으로 이관 |

### terminal_state

| Value | Meaning |
|---|---|
| `open` | 아직 처리되지 않음 |
| `resolved` | Level2 재검증과 저장으로 해소 |
| `accepted` | 사용자가 최종 판단에서 한계를 수용 |
| `monitoring_transferred` | Monitoring 조건으로 저장 |
| `deferred` | 개발 후 재검토로 보류 |
| `blocked` | 선정 불가 |

## Stage Ownership And Gate

| Issue state | Level2 behavior | Final Review behavior |
|---|---|---|
| `resolve_now + open` | blocker, 실제 action과 통과 기준 표시 | current 후보에 나타나지 않음 |
| `engineering_required + critical` | blocker, `개발 후 재검토` | current 후보에 나타나지 않음 |
| `engineering_required + noncritical` | 명시적 defer 또는 accepted-limit 전환 필요 | 자동 전달하지 않음 |
| `accepted_limit` | 왜 통과를 허용하는지 저장 | `인수한 한계`로 수용 또는 보류 |
| `final_decision` | handoff reference | 선택·보류 사유로 종결 |
| `monitoring_transfer` | handoff reference | 선정 시 Monitoring 조건으로 저장 |

Final Review에 `선정 전 미해결 항목`이 보이는 것은 legacy/stale recovery 화면만 허용한다. current eligible candidate에서는 이 영역이 항상 비어 있어야 한다.

## Root-Issue Deduplication

module과 audit row는 원인 설명을 위해 유지하지만 closure와 score는 root issue 기준으로 합친다.

예시:

```text
root_issue_id = replay_period_coverage
derived_checks = [latest_replay, pit_price_window_coverage]
```

```text
root_issue_id = historical_universe_coverage
derived_checks = [universe_listing_evidence, survivorship_delisting_control]
```

UI는 root issue card 하나 안에서 derived check를 접힌 기술 근거로 보여준다.

## GRS Replay Period Design

`load_latest_market_date()`의 전체 DB max date를 strategy의 필수 requested end로 직접 사용하지 않는다. source universe와 cash ticker 기준으로 다음 날짜를 분리한다.

- `requested_market_date`: 사용자가 요청한 최신 시장일
- `latest_common_price_date`: 전략 구성 ticker가 공통으로 가진 최신 가격일
- `last_complete_rebalance_date`: 전략 cadence상 완료된 마지막 rebalance 기준일
- `latest_valuation_date`: 주문이나 rebalance가 아닌 최신 평가 기준일

월간 전략의 Gate 원칙:

1. 완료된 마지막 cadence까지 공통 price와 strategy result가 이어지지 않으면 `resolve_now` 또는 `engineering_required` blocker다.
2. 현재 진행 중인 partial month만 뒤처진 경우 `monitoring_transfer`가 될 수 있다.
3. latest-common row를 추가할 때 signal/rebalance와 valuation을 구분해 look-ahead나 가짜 rebalance를 만들지 않는다.
4. GRS에 GTAA 패턴을 재사용할지는 strategy runtime contract test로 결정하며 단순 복사하지 않는다.

## Survivorship Applicability

현재 audit는 `manual_tickers` 고정 universe와 historical dynamic universe를 같은 강도로 평가한다. 이를 분리한다.

### Static Manual Universe

- 각 ticker가 requested start/end에 실제 존재했는지 lifecycle coverage를 확인한다.
- current survivors를 사후 선택했을 가능성은 `accepted_limit`로 설명할 수 있다.
- historical delisting source가 없다는 이유만으로 자동 blocker 또는 고정 감점을 만들지 않는다.

### Dynamic Historical Universe

- point-in-time membership와 delisting control은 필수다.
- 근거가 없으면 `engineering_required + critical` blocker다.
- 사용자의 한계 수용만으로 Final Review에 승격하지 않는다.

## Final Review UX

기존 `남은 판단 근거` 단일 의미를 다음 두 영역으로 분리한다.

### 선정 전 미해결 항목

- current eligible candidate에서는 0개다.
- legacy/stale report에서만 복구 안내와 함께 표시한다.
- 실제 Level2 action이 있으면 같은 후보로 이동한다.
- action이 없으면 `개발 후 재검토`이며 수집 버튼을 표시하지 않는다.

### 인수한 한계와 최종 판단 항목

각 root issue card는 다음을 보여준다.

- 2단계에서 확인한 사실
- 왜 통과를 허용했는가
- 선택 판단에 미치는 영향
- 수용 / 보류 / Monitoring 이관 중 필요한 종결 결과
- 접힌 derived audit와 source / 기준일

별도 체크박스를 남발하지 않는다. 기존 최종 판단 route와 판단 사유에 수용한 한계와 Monitoring 이관 조건을 Python이 요약하고, React는 확인 intent만 전달한다.

## Score Policy

role별 고정 `-6 / -4` 정책은 제거한다.

- `missing_contract`: 점수 없음, 필수 contract이면 Gate blocker
- `resolve_now + open`: 점수 감점 대신 Gate blocker
- `engineering_required + critical`: Gate blocker
- `accepted_limit`: V1에서는 자동 숫자 감점 없음; 근거 신뢰도 영향 label만 표시
- explicit measured observation과 threshold가 있는 경우에만 service가 score impact를 계산
- 동일 `root_issue_id`는 한 번만 반영

숫자보다 먼저 `근거 신뢰도 영향 없음 / 주의 / 선정 차단`의 의미를 정확히 만든다. 향후 수치 calibration은 별도 evidence가 생긴 뒤 수행한다.

## Error Handling

- `actionable_now=true`인데 `action_id` 또는 Python handler가 없으면 contract error로 보고 승격을 막는다.
- required module에 trace adapter가 없으면 `missing_contract`로 차단하고 Final Review에서 `세부 설명 준비 안 됨`을 렌더링하지 않는다.
- action 실행 후 replay / save가 끝나지 않으면 기존 recheck progress guard가 이동을 막는다.
- legacy validation은 삭제하지 않고 recovery-only로 보존한다.
- closure intent의 validation id 또는 root issue id가 현재 confirmed candidate와 다르면 저장하지 않는다.

## Ownership By File

| Boundary | Expected owner |
|---|---|
| closure normalization / root dedup / terminal-state / score impact | 새 pure service `app/services/backtest_evidence_closure.py` |
| data coverage applicability | `app/services/backtest_data_coverage_audit.py` |
| module role / Gate contract | `app/services/backtest_practical_validation_modules.py`, `app/services/backtest_practical_validation_stage_roles.py` |
| Level2 action/progress UI | `app/services/backtest_practical_validation_workspace.py`, `app/web/backtest_practical_validation/page.py` |
| replay date contract | `app/services/backtest_practical_validation_replay.py` |
| GRS strategy runtime | `app/runtime/backtest/runners/global_relative_strength.py`, `finance/sample.py` |
| Final Review Python orchestration | `app/web/backtest_final_review/page.py` |
| Final Review presentation | `app/web/components/final_review_investment_report/frontend/` |

`app/services/backtest_evidence_read_model.py`는 새 closure service를 소비해 Final Review report payload를 조립한다. data coverage audit와 module planner는 원시 evidence를 제공하고 closure service를 역으로 import하지 않는다. 이 단방향 의존성으로 import cycle을 막는다. React가 domain classification을 재계산하는 설계는 허용하지 않는다.

## Proposed Delivery Slices

### 1차: Evidence Truth And Root Dedup

- `latest_replay` trace adapter 연결
- requested / common / actual / gap 설명
- replay와 PIT price root issue 통합
- lifecycle와 survivorship root issue 통합
- `missing_contract` 사용자 노출 차단

### 2차: Level2 Actionability And Gate

- closure contract와 resolution class 도입
- `지금 해결 가능 / 개발 필요 / 한계 인수 가능` 분리
- actual handler가 있는 card만 CTA 제공
- unresolved actionable / critical engineering issue 승격 차단

### 3차: GRS Period And Survivorship Applicability

- source-specific common price / cadence / valuation date 계약
- GRS partial/latest-common 처리 보정
- static manual / dynamic historical universe severity 분리
- current GRS regression fixture 검증

### 4차: Final Review Closure And Score

- `선정 전 미해결`과 `인수한 한계와 최종 판단` 분리
- accepted / monitoring / deferred closure를 판단 사유에 통합
- 고정 감점 제거와 root-level impact 적용
- focused tests, React build, py_compile, Browser QA, docs sync

이 delivery slice는 설계 경계이며, 정확한 함수·테스트·커밋 순서는 사용자 설계 검토 후 `PLAN.md`에서 확정한다.

## Verification Design

- latest replay adapter가 actual stored provenance를 표시하는 service test
- `missing_contract` required item이 Final Review eligibility를 막는 test
- one root issue / one score impact dedup test
- action handler 없는 `resolve_now` item이 CTA를 만들지 않는 test
- unresolved actionable count가 0일 때만 current Final Review eligible이 되는 test
- static manual universe와 dynamic historical universe의 survivorship Gate 차이 test
- current GRS data fixture에서 requested/common/rebalance/valuation date contract test
- decision save가 accepted limits와 monitoring transfers를 같은 validation id로 저장하는 test
- React presentation source/contract test
- Browser QA: Level2 action, development-required state, Final Review closure, stale candidate, compact viewport

## Non-Goals

- historical universe / delisting provider 신규 도입 자체
- 새 DB schema나 별도 workflow-state registry
- registry / saved JSONL 기존 row rewrite 또는 삭제
- Final Review provider fetch 또는 replay 실행
- live approval, broker order, account sync, auto rebalance
- 투자 매력도 최적화나 새 포트폴리오 자동 생성

## Acceptance Criteria

1. current Final Review 후보에는 해결 가능한 Level2 숙제가 남지 않는다.
2. `세부 설명 준비 안 됨`이 current Final Review 사용자 UI에 나타나지 않는다.
3. 실제 action이 없는 항목은 2단계 수집 CTA를 만들지 않는다.
4. 모든 visible Final Review issue가 terminal-state 선택 또는 자동 이관 경로를 가진다.
5. 동일 원인이 module / trace 중복 감점을 만들지 않는다.
6. static / dynamic universe가 서로 다른 survivorship policy를 사용한다.
7. GRS replay 기간 부족이 ticker/date/root cause와 함께 설명된다.
8. Python service boundary와 React presentation-only 경계가 유지된다.

## 2026-07-16 Visual Fidelity Correction

사용자가 웹에서 승인한 A안은 정보 순서만이 아니라 `Workspace > Overview > 시장 맥락`과 같은 시각 언어까지 포함한다. 현재 구현의 각진 녹색 editorial report는 승인안과 다르므로, Python Decision Brief / Gate / persistence 계약은 그대로 두고 React presentation만 교정한다.

### Canonical visual references

- 승인한 A안: 질문 중심 Decision Brief mockup의 둥근 workbench, compact heading, soft neutral panel, 결론 badge, 후보 summary, metric band, progressive disclosure.
- 실행 중 기준 화면: `app/web/streamlit_components/market_context_valuation/src/style.css`와 `MarketContextValuation.tsx`.
- Final Review 고유 정보 구조: 결론 → 행동 근거 → 실제 강점/약점 → trait map → Monitoring 변화 조건 → 최종 판단 → disclosure.

### Exact visual contract

- font stack: `Inter, Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
- primary text `#152033`, secondary text `#647589`, border `#dae4ee`
- outer rhythm: one-column `18px` gap; 12-column editorial grid를 사용하지 않는다.
- question header: `20px` radius, blue-gray/teal light gradient, `22px 24px` desktop padding.
- content section: `20px` radius, white background, `0 10px 30px rgba(33, 53, 72, .055)` shadow.
- inner chart shell: `17px` radius and white-to-cool-neutral gradient.
- metric/observation band: `14px` radius, shared border between cells.
- headline hierarchy: page question `23px`, section heading `20px`, subsection `18px`; 기존 `52px` verdict headline을 사용하지 않는다.
- state colors are restrained teal `#17695e`, orange `#a24d19`, blue-gray `#284e69`; 상태를 얇은 각진 top border로 표현하지 않는다.
- responsive: `760px`에서 header/chart/finding/decision grid를 한 열로 만들고, `460px`에서 padding과 metric grid를 다시 줄인다.

### Ownership and non-goals

- `DecisionBriefWorkspace.tsx`는 approved question-first shell과 candidate intent 배치를 소유한다.
- `DecisionBriefCharts.tsx`는 좌표 계산을 유지하고 chart stroke palette만 Market Context 계열로 맞춘다.
- `style.css`가 visual token과 responsive layout을 소유한다.
- Python projection, route mapping, Gate, evidence classification, persistence, registry는 변경하지 않는다.
- Market Context component 자체를 공용화해 기존 Overview 화면에 회귀 위험을 만들지 않는다. 이번 교정은 Final Review가 canonical token을 소비하는 focused presentation correction이다.

### Visual acceptance

1. 첫 화면에서 질문과 후보 선택이 하나의 rounded gradient header로 읽힌다.
2. verdict는 compact highlighted answer panel이며 거대한 editorial headline이 아니다.
3. chart, metric, finding, monitoring, decision, disclosure가 Market Context의 radius/palette/shadow rhythm을 공유한다.
4. 1440px와 760px Browser QA에서 기준 화면과 나란히 비교하고, 760px document/component horizontal overflow가 0이다.
5. source-contract test가 canonical token, question-first hierarchy, chart palette를 고정해 같은 drift를 다시 허용하지 않는다.

## 2026-07-16 Chart Interaction And Content Polish

사용자가 Market Context visual fidelity 교정 결과를 확인한 뒤, 섹션 제목의 잘못된 가로 정렬, 의미가 부족한 차트 축, hover 부재, observation strip의 빈 면과 긴 값 clipping을 지적했다. 승인안 A는 기존 dependency-free SVG와 Python projection을 유지하면서 React presentation만 보강한다.

### Root cause

- `SectionHeading`은 eyebrow, title, detail을 flex의 세 독립 항목으로 렌더해 한글 제목이 영문 eyebrow 아래가 아니라 가운데 열에 놓인다.
- `SvgLineChart`는 series path와 수평 grid만 그리며 pointer state, X/Y tick label, crosshair, tooltip이 없다. 아래의 start/min-max/end 문자열은 실제 축이 아니다.
- `Underwater drawdown`은 running peak 대비 하락률이지만 제목과 화면 설명이 영문 contract에 머물러 사용자가 의미를 추론해야 한다.
- `.db-observation-strip`은 `auto-fit minmax(180px, 1fr)`와 회색 container background를 함께 사용한다. viewport에 따라 5+1 track이 생겨 마지막 행의 미사용 면이 큰 빈칸처럼 보인다.
- observation value와 comparator는 긴 snake-case token을 줄바꿈하는 규칙이 없어 chart shell의 `overflow: hidden` 경계에서 잘린다.

### Chosen approach A

- chart library를 추가하지 않고 현재 SVG를 확장한다. Market Context의 `pointerIndex`, hover rule, focus dot, inspector pattern을 Final Review에 맞게 재사용한다.
- `SectionHeading`은 eyebrow와 한글 title을 `.db-section-heading-copy`로 묶고, detail만 오른쪽 설명으로 유지한다. 760px 이하에서는 두 묶음을 한 열로 쌓는다.
- `SvgLineChart`는 plot margin을 명시하고 X/Y scale, 5~6개 date tick, 5개 value tick을 그린다. 누적 성과 Y축은 시작값 100의 rebased index, drawdown Y축은 `%` 단위다.
- pointer hover는 가장 가까운 point index를 선택해 vertical crosshair, series별 focus dot, 날짜와 모든 series 값을 담은 tooltip을 표시한다. mouse leave 시 latest point로 돌아가며 keyboard/screen-reader용 chart description과 수치 표 fallback을 유지한다.
- 누적 성과 chart subtitle은 `100은 관측 시작일의 기준값`을 설명한다.
- Underwater 제목은 `고점 대비 낙폭 (Underwater)`으로 바꾸고 `0%는 이전 최고점 회복, 음수는 최고점 대비 하락률`을 설명한다. Python running-peak 계산은 변경하지 않는다.
- observation strip은 desktop 3열, tablet 2열, mobile 1열로 고정한다. container의 미사용 회색 면을 없애고 각 article이 자체 border/background/radius를 가진다.
- observation `strong`, `p`, `small`은 `overflow-wrap: anywhere`와 안전한 `word-break`를 사용해 raw evidence token과 comparator 전체를 표시한다.

### Alternatives rejected

- Recharts 도입은 axis/tooltip 구현을 단순화하지만 새 dependency와 bundle 증가, existing Market Context SVG와의 visual drift를 만든다.
- axis label만 추가하는 최소안은 hover와 point-level 비교 요구를 충족하지 못한다.

### Ownership and safety

- 수정 owner는 `DecisionBriefWorkspace.tsx`, `DecisionBriefCharts.tsx`, `style.css`, tracked Vite build다.
- visual source contract test가 title grouping, hover/axis/tooltip, Korean underwater semantics, observation wrapping/grid를 고정한다.
- Python Decision Brief, exact-common alignment, running-peak drawdown, Gate, route, save, registry, Monitoring snapshot은 변경하지 않는다.
- hover는 read-only presentation state이며 registry append나 Streamlit rerun을 만들지 않는다.

### Acceptance criteria

1. 모든 `SectionHeading`에서 영문 eyebrow 바로 아래에 한글 title이 놓이고 설명은 desktop 오른쪽, narrow viewport 아래에 배치된다.
2. 누적 성과 chart는 5~6개 X date tick, 5개 rebased-index Y tick, hover 날짜와 후보/Benchmark 값을 제공한다.
3. 고점 대비 낙폭 chart는 의미 설명, percent Y tick, hover 날짜/낙폭 값을 제공한다.
4. observation 6개는 desktop 3×2, 760px 2×3, 460px 1×6으로 배치되고 큰 빈 회색 면이 없다.
5. `weak_source_or_proxy_liquidity_evidence`와 `official_fresh_capacity_evidence` 같은 긴 값이 잘리지 않고 여러 줄로 표시된다.
6. 기존 수치 표, SVG 접근성 label, chart series 계산, Python/data contract가 유지된다.

## 2026-07-16 Portfolio Character Profile And Review Pressure Separation

사용자가 `포트폴리오 성격 지도`에서 실제 포트폴리오 특성이 보이기를 원한다. 현재 radar는 이름과 달리 `측정값 ÷ review threshold`를 0~100 pressure로 정규화한 화면이다. 값이 저장돼 있어도 threshold가 없으면 `미측정`이 되므로, 실제 성격과 관리 기준 대비 압력을 서로 다른 contract와 UI로 분리한다.

### 이걸 하는 이유?

current GRS 화면에는 다음 값이 이미 존재한다.

- 최대 구성 비중 `100.00%`
- 최대 underwater 낙폭 `-12.43%`
- 평균 회전율 `3.20%`
- 거래비용 가정 `10.00 bps`

하지만 current trait map은 집중 위험만 `83.3 / 100`으로 그리고 나머지를 `미측정`으로 표시한다. 이는 raw measurement 부재만의 문제가 아니다.

- 집중 위험은 `max_weight=100`과 `max_weight_review=60`이 모두 있어 pressure를 계산한다.
- 낙폭은 curve에서 `-12.43%`를 측정했고 profile에 `mdd_review_line=-15`가 있지만 projector가 `max_drawdown_review_pct`만 찾아 threshold를 연결하지 못한다.
- 회전율은 `avg_turnover=0.032`가 있으나 명시적 review threshold가 없다.
- 비용은 `transaction_cost_bps=10`과 curve 적용 증명이 있으나 `one_way_cost_bps=10`은 비용 가정 자체이지 허용 한도가 아니므로 review threshold로 재사용할 수 없다.
- 국면 의존은 현재 structured measurement와 comparator가 없다.

`미측정` 하나로 이 원인을 합치면 사용자는 값이 없는지, 기준만 없는지, 제품 adapter가 끊겼는지 구분할 수 없다. 또한 `83.3 / 100`은 투자 품질 점수처럼 보이지만 실제로는 threshold가 50 지점이 되도록 변환한 pressure 표현이다.

### Considered approaches

#### A. Threshold-only radar 유지

- 장점: 현재 계산과 UI 변경이 작다.
- 단점: threshold가 없는 실제 관측값을 계속 숨기며, 한 축만 있는 radar가 포트폴리오 성격을 설명하지 못한다.
- 결정: 채택하지 않는다.

#### B. Raw 값을 임의 0~100 점수로 환산

- 장점: 모든 축을 radar polygon으로 그릴 수 있다.
- 단점: %, bps, 낙폭, regime 값을 근거 없는 공통 범위로 변환해 가짜 비교와 종합점수를 만든다.
- 결정: 채택하지 않는다.

#### C. Actual Character + Review Pressure 분리

- 실제 관측값은 threshold 유무와 관계없이 `포트폴리오 실제 성격`에 표시한다.
- 명시적 review criterion이 있는 항목만 `관리 기준 대비 압력`에서 비교한다.
- raw 값이 없을 때만 `분석 근거 없음`, 값은 있으나 criterion이 없으면 `기준 미설정`으로 표시한다.
- 결정: 사용자 승인으로 채택한다.

### Product meaning

첫 영역의 질문은 `이 포트폴리오는 실제로 어떤 특성을 보였는가?`다. 두 번째 영역의 질문은 `그 특성이 저장된 관리 기준을 넘었는가?`다.

`포트폴리오 실제 성격`은 좋고 나쁨을 임의로 판정하지 않는다. 측정값, 단위, 관측 의미, 기준일, source를 보여준다. `관리 기준 대비 압력`만 explicit comparator에 따라 `기준 이내 / 기준 초과 / 기준 미설정 / 분석 근거 없음`을 표시한다.

### Python contract

`app/services/backtest_final_review_decision_brief.py`가 기존 structured execution observation을 한 번 만들고, 같은 observation에서 두 projection을 파생한다. React는 raw validation이나 threshold key를 읽지 않는다.

```text
character_profile.items[]
  axis_id
  label
  measurement_status = observed | evidence_missing
  measured_value
  display_value
  unit
  interpretation
  evidence_refs[]
  as_of

review_pressure.items[]
  axis_id
  label
  status = within_limit | exceeds_limit | criterion_missing | evidence_missing
  measured_value
  display_value
  criterion_value
  criterion_display
  comparison
  delta_value
  delta_display
  ratio_to_criterion
  summary
  evidence_refs[]
  as_of
```

`aggregate_score`, role별 고정 점수, 임의 normalization은 만들지 않는다. `ratio_to_criterion`은 비교 설명을 위한 실제 비율이며 0~100 품질 점수가 아니다.

`less_or_equal` risk criterion은 measurement와 criterion의 절댓값 크기로 비교한다. `delta_value = abs(measured) - abs(criterion)`이며 양수는 초과, 0 이하는 기준 이내 buffer다. 사용자 화면은 원래 부호와 단위를 보존해 concentration은 `%p`, drawdown은 signed `%`, cost는 `bps`로 설명한다. `ratio_to_criterion`은 cap하지 않는다.

### Canonical measurement and criterion mapping

| Axis | Measurement | Criterion | Current behavior |
|---|---|---|---|
| `concentration` | `metrics.max_weight` | `max_weight_review` | 실제 값과 `기준 60% 대비 +40%p 초과` 표시 |
| `drawdown` | running-peak underwater의 minimum | `max_drawdown_review_pct` 또는 canonical alias `mdd_review_line` | signed display `-12.43%`; magnitude로 `-15% 관리선 이내 2.57%p` 비교 |
| `turnover` | turnover evidence contract의 `avg_turnover` | `avg_turnover_review` 또는 `turnover_review` | raw `3.20%` 표시; criterion 없으면 `기준 미설정` |
| `cost` | cost contract의 `transaction_cost_bps` | `transaction_cost_bps_review` | raw `10bps`와 curve 적용 상태 표시; `one_way_cost_bps`를 허용 기준으로 사용하지 않음 |
| `regime_dependency` | explicit regime dispersion/dependency observation | 해당 observation의 explicit comparator | current source가 없으면 `분석 근거 없음`; prose나 가짜 0으로 채우지 않음 |

threshold alias 정규화는 Python service가 소유한다. `mdd_review_line`은 명백한 drawdown review line이므로 canonical drawdown criterion으로 연결한다. contract alias 누락을 사용자에게 `기준 연결 필요`로 노출하지 않는다. 필수 alias가 다시 끊기면 source-contract test가 실패해야 한다.

### UI structure

기존 `포트폴리오 성격 지도` section을 다음 한 section 안의 두 계층으로 교체한다.

1. `포트폴리오 실제 성격`
   - 5개 trait row/card를 사용한다.
   - 각 row는 한국어 label, 큰 raw value, 한 줄 의미, 기준일을 보여준다.
   - threshold가 없어도 observed value는 항상 노출한다.
   - 국면 의존처럼 measurement가 없을 때만 `분석 근거 없음` empty state를 사용한다.
2. `관리 기준 대비 압력`
   - radar polygon과 `83.3 / 100` 표현을 제거한다.
   - 각 항목을 horizontal comparison row로 표시한다.
   - criterion이 있으면 actual, criterion, 차이와 `기준 이내 / 초과`를 표시한다.
   - criterion이 없으면 actual을 반복하지 않고 `기준 미설정`과 그 의미만 표시한다.

desktop에서는 실제 성격과 관리 압력을 2열로 배치하고, 760px 이하에서는 실제 성격 다음에 관리 압력을 한 열로 쌓는다. `Workspace > Overview > 시장 맥락`의 blue-gray palette, rounded surface, soft shadow, compact typography를 유지한다.

### User reading flow

```text
행동 차트와 관측값
  -> 포트폴리오 실제 성격에서 raw 특성 확인
  -> 관리 기준 대비 압력에서 초과/이내/기준 미설정 확인
  -> 실제 강점과 약점
  -> Monitoring 변화 조건
  -> 최종 판단
```

성격 section은 Final Review에서 새 remediation을 수행하지 않는다. criterion이 없다는 사실은 Level2 action으로 자동 승격하지 않으며, selected-route Gate도 이 presentation만으로 변경하지 않는다.

### Fallback and compatibility

- Streamlit fallback도 radar text list 대신 같은 `실제 성격 / 관리 기준 대비 압력` 순서를 사용한다.
- current `decision_brief_v1`의 `trait_map`은 current React와 fallback consumer를 함께 전환한 뒤 제거한다. stored final-decision snapshot에는 chart/trait bulk가 저장되지 않으므로 기존 JSONL row rewrite는 필요하지 않다.
- legacy report compatibility service, score, route, closure snapshot, Monitoring snapshot은 변경하지 않는다.
- Python observation은 한 번만 만들고 character/review projection이 같은 `axis_id`와 evidence ref를 공유해 중복 근거를 만들지 않는다.

### Error and empty-state policy

- measurement가 없으면 `분석 근거 없음`과 필요한 근거 종류를 표시한다.
- measurement는 있으나 criterion이 없으면 `기준 미설정`으로 표시하며 `미측정`이라고 부르지 않는다.
- measurement와 criterion이 있으면 comparison을 반드시 계산한다. 계산 불가능한 단위/비교 방향이면 contract error로 test에서 차단한다.
- `mdd_review_line` alias처럼 known criterion이 연결되지 않는 상태는 사용자 empty state가 아니라 product contract regression이다.
- UI는 provider fetch, replay, DB ingestion, threshold 저장을 실행하지 않는다.

### Ownership by file

| Responsibility | Owner |
|---|---|
| character/review projection, drawdown alias, comparison/delta | `app/services/backtest_final_review_decision_brief.py` |
| current fallback rendering | `app/web/backtest_final_review/page.py` |
| TypeScript payload contract | `frontend/src/decisionBriefTypes.ts` |
| section orchestration | `frontend/src/DecisionBriefWorkspace.tsx` |
| actual character and review pressure presentation | 새 focused owner `frontend/src/DecisionBriefCharacter.tsx`; 기존 radar code는 `DecisionBriefCharts.tsx`에서 제거 |
| responsive visual contract | `frontend/src/style.css` |
| Python/service/source contract tests | `tests/test_backtest_final_review_decision_brief.py`, `tests/test_service_contracts.py`, `tests/test_final_review_market_context_visual_contract.py` |

### Delivery slices

1. **Character contract**: RED tests, `character_profile` / `review_pressure`, drawdown threshold alias, removal of aggregate 0~100 pressure score.
2. **Decision Workspace presentation**: radar를 actual character rows와 review comparison rows로 교체하고 fallback을 동기화한다.
3. **QA and docs**: current GRS fixture regression, production build, desktop/760px Browser QA, durable flow/active task/root handoff sync.

### Verification design

- current GRS fixture에서 concentration, drawdown, turnover, cost가 `observed`이고 regime만 `evidence_missing`인 service test
- drawdown `mdd_review_line=-15`가 `-12.43%` observation과 연결돼 `within_limit`이 되는 alias regression test
- turnover/cost raw value는 보이지만 criterion이 없을 때 `criterion_missing`인 test
- `one_way_cost_bps`가 cost review limit으로 오용되지 않는 test
- aggregate score와 arbitrary normalized value가 payload/UI에 없는 contract test
- current React가 radar/`미측정` 통합 label을 렌더하지 않고 실제 성격/관리 압력 순서를 유지하는 source contract test
- Streamlit fallback parity test
- Vite production build, target `py_compile`, `git diff --check`
- Browser QA desktop/760px: raw value visibility, drawdown 기준 연결, criterion/evidence 상태 구분, no horizontal overflow, Final Review save CTA 미실행

### Non-goals

- 새 regime provider 또는 historical regime analytics 구현
- turnover/cost 허용 기준을 임의 기본값으로 추가
- raw units를 공통 0~100 성격 점수로 변환
- overall investment score 또는 radar aggregate 재도입
- Final Review에서 validation profile을 편집하거나 저장
- registry / saved JSONL 기존 row rewrite
- Gate, canonical route, broker/live approval/auto rebalance 변경

### Acceptance criteria

1. current GRS에서 집중도, 낙폭, 회전율, 비용의 실제 값이 criterion 유무와 관계없이 보인다.
2. 국면 의존만 현재 structured evidence 부재로 `분석 근거 없음`을 표시한다.
3. 낙폭 `mdd_review_line`이 canonical criterion으로 연결되고 `-12.43% / 관리선 -15% / 기준 이내`가 함께 읽힌다.
4. 회전율과 비용은 `미측정`이 아니라 `기준 미설정`으로 구분된다.
5. `83.3 / 100` 같은 임의 pressure score와 한 축 radar polygon이 current UI에서 제거된다.
6. actual character와 review pressure는 같은 Python observation/evidence ref를 사용하고 React가 계산하지 않는다.
7. Gate, route, persistence, Monitoring snapshot, protected registry는 변경되지 않는다.
8. desktop과 760px에서 실제 성격 → 관리 압력 → 강점/약점 흐름과 가로 overflow 0을 확인한다.

### Design self-review

- [x] `TBD`, `TODO`, placeholder 또는 구체화되지 않은 소유 파일이 없다.
- [x] raw character와 criterion-based pressure가 서로 다른 사용자 질문과 payload로 분리돼 있다.
- [x] drawdown의 signed display, magnitude comparison, delta 방향이 일관된다.
- [x] turnover/cost criterion을 임의 생성하지 않고 regime provider 도입도 범위 밖으로 고정했다.
- [x] current React와 Streamlit fallback을 함께 전환하고 기존 JSONL row를 rewrite하지 않는다.
- [x] Python projection owner / React presentation-only / Gate·route·persistence 불변 경계가 명확하다.
- [x] 3개 delivery slice와 RED contract, build, desktop/760px QA 완료 조건이 연결된다.
