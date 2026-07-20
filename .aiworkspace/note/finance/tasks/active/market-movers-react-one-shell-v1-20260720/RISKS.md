# Risks

- group snapshots는 sector/industry × daily/weekly/monthly 여섯 개이므로 cached DB loader를 사용해야 한다.
- current TTM PER coverage가 낮아 unavailable UX가 기본 경로에서 읽기 쉬워야 한다.
- provider industry는 stable display key이며 GICS taxonomy로 표방하지 않는다.
- 기존 generated QA 이미지와 registry/saved/run-history 파일은 이번 task에 포함하지 않는다.
- 5차 OOS gate 전에는 conditional outlook 수치를 노출하지 않는다.
- selected research의 current PER는 actual 표본에서 unavailable이 흔하다. UI는 이를 계산 실패로 숨기지 않고 reported diluted EPS 4분기 조건과 함께 표시한다.
- 6개 cached group snapshot 때문에 최초 uncached 진입은 수 초 이상 걸릴 수 있다. 이 task는 correctness와 one-shell UX를 닫았고, materialized aggregate/latency 최적화는 5차 설계에서 별도 판단한다.
- repository-wide service contract는 Market Movers 외 Practical Validation / Final Review / Sentiment에서 13건 실패한다. Market Movers focused 126건에는 실패가 없으며 이번 task에서 해당 외부 경로를 수정하지 않는다.
