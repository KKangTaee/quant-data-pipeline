# Portfolio Monitoring Price Refresh V1 Design

## 이걸 하는 이유?

Portfolio Monitoring의 종합 가치곡선은 활성 항목 중 가장 오래된 최신 일봉을 공통 기준일로 사용한다. 따라서 일부 종목의 DB 일봉이 늦으면 정상 종목까지 오래된 날짜로 보이지만, 현재 화면에는 해당 그룹만 즉시 보강하는 행동 경로가 없다.

## 결정

- 공통 기준일 계산은 바꾸지 않는다. 결측일 보간이나 carry-forward도 하지 않는다.
- 현재 선택 그룹의 활성 direct stock·ETF만 최신성 점검과 수집 대상으로 삼는다.
- 목표일은 최근 완전히 종료된 NYSE 거래일이다.
- stale 종목은 가장 오래된 최신일 앞 7일을 겹쳐 수집하며, provider 결과가 없는 종목의 기존 DB 행은 삭제하지 않는 현행 writer 계약을 사용한다.
- 수집 직후 DB를 다시 읽어 실제 해결 여부를 판정한다.
- React는 계산하지 않고 Python projection과 event만 소비한다.
- 실행 상세는 기존 Ingestion history가 소유하고 Portfolio Monitoring에는 지연 종목·목표일·간결한 결과만 표시한다.

## 사용자 흐름

1. 공통 기준일 배너에서 지연 종목과 각 최신일을 확인한다.
2. `보유 종목 가격 최신화`를 누른다.
3. 현재 그룹 direct stock·ETF의 최근 일봉만 수집한다.
4. 수집 후 DB freshness를 재확인한다.
5. 화면을 다시 불러 공통 기준일과 가치곡선을 재계산한다.
6. 남은 종목이 있으면 해당 symbol을 부분 완료 메시지로 확인한다.

## 제외 범위

- selected strategy 구성종목 자동 해석·수집
- 종료 종목 수집
- 재무제표, asset profile, ETF holdings/exposure, macro 수집
- broker/account/order/auto rebalance
- Portfolio Monitoring 내부 raw job diagnostics panel
