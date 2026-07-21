# Risks

- provider가 최근 완료 거래일 데이터를 아직 제공하지 않으면 부분 완료로 남을 수 있다.
- selected strategy는 1차 대상이 아니므로 direct security가 없어도 전략 lane 자체가 오래되면 이 action으로 해결되지 않는다.
- 실제 provider 호출 Browser QA는 외부 응답과 rate limit에 영향을 받는다.
- partial success는 숨기지 않고 아직 지연된 symbol을 공통 기준일 배너에 계속 남긴다. 재시도와 상세 job 원인은 Ingestion 실행 기록에서 확인한다.
- selected strategy의 구성 종목 자동 해석·수집은 전략 replay source와 비용 경계가 달라 후속 승인 범위로 남긴다.
