# Practical Validation Flow Gating / Evidence IA V1 Notes

## Initial Findings

- `render_practical_validation_workspace` currently builds `validation_result` after Flow 2 and renders Flow 3 / Flow 4 / Flow 5 unconditionally.
- Data collection can resolve only part of Data Coverage / Conditional Evidence gaps: provider snapshot, holdings / exposure, macro context, and DB price window. Replay, method strength, component role / weight, and Final Review judgment should not get a collection button.
- Existing lower evidence tabs duplicate Flow 4 criteria detail and should become a supporting evidence appendix rather than the primary reading path.

## 2차 Decision

- Criteria card 내부의 `수집하기`는 Flow 4 Provider / Data 보강 액션 영역으로 이동하는 CTA다. 실제 Streamlit 실행 버튼은 기존 Provider Action Center가 소유한다.
- Data Coverage / Construction Risk는 non-PASS evidence row가 provider / holdings / exposure / macro 계열일 때만 collection CTA를 노출한다. Method strength, replay, role / weight, Final Review 판단 항목에는 collection CTA를 붙이지 않는다.

## 3차 Decision

- Stage ownership inventory는 검증을 새로 실행하거나 gate를 바꾸지 않는다. 현재 `validation_modules`의 `stage_owner`, `requirement`, `status`, `resolution_surface`를 화면에서 확인 가능한 read model로 정리한다.
- 후속 단계 소유 기준은 `후속 단계 판단`으로 표시하고, Practical Validation 보강 항목으로 반복 노출하지 않는 경계를 유지한다.
