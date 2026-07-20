# Portfolio Monitoring Diagnosis Grouping / Scroll V1 Risks

- 그룹 대표값만 보이면 개별 근거가 사라진 것처럼 보일 수 있으므로 member evidence를 disclosure에 모두 보존한다.
- mobile 내부 스크롤은 page scroll과 충돌할 수 있어 760px 이하에서는 높이 제한을 해제한다.
- display grouping이 raw history identity를 바꾸지 않도록 persistence input은 기존 `all_rows`를 유지한다.
