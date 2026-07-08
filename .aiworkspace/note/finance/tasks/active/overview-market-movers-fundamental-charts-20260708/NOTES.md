# Notes

- UI는 provider/DB를 직접 fetch하지 않는다. 조사 snapshot 서비스와 helper model이 만든 payload만 렌더링한다.
- 기존 `PER / EPS`, `당기순이익` 표 렌더링 테스트는 유지해야 한다.
- 유동비율은 `current_assets / current_liabilities`, FCF는 statement shadow / legacy financial row의 `free_cash_flow`를 사용한다.
- trend chart는 최근 최대 8개 statement row를 period_end / available_at 기준으로 정렬해 보여준다.
