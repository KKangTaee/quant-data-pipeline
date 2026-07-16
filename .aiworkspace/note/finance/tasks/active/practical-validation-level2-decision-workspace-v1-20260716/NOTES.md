# Notes

## 2026-07-16 Diagnosis

- Practical Validation focused closure / boundary / workspace tests 66개는 통과했다. 현재 문제는 기능 장애보다 제품 projection과 UI 구조다.
- actual page는 Flow 1~4를 렌더링하고 저장 / Final Review 이동은 Flow 3에 포함한다. architecture 일부 문서는 5-flow로 기록해 drift가 있다.
- 설계 진단 당시 확인한 saved GRS-shaped row는 replay PASS, unresolved actionable 0, critical engineering 0, accepted limit 6, final decision 1이었다. 구현 중간에 확인한 2026-07-12 row는 accepted limit 5건이었고, current latest-per-source projection은 아래 Runtime Observation의 2026-07-16 row를 따른다.
- current Flow 3은 accepted limit count만 compact하게 보여주고 final decision item은 같은 summary에서 분리하지 않는다.
- `practical_validation_fix_queue`와 `practical_validation_data_action_board`는 별도 iframe이고, 둘 다 square / no-shadow visual contract를 사용한다.
- action board summary가 0건이어도 empty groups를 렌더링한다.
- closure root dedup은 Final Review에 적용됐지만 Level2 category card는 module / audit 기준이라 같은 원인이 반복될 수 있다.
- current saved GRS-shaped Validation Efficacy는 `walk-forward REVIEW / OOS PASS / regime PASS` 실제 audit row를 갖고 있지만 module-level first-read는 이를 generic 방법론 주의 문구로 축약한다.

## 2026-07-16 Design Decision

- visible user flow는 4단계로 고정한다.
- `검증 기준 상세`는 별도 flow가 아니라 Step 3 disclosure다.
- 새 pure Decision Workspace read model이 finding_kind, user-action count, lane, category disclosure를 소유한다.
- 새 React one-shell은 Final Review visual token을 재사용하지만 domain classification을 재계산하지 않는다.
- custom profile과 raw evidence의 full React migration은 범위에서 제외한다.
- read model은 audit PASS row를 `verified`, explicit observation + comparator가 있는 non-blocker만 `measured_caution`으로 투영하고, 같은 root가 handoff lane에 다시 나타나지 않게 한다.
- normalized category evidence는 React disclosure에 두고 custom profile, advanced replay, full raw evidence는 secondary Streamlit disclosure에 유지한다.

## 2026-07-16 Implementation

- single-component 100% weight는 mix concentration이 아니므로 `NOT_APPLICABLE`로 투영한다.
- evidence closure는 resolution class별 count를 제공하고, registered callable handler가 있는 action만 `resolve_now`로 유지한다.
- `app/services/backtest_practical_validation_decision_workspace.py`가 `source_required / replay_required / resolution_required / ready_with_handoff / ready` state와 top-level `validation_result_id`를 제공한다.
- 실제 계산된 audit PASS는 verified로, explicit observation과 threshold/comparator가 모두 있는 non-blocker만 measured caution으로 분리한다.
- accepted limit / final decision / monitoring transfer는 Level2 수리 lane이 아니라 Final Review handoff lane이다.
- React는 six intents만 반환하고 Python이 classification / applicability / root dedup / Gate / handler validation / replay / persistence를 소유한다.
- validation builder가 rerun마다 UUID를 새로 생성하므로 동일 replay/profile의 result를 Python session에서 재사용해 stale intent 오판을 막았다.
- active first-read는 새 one-shell 하나만 렌더링한다. legacy Fix Queue / Data Action Board는 compatibility code로 남지만 active path에서 사용하지 않는다.
- new component build는 root `build/` ignore 규칙에 걸리므로 clean checkout에서도 React가 활성화되도록 build index/assets를 명시적으로 force-stage했다.

## 2026-07-16 Runtime Observation

- 초기 계약으로 Final Review의 latest-per-source selector가 고른 최신 eligible GRS-shaped row는 `validation_selection_rebuilt_grs_macro_top1_ma200_aef1f226_d289e7e8`이며, `ready_with_handoff`, resolve-now 0, critical engineering 0, missing contract 0, accepted limit 6, final decision 1이었다.
- 직전 `7bca4e1a` row의 accepted limit 5건과 달리 2026-07-16 observation refresh row에는 historical universe accepted limit가 포함된다. append-only registry를 재작성하지 않고 최신 row를 read-only로 투영했다.

## 2026-07-16 User Feedback Correction

- 후보 카드와 검증 profile이 같은 grid / card 문법을 사용해 profile이 포트폴리오
  설계안처럼 읽혔다. 두 선택을 1A / 1B subsection으로 분리한다.
- React component intent 뒤 Python이 replay를 실행하고 다시 full `st.rerun()`을
  호출해 전체 탭 reset처럼 보였다. one-shell을 fragment boundary로 격리한다.
- decision workspace가 raw `Criteria`, `Evidence`, `Current`를 그대로 표시해
  함수 경로와 `key=value`가 사용자 설명으로 노출됐다.
- `backtest_practical_validation_stage_roles.py`는 `pv_data_caution`과
  `pv_practical_caution`을 Practical Validation 소유로 선언하지만,
  `_generic_module_issue()`는 이 role을 모두 `accepted_limit / final_review`로
  fallback했다. 이 stage-ownership 불일치가 current GRS handoff 6건의 핵심
  regression 원인이다.
- 승인된 보정은 evidence가 있는 caution을 Level2 `validated_caution`으로
  종결하고, evidence가 없는 required validation은 engineering blocker로
  유지한다. explicit applicability가 있는 구조적 한계와 실제 사용자 판단만
  Final Review로 넘긴다.

## 2026-07-16 Correction Runtime Result

- 최신 GRS row를 현재 module / enrichment / closure / decision-workspace
  계약으로 read-only 재투영한 결과는 `ready_with_handoff`다.
- verified 22, validated caution 5, resolve-now 0, engineering blocker 0,
  missing contract 0이며 provider enrichment action도 0건이다.
- Final Review handoff는 `historical_universe_coverage / accepted_limit`과
  `tax_account_scope / final_decision` 두 root만 남는다.
- 실제 projection에서 summary에는 handoff 2건이 있지만 lane이 비는 회귀를
  발견했다. 원인은 measurement가 있는 모든 non-blocker를
  `measured_caution`으로 덮어쓴 것이었다.
- measured caution은 `validated_caution`에만 적용하고 accepted limit /
  final decision / monitoring transfer는 measurement가 있어도 원래
  handoff class를 유지하도록 TDD로 보정했다.

## 2026-07-16 Action Lifecycle Follow-up

- 선택 후보를 후보 grid 바로 아래에 다시 크게 표시하면 후보 선택과 검증 관점
  사이에 불필요한 중복 context가 생긴다. 현재 선택은 one-shell header의
  `검증 대상` context로 이동했다.
- 5개 검증 관점은 4 + 1보다 3 + 가운데 정렬 2가 데스크톱 카드 밀도와
  선택 관계를 더 안정적으로 보여준다. 760px에서는 기존처럼 1열이다.
- 지정 후보에서 2026-07-16 provider gap action 실행 이력이 실제로 있었지만,
  source-map 탐색 실패와 미지원 `ishares_workbook` parser가 다시 callable
  action으로 분류됐다. 사용자가 클릭하지 않은 것이 아니라 action lifecycle
  판정 버그였다.
- provider 보강과 replay는 독립 병렬 action이 아니다. provider 결과는 기존
  replay / decision cache를 무효화하고, 다음 단계 replay가 새 DB 근거로
  validation을 다시 계산해야 한다.
- 공식 source 탐색을 이미 시도했지만 계약이 없거나 parser가 현재 수집기에서
  지원되지 않으면 `resolve_now`를 반복하지 않고 `engineering_required`로
  전환한다. 아직 `candidate` 상태라 검증하지 않은 source는 최초 discovery
  action을 유지한다.
- discovery job 예외 결과에도 요청 symbol을 run metadata에 남겨 다음 read
  model이 같은 CTA를 다시 만들지 않게 한다.
- partial-month Monitoring은 날짜 필드 존재만으로 인정하지 않는다. 요청 월의
  평가일, 바로 이전 월의 완결 리밸런싱과 동일한 실제 결과일, 월말 7일 이내
  공통 가격일, 31일 이내 gap이 함께 맞을 때만 종결한다. 장기 또는 모순된
  gap은 engineering blocker다.
- provider 계약은 target data-kind별로 판단한다. holdings 누락을 operability
  계약만으로 개발 필요 처리하지 않으며, 동일 symbol/data-kind의 candidate와
  failed row 순서가 달라도 terminal 상태를 우선한다.
- 동일 symbol/data-kind에 verified holdings 계약이 여러 개면 현재 자동
  수집기가 지원하는 parser를 우선해, row 정렬 순서 때문에 실행 가능한
  계약을 engineering blocker로 낮추지 않는다.
- 지정 후보의 actual replay는 전체 PASS이며 period coverage도 PASS다.
  최신 시장 요청일은 2026-07-15, 공통 가격일은 2026-06-26, 마지막 완결
  리밸런싱은 2026-06-30, 최신 평가는 2026-07-06이고 제한 종목은
  COMT / TIP / XLE다.
- 현재 자동 수집기로 해결할 수 없는 holdings/exposure 계약은
  COMT / EFA / IWD / IWM / IWN / LQD / TIP / VNQ 8종이다.
