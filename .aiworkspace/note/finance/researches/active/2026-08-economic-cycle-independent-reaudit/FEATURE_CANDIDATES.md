# Feature Candidates

Date: 2026-08-03
Status: not approved

## A. Current Model Repair

- h0를 deterministic quadrant로 바꾼다.
- h0 coverage와 +2M transition prior를 수정한다.
- 1·2개월 확률과 기존 화면은 유지한다.

장점: 변경량이 작다.

한계: 미래 확률의 표본·baseline 문제와 사용자의 목적 불일치를 남긴다.

## B. Observed State + Transition Monitor

- 현재 국면을 actual level / momentum / breadth / duration으로 판정한다.
- 1·2개월 확률 대신 `유지`, `전환 감시`, `전환 확인` 상태를 둔다.
- 최근 1 / 3 / 6개월의 실물, 노동, 금융선행, 물가정책 변화를 설명한다.
- 다음 인접 국면은 조건부 경로로만 제시하고 충족 조건과 반증 조건을 함께 표시한다.
- graph는 실제 과거 score와 현재점만 그리고 미래 terminal point는 제거한다.

장점: 사용자가 현재 상태와 다음에 확인할 것을 바로 이해한다.

한계: hysteresis, breadth와 transition condition을 새 validation contract로 만들어야 한다.

## C. Dynamic-Factor / Markov-Switching Nowcast

- mixed-frequency current activity latent state를 추정한다.
- 전환 확률은 shadow validation을 통과할 때만 보조 근거로 공개한다.

장점: current nowcast와 missing / irregular release를 통계적으로 처리할 수 있다.

한계: 구현·검증 비용이 크고, 바로 probability-first UI로 돌아갈 위험이 있다.

## Recommended Sequence

B를 제품 계약으로 먼저 구현하고 C는 shadow research로 분리한다. A는 B로 가기 전
긴급 일관성 fix가 필요할 때만 제한적으로 사용한다.
