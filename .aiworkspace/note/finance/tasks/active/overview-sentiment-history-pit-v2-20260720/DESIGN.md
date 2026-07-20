# Design

승인된 설계 원문은 아래 문서를 따른다.

- `docs/superpowers/specs/2026-07-20-overview-sentiment-history-pit-v2-design.md`

핵심 경계:

- `macro_series_observation`: 현재 화면과 canonical latest history
- `market_sentiment_collection_batch`: source별 수집 회차와 성공/실패 provenance
- `market_sentiment_observation_snapshot`: 덮어쓰지 않는 normalized 수집 당시 기록
- `known_at`: provider publication time이 아니라 application이 실제 확인한 UTC 시각
- 현재 해석의 최근 범위는 180일로 고정하고 chart만 `6M / 1Y / 전체`를 전환
- 1W·1M 전망은 이번 task에서 계속 `UNAVAILABLE`
