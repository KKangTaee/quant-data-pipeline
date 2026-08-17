# Notes

- Source of truth for implementation and actual QA: `.superpowers/sdd/2026-08-17-institutional-holdings-metric-clarity/task-{1,2,3,4}-brief.md`.
- Canonical flow에는 최종 검증된 contribution과 ranking 의미만 추가했다. Product ownership과 system boundary는 unchanged다.
- `top_contributors`와 `top_detractors`는 각각 strictly positive/negative `contribution_pct`만 포함한다. 0은 어느 목록에도 표시하지 않는다.
- 기존 `SEC_13F_SOURCE_CAVEATS`는 변경하지 않고 Korean disclosure projection을 별도 read-model 상수로 제공한다.
- Actual Browser QA에서 contributor는 양수만, detractor는 음수만 표시됐고 각 row는 `이전 보고 비중 / 종목 수익률(%) / 포트폴리오 기여(%p)`를 분리했다.
- 첫 Browser pass의 계산식 white-on-light 문제는 `7b8fd606`에서 수정했다. Final QA computed color는 `rgb(23, 35, 55)`, 카드 배경은 `rgb(247, 250, 252)`다.
- 첫 pass의 빈 랭킹 값과 legacy English disclosure는 pre-Task1 Python modules를 유지한 기존 `:8502` process를 재사용한 결과였다. 현재 HEAD에서 fresh `:8521` process를 시작하자 GOOGL `보유 기관 7개 / 13F 보고 보유가액 합계 $31.4B`, 시가총액/거래량 clarification, Korean disclosure가 모두 표시됐다.
- disclosure는 초기에 접혀 있고 `13F 자료 해석 시 주의 / 지연 공시 · 실시간 매매 신호 아님`을 보이며, 펼치면 정확히 한국어 3개 bullet을 표시한다.
- 계산, 랭킹 우선순위, refresh, ingestion, DB schema, registry/saved, trading boundary는 바뀌지 않았다.
