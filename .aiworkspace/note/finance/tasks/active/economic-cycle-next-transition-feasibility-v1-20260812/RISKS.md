# Risks

- 같은 전환 전의 여러 월을 독립 표본처럼 쓰면 성능과 표본 수가 과장된다.
- strict PIT coverage가 2014년부터여서 최근 shock에 결과가 집중된다.
- 신규 RTDSM/ADS provider는 data schema, ingestion과 current-state parity를 별도
  검증해야 하며 이번 feasibility task에서 암묵적으로 추가하지 않는다.
- sample gate 통과는 model publication 승인이 아니다. 이후 baseline skill과
  calibration gate가 별도로 필요하다.
- repository-wide pytest는 기존 Streamlit singleton 격리 문제로 345 failed / 2317
  passed다. 경제사이클 전체 226개는 fresh process에서 통과했으며 이번 파일과 직접
  관련된 실패는 없다.
