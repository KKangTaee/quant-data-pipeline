# Phase 10 Dynamic PIT First-Pass Implementation Order

## 목적

- `historical dynamic PIT universe`를
  현재 프로젝트 구조에서 가장 안전하게 여는 구현 순서를 고정한다.

## 핵심 전제

- current static preset는 유지한다
- first pass target은 `strict annual family`
- universe membership는 first pass에서
  **rebalance-date approximate PIT market-cap** 기준으로 구성한다

## 추천 구현 순서

### Step 1. contract and naming

먼저 아래 naming을 고정한다.

- `Static Managed Research Universe`
- `Historical Dynamic PIT Universe`

중요:

- 기존 preset 의미를 바꾸지 않는다
- new mode를 additive path로 연다

산출물:

- mode 명칭
- help/caution wording
- runtime meta key

### Step 2. universe membership builder

rebalance date별 membership builder를 만든다.

기본 알고리즘:

1. rebalance date 입력
2. usable price row 확보
3. `latest_available_at <= rebalance_date`인 최신 statement shadow row 선택
4. `shares_outstanding` 선택
5. `price * shares_outstanding`으로 market-cap proxy 계산
6. top-N membership 구성

산출물:

- builder function
- membership dataframe contract

### Step 3. annual strict runtime integration

strict annual family runtime에
새 universe mode를 연결한다.

초기 target:

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

산출물:

- single strategy first pass
- compare는 later same phase 또는 second pass

### Step 4. validation readout

dynamic mode가 들어가면
사용자는 반드시 아래를 같이 볼 수 있어야 한다.

- requested top-N
- actual dynamic membership count
- membership drift summary
- static vs dynamic difference summary

즉 단순 실행만이 아니라
“왜 결과가 달라졌는지”를 읽는 표가 같이 있어야 한다.

### Step 5. persistence / snapshot option

first pass에서 필요하면
rebalance-date membership snapshot을 저장한다.

후보:

- in-memory first pass
- or optional `universe snapshot` persistence

권고:

- first pass는 실행 correctness 우선
- persistence는 second pass 또는 optional helper로 두는 편이 안전하다

### Step 6. compare / history extension

single strategy가 안정화된 뒤,
다음 surface로 확장한다.

- compare
- history
- rerun payload

권고:

- single strategy first pass 검증 전 compare로 바로 넓히지 않는다

## why this order is good

이 순서가 좋은 이유:

1. current static contract를 깨지 않음
2. annual strict family로 가장 안정적인 strategy surface에서 시작
3. 구현 복잡도를 universe builder에 집중 가능
4. 결과 해석을 static vs dynamic 비교로 바로 검증 가능

## what not to do first

처음부터 아래를 같이 하지 않는 것이 좋다.

- quarterly family까지 동시에 열기
- portfolio productization과 같이 묶기
- perfect constituent-history DB를 먼저 만들려고 하기

이건 모두 일정과 리스크를 크게 늘린다.

## one-line recommendation

Phase 10 first pass는
**annual strict family + rebalance-date approximate PIT market-cap universe builder**
로 시작하는 것이 가장 현실적이고 실무적인 경로다.
