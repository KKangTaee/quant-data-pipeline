# Today Home + Purpose Navigation Design

## 이걸 하는 이유?

현재 `Workspace / Operations / Reference`는 기능 위치와 사용자 목적을 섞어 첫 진입에서 무엇을 판단해야 하는지 바로 드러내지 못한다. 사용자가 확정한 첫 업무는 `오늘의 시장 판단`이며, 시장 근거와 대표 포트폴리오 한 개의 영향을 같은 읽기 흐름에서 끝내야 한다.

## Approved User Flow

```text
Finance Console 최초 진입
  -> Research > Today
  -> 오늘의 시장 판단과 근거 확인
  -> 대표 포트폴리오 성과·기여·주의 확인
  -> Market Research / 종목 조사 / Portfolio Monitoring 중 하나로 이동
```

## Ownership

- `app/services/today.py`: 기존 결과의 compact projection과 missing/partial semantics.
- `app/web/today_page.py`: 기존 Overview visual token 기반 B안 renderer와 Page link adapter.
- `app/web/streamlit_app.py`: `/today` 등록, 기본 page, 목적형 navigation.
- 기존 Overview·Institutional·Backtest·Monitoring·Ingestion·Reference renderer: 변경하지 않음.

## Data Contract

Today는 provider를 부르지 않고 Economic Cycle, S&P 500 valuation, persisted Futures Macro, CNN/AAII sentiment, market events, default Portfolio Monitoring workspace만 읽는다.

시장 결론은 새 점수가 아니라 기존 근거의 상태·문장을 짧게 결합한 projection이다. 세 개 미만의 시장 근거만 사용 가능하면 결론을 만들지 않고 판단 보류를 표시한다.

## Presentation Contract

B안의 판단 우선 순서를 유지하되 기존 Market Context와 같은 white surface, blue-gray hierarchy, thin border, compact badge, restrained warning/positive tone을 사용한다. 데스크톱은 근거/일정을 2열로, 760px 이하에서는 같은 우선순위의 1열로 재배치한다.

## Tradeoffs

- 첫 화면 로딩은 여러 DB-backed loader를 읽기 때문에 Overview 단일 탭보다 무거울 수 있다. 기존 loader cache와 compact projection으로 제한하고 실제 Browser QA에서 확인한다.
- 종목별 당일 기여가 기존 workspace에 독립 필드로 없으므로 V1은 명확히 `누적 기여`로 표시하고, 오늘 수익률은 group unit value의 최근 두 관측으로 계산한다.
- 대표 포트폴리오 변경 command는 이번 범위가 아니다. 현재 default group을 따른다.
