# Notes

- 기존 Evidence `direction`은 전월 대비 변화량이 아니라 expanding robust scale 점수의 ±0.15 구간이다.
- 따라서 실물 factor는 과거 기준 대비 수준, 전망 factor는 경기 전망에 주는 지원·부담으로 번역했다.
- 금융·선행 여건과 물가·정책 압력이 모두 양수여도 각각 `전망 지원`과 `전망 부담`으로 다르게 표시한다.
- 자산 카드의 `economic_state.summary`도 같은 네 factor를 사용하므로 `현재 수준 / 전망 여건`으로 분리했다.
- `observations[*].direction` enum은 호환성을 위해 유지하고, React 자산 카드 배지는 Evidence helper를 재사용해 역할별 문구로 표시한다.
