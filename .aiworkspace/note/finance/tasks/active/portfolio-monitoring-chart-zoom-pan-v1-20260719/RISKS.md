# Risks

- wheel event의 page scroll 차단 범위를 chart hit area로만 제한해야 한다.
- hover와 drag threshold를 분리하지 않으면 클릭 또는 tooltip 사용이 pan으로 오인될 수 있다.
- mobile touch gesture는 V1에서 제외하므로 버튼 controls의 크기와 접근성이 충분해야 한다.
- visible-only Y축은 확대 구간의 변화폭을 강조하므로 현재 날짜 범위를 항상 표시해야 한다.
- 실제 browser에서 trackpad wheel 빈도, pointer capture 종료, line/candle viewport 유지와 420px control wrapping은 자동 DOM 접근 차단으로 아직 확인하지 못했다.
- Browser QA가 끝나기 전에는 전체 roadmap 3/3 완료로 올리지 않는다. 사용자가 실제 화면에서 검증하거나 browser security policy가 허용될 때 closeout한다.
- 35:65 CSS와 11px axis contract는 자동 검증했지만 실제 desktop 목록 최소 폭, 900px 단일 열, 420px axis clipping/overflow는 Browser policy 때문에 관찰하지 못했다.
