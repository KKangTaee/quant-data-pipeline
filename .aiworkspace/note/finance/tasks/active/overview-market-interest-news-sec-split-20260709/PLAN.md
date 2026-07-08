# Overview Market Interest News / SEC Split Plan

## 이걸 하는 이유?

`Overview > Market Movers > 시장 관심`에서 뉴스와 SEC 공시가 `뉴스/공시 촉매` 한 테이블에 섞여 보여 Form 144 같은 공시가 뉴스 기사처럼 읽히는 혼선이 생겼다. 이 작업은 사용자가 선택 종목의 조사 단서를 더 빨리 구분하도록 뉴스 리스트와 SEC 공시 촉매 리스트를 분리한다.

## Scope

- 선택 종목 1개에 대한 `시장 관심` 패널만 수정한다.
- 기존 세션 전용 뉴스 / 한국 뉴스 / SEC metadata 흐름을 재사용한다.
- DB schema, ingestion, 13F 공식 데이터 수집, analyst provider API 연결은 하지 않는다.
- 추천, 점수화, buy/sell signal, 자동 catalyst 판정은 추가하지 않는다.

## Roadmap

| 차수 | 목적 | 완료 조건 |
|---|---|---|
| 1차 | 뉴스와 SEC 공시 read model 분리 | `news_catalysts`, `sec_filing_catalysts` sections가 테스트로 고정된다 |
| 2차 | SEC Form 의미 라벨 보강 | Form 144가 proposed sale notice로 표시되고 뉴스와 분리된다 |
| 3차 | UI table 분리 | `뉴스 리스트`, `SEC 공시 촉매`가 별도 표로 렌더링된다 |
| 4차 | QA / 문서 / 커밋 | focused tests, py_compile, diff check, Browser QA 후 커밋한다 |

## Files

- `app/services/overview/market_interest.py`
- `app/web/overview/market_movers_helpers.py`
- `tests/test_service_contracts.py`
- `.aiworkspace/note/finance/tasks/active/overview-market-interest-news-sec-split-20260709/`
- 필요한 경우 durable docs / root handoff logs
