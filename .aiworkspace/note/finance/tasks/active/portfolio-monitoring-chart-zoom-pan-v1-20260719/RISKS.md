# Risks

- wheel event의 page scroll 차단 범위를 chart hit area로만 제한해야 한다.
- hover와 drag threshold를 분리하지 않으면 클릭 또는 tooltip 사용이 pan으로 오인될 수 있다.
- mobile touch gesture는 V1에서 제외하므로 버튼 controls의 크기와 접근성이 충분해야 한다.
- visible-only Y축은 확대 구간의 변화폭을 강조하므로 현재 날짜 범위를 항상 표시해야 한다.
