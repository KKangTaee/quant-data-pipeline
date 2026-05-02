# Phase 10 PIT Source And Schema Gap Analysis

## 목적

- current code / DB 기준으로
  `historical dynamic PIT universe` 구현에 바로 활용 가능한 데이터와
  아직 부족한 데이터를 구분한다.
- first-pass dynamic PIT 구현안을
  현재 저장 구조에 맞게 현실적으로 설계한다.

## 현재 코드 기준 확인 결과

### 1. `nyse_asset_profile`

현재 schema:

- `symbol`
- `kind`
- `sector`
- `industry`
- `country`
- `market_cap`
- `status`
- `last_collected_at`
- `delisted_at`

핵심 한계:

- **current snapshot 테이블**이다
- historical market-cap history가 없다
- historical listing-status snapshot도 없다

즉:

- current strict preset 생성용 current managed universe에는 유용
- `historical dynamic PIT universe` membership source로는 불충분

### 2. `nyse_price_history`

현재 schema:

- `symbol`
- `timeframe`
- `date`
- `open/high/low/close/adj_close/volume`

강점:

- historical price time series는 이미 있음
- rebalance-date 종가 기준 정렬/필터의 핵심 입력으로 바로 쓸 수 있음

한계:

- market-cap ranking 자체는 가격만으로 만들 수 없음
- shares outstanding 또는 equivalent market-cap source가 필요함

### 3. `nyse_fundamentals_statement`

현재 schema/의미:

- `symbol`
- `freq`
- `period_end`
- `shares_outstanding`
- `latest_available_at`
- `latest_accession_no`
- `latest_form_type`
- statement-derived normalized fields

강점:

- point-in-time usable statement shadow가 있음
- `shares_outstanding`와 `latest_available_at`가 있어
  **“그 시점에 알려진 최신 발행주식수”** 근사 source로 활용 가능함

한계:

- statement cadence 기반이라 월별/일별로 촘촘하지 않음
- 모든 종목 / 모든 날짜에 시장가치 ranking source로 완전하지 않음

### 4. `nyse_factors_statement`

현재 schema/의미:

- `fundamental_available_at`
- `price_date`
- `market_cap`
- `pit_mode = statement_derived_shadow`

강점:

- statement-derived market-cap이 이미 계산되어 저장됨
- strict family factor path와 자연스럽게 이어질 수 있음

한계:

- factor snapshot의 cadence와 symbol coverage에 종속됨
- rebalance-date universe membership를 직접 저장하는 구조는 아님

## 중요한 결론

현재 DB에는
**historical universe membership table 자체는 없다.**

즉 지금 바로 가능한 방식은 둘 중 하나다.

1. 별도 historical membership source를 새로 구축
2. 현재 있는 price + statement shares_outstanding을 이용해
   **rebalance-date approximate PIT market-cap universe**를 first pass로 구성

실전 우선순위와 구현 비용을 같이 보면,
현재 프로젝트에서는 **2번이 더 현실적인 first pass**다.

## 권장 first-pass universe source

### rebalance-date approximate PIT market cap

각 rebalance date마다:

1. 해당 날짜의 usable price 확보
2. 그 날짜 기준 `latest_available_at <= rebalance_date`인
   가장 최신 statement shadow row 선택
3. 그 row의 `shares_outstanding` 사용
4. `price * shares_outstanding`으로 approximate PIT market-cap 계산
5. top-N membership 구성

이 방식의 장점:

- 현재 DB 구조 안에서 바로 시작 가능
- annual strict family와 가장 잘 맞음
- point-in-time discipline을 현재 static preset보다 크게 개선함

이 방식의 한계:

- true constituent history와 동일하지는 않음
- shares outstanding update lag가 존재할 수 있음
- foreign / unsupported form bucket은 여전히 제외 정책이 필요함

## first-pass에 적합한 대상

현재 가장 적합한 target은:

- `strict annual family`

이유:

- annual family가 현재 가장 안정적
- quarterly는 coverage와 policy가 아직 더 민감함
- dynamic PIT first pass는 universe contract를 검증하는 성격이 강하므로
  먼저 annual에서 contract를 여는 편이 안전함

## schema gap

현재 기준 부족한 것:

### 1. historical universe snapshot persistence

아직 없음.

후보:

- `nyse_universe_snapshot`
  - `rebalance_date`
  - `symbol`
  - `universe_mode`
  - `rank`
  - `market_cap`
  - `price_date`
  - `shares_available_at`
  - `membership_reason`

### 2. historical asset-profile history

아직 없음.

다만 first pass에 꼭 필요하지는 않다.
initial pass는
price + statement shares outstanding 근사치로 먼저 열 수 있다.

### 3. symbol continuity mapping

현재는 policy/logical review 수준이지,
dedicated historical symbol lineage table은 없다.

이 부분은 later hardening 대상으로 두는 편이 현실적이다.

## recommendation

현재 코드베이스 기준 가장 합리적인 Phase 10 first pass는:

1. current static preset 유지
2. annual strict family에 한해
3. `price x latest-known shares_outstanding` 기반
   `rebalance-date approximate PIT market-cap universe`
   를 별도 mode로 추가
4. static vs dynamic 결과를 비교 가능하게 만들기

즉 처음부터 “완벽한 historical constituent DB”를 요구하지 말고,
현재 저장 구조를 최대한 활용하는 realistic PIT upgrade path로 가는 것이 맞다.
