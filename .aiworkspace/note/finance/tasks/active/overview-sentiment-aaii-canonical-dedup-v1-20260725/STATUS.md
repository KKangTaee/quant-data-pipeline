# Status

- 상태: 완료
- 전체 범위: `3/3` 완료
- 1차 preventive reconciliation: success 상태의 official AAII XLS capture가 네 series 정렬과 연속 7일 cadence를 모두 통과할 때만 snapshot insert 뒤 canonical UPSERT 전에 incoming date window를 official date set으로 정리한다. HTML fallback, CNN, partial/non-official capture는 비대상이다.
- 2차 actual cleanup: official workbook full backfill로 canonical을 `2,054주 / 8,216행`에서 `2,033주 / 8,132행`으로 원자 재구축했다. Immutable snapshot `1,104행`과 batch `11건`은 보존했다.
- 3차 downstream 검증: 6/17·18, 7/8·9를 포함한 HTML/XLS 하루 간격 중복이 DB와 React payload에서 제거됐고 최근 row는 정확한 7일 간격이다.
- 자동 검증: initial TDD RED와 review 반례 RED를 확인한 뒤 `tests.test_sentiment_pit` `26 passed`, sentiment service/React focused contract `14 passed`, sentiment Python compile와 `git diff --check`가 통과했다.
- 전체 suite 공백: repository-wide `unittest discover`는 현재 비관련 영역을 포함해 `1,816 tests / 272 errors / 12 failures`로 green이 아니다. 상세는 `RUNS.md`와 `RISKS.md`에 남겼다.
- 실제 Browser QA: `localhost:8501/overview?overview_tab=sentiment`에서 AAII 보유 이력 `2,033개`, latest `2026-07-23`, previous `2026-07-16`, Spread tab 렌더와 console error 0을 확인했다. Screenshot은 generated `overview-sentiment-aaii-canonical-dedup-qa.png`로 commit에서 제외한다.
- 변경하지 않은 범위: immutable PIT, AAII 판정 기준, chart rendering, CNN, 1W/1M 전망, 기존 Sentiment 전체 roadmap `2/4차`.
- 다음 행동: 없음. 3차 독립 데이터 후보 검토는 기존 상위 Sentiment roadmap에서 계속 보류 상태다.
