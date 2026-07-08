# Notes

- UI는 provider/DB를 직접 fetch하지 않는다. 조사 snapshot 서비스와 helper model이 만든 payload만 렌더링한다.
- 기존 `PER / EPS`, `당기순이익` 표 렌더링 테스트는 유지해야 한다.
- 유동비율은 `current_assets / current_liabilities`, FCF는 statement shadow / legacy financial row의 `free_cash_flow`를 사용한다.
- trend chart는 최근 최대 8개 statement row를 period_end / available_at 기준으로 정렬해 보여준다.
- 2026-07-08 후속 2: 연간 / 분기를 한 차트에 섞지 않는다. 연간값과 분기값은 스케일이 달라 PER / EPS / 당기순이익 / FCF 해석이 왜곡될 수 있으므로, 같은 지표 탭 안에 `연간`과 `분기` 차트를 위아래로 동시에 둔다.
- 막대 폭은 화면 너비를 채우지 않도록 고정 컬럼 폭 / 고정 bar width로 둔다. 긴 series는 각 그래프 내부 horizontal scroll로 확인한다.
- 2026-07-08 후속 3: 값은 막대 위 annotation으로 두지 않는다. 좁은 column에서 막대 / 숫자 / 기간 라벨이 겹치므로 `막대 -> 기간 -> 값` 순서로 고정 caption을 둔다. 상세 회계기간 / 공시일은 title / aria label로 남긴다.
- 2026-07-08 후속 4: 연간과 분기를 같은 축에 합치지 않고 같은 row의 좌우 패널로 둔다. 각 패널은 독립 y-scale을 유지하고, 막대 top을 SVG line overlay로 연결해 같은 series 안의 흐름만 보여준다.
