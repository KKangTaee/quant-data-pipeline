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

- Final Review의 latest-per-source selector가 고른 최신 eligible GRS-shaped row는 `validation_selection_rebuilt_grs_macro_top1_ma200_aef1f226_d289e7e8`이며, `ready_with_handoff`, resolve-now 0, critical engineering 0, missing contract 0, accepted limit 6, final decision 1이었다.
- 직전 `7bca4e1a` row의 accepted limit 5건과 달리 2026-07-16 observation refresh row에는 historical universe accepted limit가 포함된다. append-only registry를 재작성하지 않고 최신 row를 read-only로 투영했다.
