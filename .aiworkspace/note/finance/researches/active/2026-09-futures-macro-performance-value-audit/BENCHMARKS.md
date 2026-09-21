# 외부 근거의 범위

Date: 2026-09-21

최초 요청은 현 제품의 성능·해석 감사였고 그 시점에는 경쟁 서비스 비교를 수행하지 않았다. 이후 사용자가 실무 근거를 빠르게 확인해 달라고 요청해 아래의 좁은 benchmark를 추가했다. 기존 벤치마크나 외부 제품의 성과를 현 제품의 검증 결과처럼 재사용하지 않는다.

확인한 1차 자료:

- [CME: The basics of U.S. Treasury futures](https://www.cmegroup.com/trading/interest-rates/basics-of-us-treasury-futures.html): 국채 가격과 수익률의 역관계는 국채선물 약세를 금리 부담의 대리 지표로 삼는 방향 해석을 뒷받침한다. 특정 시점의 원인이나 주가 하락을 확정하지 않는다.
- [CME: Continuous Price Series](https://www.cmegroup.com/market-data/cme-group-continuous-price-series.html): active/front contract 선택, 교체 규칙과 settlement 기준이 연속가격의 정의를 구성한다. 현재 앱의 Yahoo 데이터가 CME 구성과 같거나 roll 보정이 완전하다고 추정할 수 없다.

외부 UI 벤치마크가 후속 필요하다면 ‘가격 사실과 해석의 분리’, ‘교차자산 불일치의 설명’, ‘잠정 시점과 완료일 표시’를 질문으로 삼는다. 현재 요청을 넘는 제품 리서치를 자동 확장하지 않는다.

## 후속 실무 근거 확인

Access: 2026-09-21. 대상은 분석 구조의 유사성·실무 존재 여부다. 가격/패키징은 범위 밖이다.

| 제품/방법 | 사용자·workflow | 근거 수준 | 적용과 한계 |
|---|---|---|---|
| SentimenTrader | 시장 리서처; 유사 패턴 이후 기간별 성과, 조건별 backtest | Documented/Observed-public-page: 공식 API와 공개 페이지의 표 구조 | 직접적인 analog/conditional outcome 선례. 유료 engine 실행·정확도 검증은 안 함 |
| MSCI predictive stress testing | 위험관리자; 시나리오 정량화 → 위험요인 전파 → 견고성 검토 | Documented: 공식 방법론 | 교차자산 해석 근거. 발생 확률·5일 예측력 근거가 아님 |
| Vanguard Portfolio Analytics stress testing | advisor; 역사 사건/가상 충격의 portfolio/sleeve 영향 비교 | Claimed: 공식 제품 workflow 소개 | 실제 서비스 목적 확인. n/N forecast와 동일하지 않음 |

SentimenTrader의 공개 기능은 이번 제안과 직접 비교 가능하다. MSCI/Vanguard는 인접 위험관리 workflow이며 그 이름만으로 우리 forecast를 정당화하지 않는다. 공식 출처·확인 한계는 [PRACTICE_VALIDATION.md](./PRACTICE_VALIDATION.md)와 SOURCES에 둔다.
