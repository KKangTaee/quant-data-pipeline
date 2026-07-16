# Notes

## 2026-07-16 Diagnosis

- Practical Validation focused closure / boundary / workspace tests 66개는 통과했다. 현재 문제는 기능 장애보다 제품 projection과 UI 구조다.
- actual page는 Flow 1~4를 렌더링하고 저장 / Final Review 이동은 Flow 3에 포함한다. architecture 일부 문서는 5-flow로 기록해 drift가 있다.
- current GRS는 replay PASS, unresolved actionable 0, critical engineering 0, accepted limit 6, final decision 1이다.
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
