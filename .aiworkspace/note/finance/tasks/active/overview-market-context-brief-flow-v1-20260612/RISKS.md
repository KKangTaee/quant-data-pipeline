# Overview Market Context Brief Flow V1 Risks

## Residual Risks

- 갱신을 실행한 뒤 상단 Market Context가 즉시 새 snapshot을 반영하는지 별도 점검이 필요하다.
- CPI/Event coverage 보강과 Macro Calendar collector 개선은 별도 데이터 수집 작업이다.
- Data Health 노출 범위는 1차에서 작게 줄이지만, 전체 Data Health UX는 후속 검토가 필요하다.
- 과거 유사국면 기능은 이번 1차 범위가 아니며 별도 제품 기능으로 검토해야 한다.
- `source_confidence` read model에는 아직 `next_checks` 구조가 남아 있다. 이번 1차 UI에서는 노출하지 않지만, 2차 Data Health 노출 범위 재검토 때 model naming까지 정리할 수 있다.
