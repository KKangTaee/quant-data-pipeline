# Status

## 2026-07-03

- V7 완료: Policy Signal 분류 read-model `build_policy_signal_inventory`를 추가하고 blocker / review / context row contract를 테스트했다.
- V8 완료: `can_move_to_compare` strict 판단은 보존하고, 2차 Practical Validation source 등록용 `can_enter_practical_validation`을 분리했다. `hold`, liquidity / ETF / validation policy caution은 조건부 review로 낮추고, promotion missing / benchmark missing / price hard error는 source blocker로 유지한다.
- V9 완료: `검증 신호 · Policy Signals` active render path를 compact evidence 화면으로 바꿨다. nested `현재 판단 / 검토 근거 / 실행 부담 / 기술 상세` 탭은 active 함수에서 제거하고, summary / policy rows / Practical Validation review rows / 접힌 상세 근거로 정리했다.
- V10 완료: Candidate Review draft의 handoff snapshot을 `practical_validation_entry_gate_v2`로 올리고, Practical Validation source / component replay contract에 `entry_gate` 요약과 review focus row를 보존했다.
- 다음: V11에서 durable docs, root handoff log, 최종 QA / Browser smoke를 정리한다.
