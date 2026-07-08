# Notes

- UI는 provider/DB를 직접 fetch하지 않는다. 조사 snapshot 서비스와 helper model이 만든 payload만 렌더링한다.
- 기존 `PER / EPS`, `당기순이익` 표 렌더링 테스트는 유지해야 한다.
- 유동비율은 `current_assets / current_liabilities`, FCF는 statement shadow / legacy financial row의 `free_cash_flow`를 사용한다.
- trend chart는 최근 최대 8개 statement row를 period_end / available_at 기준으로 정렬해 보여준다.
- 2026-07-08 후속 2: 연간 / 분기를 한 차트에 섞지 않는다. 연간값과 분기값은 스케일이 달라 PER / EPS / 당기순이익 / FCF 해석이 왜곡될 수 있으므로, 같은 지표 탭 안에 `연간`과 `분기` 차트를 위아래로 동시에 둔다.
- 막대 폭은 화면 너비를 채우지 않도록 고정 컬럼 폭 / 고정 bar width로 둔다. 긴 series는 각 그래프 내부 horizontal scroll로 확인한다.
