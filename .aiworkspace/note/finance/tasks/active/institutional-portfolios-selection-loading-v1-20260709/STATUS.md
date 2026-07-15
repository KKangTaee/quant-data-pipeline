# Institutional Portfolios Selection Loading V1 Status

Status: Completed
Started: 2026-07-09
Completed: 2026-07-10 KST

## Progress

- 2026-07-09: 사용자 제보와 코드 추적으로 watchlist manager 선택 시 `selected_cik`가 search result 첫 row로 fallback되고, 같은 component key의 이전 event가 재처리되면서 rerun loop가 발생할 수 있음을 확인했다.
- 2026-07-09: reverse lookup은 manager portfolio 조회와 별개이며, `AAPL` 조회가 약 10초 걸리는 병목으로 측정됐다.
- 2026-07-10 KST: watchlist-aware selected manager resolver, custom component event nonce 소비, reverse lookup lazy cache, loading banner, Runtime / Build 제거, 주요 문구 한글화를 적용했다.
- 2026-07-10 KST: reverse lookup을 CUSIP / mapped symbol 우선 조회로 바꾸고 `institutional_13f_manager.latest_accession_number` index를 추가해 AAPL / CUSIP 조회를 약 0.13~0.30초로 낮췄다.
- 2026-07-10 KST: Browser QA에서 Baupost -> Pershing -> Berkshire -> Appaloosa 반복 선택 시 각 클릭 직후 `포트폴리오 불러오는 중` 배너가 뜨고 선택한 hero / active card로 정상 settle됨을 확인했다.

## Current Step

- 1차~6차 완료. 남은 후속 범위는 공식 SEC full ZIP 운영 refresh와 CUSIP-symbol map 품질 개선이다.
