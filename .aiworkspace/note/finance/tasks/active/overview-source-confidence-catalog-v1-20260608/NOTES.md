# Notes

- 4차의 provider hardening은 새 provider 교체가 아니라 기존 source semantics를 화면에서 숨기지 않는 read-model/UI hardening이다.
- 1차 cockpit이 이미 필요한 snapshots를 모으므로 catalog도 그 snapshots를 재사용한다.
- Catalog items는 Prices / Movers, Breadth / Groups, Futures Context, Sentiment, Events, Data Health 순서로 고정했다.
- Sentiment는 snapshot status가 OK여도 `analysis.data_confidence.status`가 degraded이면 catalog에서 REVIEW로 노출한다.
- Status는 source confidence context이며 Practical Validation PASS/BLOCKER, Final Review decision, monitoring signal, trading instruction이 아니다.
- Browser QA에서는 `Source Confidence` lane이 Market Movers stale, Events review, Data Health review, futures free-provider caveat를 표시하는 것을 확인했다.
