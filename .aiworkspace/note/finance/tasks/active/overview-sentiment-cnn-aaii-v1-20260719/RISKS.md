# Risks

- CNN은 여러 시장 행동 지표의 종합값이므로 구성요소를 별도 독립 축처럼 다시 합산하면 이중 반영된다.
- AAII 주간 설문과 CNN 일간 지표의 변화 속도를 직접 비교하거나 같은 선으로 연결하지 않는다.
- 최근 범위 percentile은 저장된 표본 내 위치이며 장기 역사 percentile이나 미래 예측으로 표현하지 않는다.
- `+10pp / -10pp` AAII spread 경계는 제품의 deterministic 해석 규칙이며 투자 수익 예측 임계값이 아니다.
- 1차에서 제공하는 확인 조건은 관찰 checklist이지 목표가격, 매매 신호, 확률 전망이 아니다.
- 2차에서 발표 당시 값과 수정 이력, 장기 coverage가 충분히 축적되기 전에는 최근 percentile을 역사적 극단값처럼 해석하지 않는다.
- 1주·1개월 전망은 별도 point-in-time feature/target 정의와 chronological out-of-sample 검증 없이는 추가하지 않는다.
- AAII 표본과 CNN 산출 방법의 source-side 변경 가능성은 freshness / raw evidence와 후속 품질 점검에서 계속 확인한다.
- 시각 companion의 1W·1M 확률은 production 근거로 재사용하지 않는다. estimator와 validation evidence가 없으면 UI는 반드시 `UNAVAILABLE`을 표시하고 확률 field를 렌더링하지 않는다.
- frontend fallback은 rolling reload 시 component crash를 막는 unavailable 표시일 뿐이며 전망 evidence를 대체하지 않는다. 정상 전망 공개 여부는 Python의 validation gate가 소유한다.
