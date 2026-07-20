# Design

승인된 설계 원문은 아래 문서를 따른다.

- `docs/superpowers/specs/2026-07-20-overview-sentiment-history-pit-v2-design.md`
- 사용자 최신값 노출 후속: `docs/superpowers/specs/2026-07-20-overview-sentiment-aligned-latest-end-design.md`

핵심 경계:

- `macro_series_observation`: 현재 화면과 canonical latest history
- `market_sentiment_collection_batch`: source별 수집 회차와 성공/실패 provenance
- `market_sentiment_observation_snapshot`: 덮어쓰지 않는 normalized 수집 당시 기록
- `known_at`: provider publication time이 아니라 application이 실제 확인한 UTC 시각
- 현재 해석의 최근 범위는 180일로 고정하고 chart만 `6M / 1Y / 전체`를 전환
- 1W·1M 전망은 이번 task에서 계속 `UNAVAILABLE`
- History는 두 source의 시작점만 맞추고 공통 x축 종료는 source 중 최신 날짜까지 확장한다. 각 선은 자기 마지막 관측일에서 끝나며 보간하지 않는다.
