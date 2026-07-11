# Notes

- Market Movers 상단은 page header이므로 내부 section header와 동일하게 만들지 않는다.
- Ranking Board는 이미 `kicker / title / detail / count badge` 구조에 가까워 이번 변경의 기준으로 삼는다.
- 섹터 영역의 외부 divider와 내부 `시장 확산 지도`는 중복 계층이다. 하나의 section header로 합친다.
- 섹터 분석 headline은 고정된 화면 제목이 아니라 현재 데이터가 만든 결과이므로 section title 아래 결과 요약으로 분리했다.
- 상태 tone은 badge/rail/sector lane에 남기고, section kicker/title은 Ranking Board와 유사한 고정 정보 계층을 사용한다.
- 후속 보더 통일에서는 section outer boundary도 Ranking Board와 같은 top/bottom-only contract로 맞췄다. Sector 상태 tone은 badge, participation rail, lane/card 색상으로 충분히 유지되므로 별도 왼쪽 rail을 두지 않는다.
- Ranking Board의 Top 5 박스 배경은 요약 항목의 상승/하락 방향을 빠르게 구분하기 위한 4% tone tint다. 하단 목록도 같은 `--ov-row-tone` 4% tint를 적용해 색상 범위가 중간에서 끊겨 보이지 않게 했고, 맨 아래 안전 안내 박스는 의미가 다른 중립 배경으로 유지했다.
