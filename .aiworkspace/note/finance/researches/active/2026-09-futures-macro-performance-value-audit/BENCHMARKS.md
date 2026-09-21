# 외부 근거의 범위

Date: 2026-09-21

이번 요청은 현 제품의 성능·해석 감사다. 경쟁 서비스의 UI, 가격, 기능 비교는 수행하지 않았다. 기존 벤치마크 결론을 현 제품의 검증 결과처럼 재사용하지 않는다.

확인한 1차 자료:

- [CME: The basics of U.S. Treasury futures](https://www.cmegroup.com/trading/interest-rates/basics-of-us-treasury-futures.html): 국채 가격과 수익률의 역관계는 국채선물 약세를 금리 부담의 대리 지표로 삼는 방향 해석을 뒷받침한다. 특정 시점의 원인이나 주가 하락을 확정하지 않는다.
- [CME: Continuous Price Series](https://www.cmegroup.com/market-data/cme-group-continuous-price-series.html): active/front contract 선택, 교체 규칙과 settlement 기준이 연속가격의 정의를 구성한다. 현재 앱의 Yahoo 데이터가 CME 구성과 같거나 roll 보정이 완전하다고 추정할 수 없다.

외부 UI 벤치마크가 후속 필요하다면 ‘가격 사실과 해석의 분리’, ‘교차자산 불일치의 설명’, ‘잠정 시점과 완료일 표시’를 질문으로 삼는다. 현재 요청을 넘는 제품 리서치를 자동 확장하지 않는다.
