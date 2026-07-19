# Economic Cycle Gold / Dollar Price Confirmation V1 Plan

## 이걸 하는 이유?

경제 전체의 회복 국면을 금·달러 가격 회복으로 오해하지 않도록 거시 배경과 실제 가격 확인을 분리한다.

1. 금·달러 가격 원천과 DB-only loader
2. 가격 흐름 및 거시 배경 일치·불일치 판정
3. Overview service 연결
4. 5개 카드 React UI
5. actual backfill, QA, docs

Stop condition: 금과 달러가 분리되고 각 카드에서 경제 배경, 1주/1개월/3개월 가격, 종합 판단, 서로 다른 기준일을 읽을 수 있다.
