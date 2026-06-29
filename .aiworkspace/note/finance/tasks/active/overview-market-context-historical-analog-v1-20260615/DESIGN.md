# Overview Market Context Historical Analog V1 Design

## User Flow

1. 사용자는 Market Context의 `현재 맥락`과 `시장 브리프`를 먼저 읽는다.
2. 바로 아래의 `과거 유사 맥락 참고`에서 현재 어떤 leadership sector와 ETF proxy를 기준으로 보았는지 확인한다.
3. sample이 충분하면 주요 자산의 이후 5D/20D/60D 중간값 / 상승 비율 / 최선 / 최악 범위를 compact하게 본다.
4. sample이나 coverage가 부족하면 이유와 한계를 보고 억지 해석을 하지 않는다.
5. 더 자세한 운영/수집 상태는 Data Health 또는 task note가 소유하고, Market Context는 해석 보조만 맡는다.

## Recommended Approach

선택지는 세 가지다.

- A. `overview_market_intelligence.py`에 모든 analog logic을 추가한다. 기존 cockpit과 결합은 쉽지만 파일이 더 커지고 test boundary가 흐려진다.
- B. 새 `app/services/overview_market_context_analog.py`를 만들고, cockpit read model이 compact 결과만 embed한다. map / coverage / relative-strength / forward-return logic을 독립 테스트하기 쉽다.
- C. UI helper에서 기존 snapshot만 조합한다. 빠르지만 DB price coverage와 look-ahead 방지 계산을 UI가 떠안는다.

이번 MVP는 B를 선택한다. Streamlit-free service가 DB-backed price history를 받아 계산하고, 기존 Overview service/UI는 결과를 작게 렌더링한다.

## Read Model Direction

- `SECTOR_ETF_PROXIES`: GICS sector와 흔한 label alias를 대표 ETF로 매핑한다.
- `resolve_sector_proxy_from_leadership()`: current leadership label에서 sector ETF proxy를 찾는다.
- `summarize_price_coverage()`: symbol별 start/end/row count/coverage status를 만든다.
- `build_historical_analog_snapshot()`: leadership, price data, comparison assets를 받아 `OK / REVIEW / INSUFFICIENT_DATA` read model을 만든다.
- relative-strength condition은 MVP에서 단순하게 유지한다.
  - current relative strength: sector ETF 5D return - SPY 5D return.
  - anchor 후보: 과거 구간의 5D relative strength가 현재값과 threshold 안에 있거나 최소 threshold 이상.
  - optional 20D relative strength를 condition summary에 보조로 둔다.
  - 중복 anchor는 최소 간격으로 dedup한다.
  - forward return은 anchor 이후 5D/20D/60D 데이터만 사용한다.

## UI Direction

- Market Context에서 `시장 브리프`와 event/data cue 아래에 작은 section으로 둔다.
- 제목은 `과거 유사 맥락 참고`를 사용한다.
- headline은 `과거 유사 맥락 N회 발견` 또는 `자료 부족`처럼 표현한다.
- table은 핵심 자산과 5D/20D/60D summary를 우선 보여주고, limitations는 작게 둔다.
- 금지 문구: 예측, 추천, 매수, 매도, 신호, PASS, BLOCKER.

## Boundary

기존 `Ingestion -> DB -> Loader/Service -> UI` 흐름을 유지한다.
이번 작업은 Overview context-only 보조 분석이며 DB schema, provider, registry/saved JSONL, Backtest/Validation/Final Review/Operations 의미를 만들지 않는다.
