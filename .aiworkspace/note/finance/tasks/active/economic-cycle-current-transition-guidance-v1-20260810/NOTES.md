# Notes

- 실제 payload: observed `contraction`, anchor `recovery`, target `expansion`, non-adjacent true.
- route map은 `contraction → recovery`지만 transition panel은 `recovery → expansion`을 보여주는 presentation mismatch가 원인이다.
- persisted state machine은 보존하고 Overview service에서 사용자용 current transition을 파생한다.
- 사용자용 `current_transition`은 항상 정식 월말 observed phase에서 시작하고, 순환 순서상 다음 인접 국면을 확인 대상으로 둔다.
- 실제 2026-07-31 read model은 `contraction → recovery`, 조건 `0/3`, 실제값 `-0.16/-0.24`, 확산 `4/8·50%`, 활동/고용 `-0.12/-0.20`으로 확인됐다.
- 기존 anchor/target은 state machine 호환을 위해 보존하되 UI에서는 `이전 모델 기준 · 보조 정보`로만 표시한다.
- 월중 좌표는 잠정 맥락이며 정식 월말 국면을 덮어쓰지 않는다.
- 순환 경로 지도도 persisted monitor가 아니라 사용자용 `current_transition`을 우선 사용한다.
- persisted monitor의 context는 legacy target 기준이므로 current target과 다를 때 `이전 모델 기준 · 보조 정보` 내부에서만 표시한다.
- diffusion은 비교 가능한 지표가 6개 미만이면 60% 계산값보다 최소 커버리지 부족을 우선 설명한다.
