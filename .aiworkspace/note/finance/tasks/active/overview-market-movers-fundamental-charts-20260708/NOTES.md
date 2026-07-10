# Notes

- UI는 provider/DB를 직접 fetch하지 않는다. 조사 snapshot 서비스와 helper model이 만든 payload만 렌더링한다.
- 기존 `PER / EPS`, `당기순이익` 표 렌더링 테스트는 유지해야 한다.
- 유동비율은 `current_assets / current_liabilities`, FCF는 statement shadow / legacy financial row의 `free_cash_flow`를 사용한다.
- trend chart는 period_end / available_at 기준 정렬 후 연간 최대 8개, 분기 최대 32개를 보여준다. 연간과 분기를 모두 8개로 자르면 연간은 2019년부터 보이지만 분기는 2023년 이후만 보여 사용자가 비교 범위를 오해한다.
- 2026-07-08 후속 2: 연간 / 분기를 한 차트에 섞지 않는다. 연간값과 분기값은 스케일이 달라 PER / EPS / 당기순이익 / FCF 해석이 왜곡될 수 있으므로, 같은 지표 탭 안에 `연간`과 `분기` 차트를 위아래로 동시에 둔다.
- 막대 폭은 화면 너비를 채우지 않도록 고정 컬럼 폭 / 고정 bar width로 둔다. 긴 series는 각 그래프 내부 horizontal scroll로 확인한다.
- 2026-07-08 후속 3: 값은 막대 위 annotation으로 두지 않는다. 좁은 column에서 막대 / 숫자 / 기간 라벨이 겹치므로 `막대 -> 기간 -> 값` 순서로 고정 caption을 둔다. 상세 회계기간 / 공시일은 title / aria label로 남긴다.
- 2026-07-08 후속 4: 연간과 분기를 같은 축에 합치지 않고 같은 row의 좌우 패널로 둔다. 각 패널은 독립 y-scale을 유지하고, 막대 top을 SVG line overlay로 연결해 같은 series 안의 흐름만 보여준다.
- 2026-07-08 후속 5: scroll wrapper 자체는 있었지만 `.ov-mm-research-chart` grid child가 기본 `min-width: auto`로 내용 폭을 밀어낼 수 있어 내부 `overflow-x: auto`가 체감되지 않을 수 있었다. chart panel에 `min-width: 0`, scroll wrapper에 `width/max-width: 100%`를 둬 분기처럼 긴 series가 각 그래프 내부에서 좌우 스크롤되도록 고정했다.
- 2026-07-08 후속 6: 음수 값이 하나라도 있으면 해당 연간/분기 그래프만 diverging axis로 처리한다. 양수-only 그래프는 기존처럼 아래 기준으로 전체 높이를 쓰고, 음수 포함 그래프는 0선을 50% 위치에 두고 양수/음수를 `max(abs(value))` 기준으로 위/아래에 배치한다.
- 2026-07-08 후속 7: screenshot에서 분기 그래프가 2023년 이후만 노출된 직접 원인은 service trend builder의 `limit=8` 기본값이었다. 화면 scroll CSS가 있어도 point가 8개뿐이면 overflow가 생기지 않는다.
- 2026-07-08 후속 7: 금액 value가 `"620,000,000"`처럼 콤마 문자열로 들어올 수 있어 service/model/component에서 숫자 정규화를 보강했다. 금액 표시는 `조/억/만/천/달러` 순으로 축약한다.
- 2026-07-11 정렬 보정: 선의 x좌표는 Python 상수 `64px` 열과 `4px` 간격으로 계산했지만 CSS 막대 열은 `rem` 단위를 사용해, root 글자 크기가 16px이 아닐 때만 중심선이 달라졌다. plot wrapper가 같은 Python 상수에서 chart-local CSS 변수를 주입하고 막대 grid/column이 그 변수를 상속하도록 해 선, 막대, 라벨이 하나의 폭 계약을 사용한다.
