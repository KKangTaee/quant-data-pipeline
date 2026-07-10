# Final Review Investment Report Redesign V1 Design

## 경계

- Python service가 score, evidence trace, pattern 판정과 문구를 만든다.
- Streamlit page는 확정 후보와 report render 순서를 소유한다.
- React component는 전달받은 read model을 표시만 한다.

## 점수 의미

- `투자 매력도`: 실제 측정값이 불리한 경우에만 낮춘다.
- `근거 신뢰도`: 미측정, proxy, freshness, coverage 부족을 반영한다.
- `Monitoring 준비도`: blocker, 저장 전 확인, 추적 조건의 준비 상태를 반영한다.
- open REVIEW 개수만으로 투자 매력도에 고정 감점이나 score cap을 적용하지 않는다.

## 패턴 가이드 원칙

- 저장된 evidence만 사용한다.
- 패턴마다 `supported`, `indicative`, `insufficient` 지원 상태를 제공한다.
- 관측값과 임계값이 없는 경우 투자 성과 방향을 단정하지 않는다.
- 대안 배분은 counterfactual backtest가 없으면 `대안 실험 후보`로만 제시한다.

## 패턴 10종 계약

1. 주식 / 섹터 집중도
2. 주식-채권 분산과 상관
3. 금리 / 듀레이션 민감도
4. 인플레이션 민감도
5. 변동성 / 낙폭 / tail risk
6. 추세 / 모멘텀 체제
7. 위험 기여도 / 구성요소 의존
8. 유동성 / 비용 / turnover
9. 벤치마크 의존 / 상대 성과
10. 파라미터 / 리밸런싱 민감도

각 패턴은 직접 관측값과 판단 기준이 있는 `supported`, 일부 직접 근거 또는 명시된 proxy만 있는 `indicative`, 필수 signal이 없는 `insufficient` 중 하나로만 판정한다.
