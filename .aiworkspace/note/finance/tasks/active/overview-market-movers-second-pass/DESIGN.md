# Design

## Why This Exists

`Overview > Market Movers > Why It Moved`는 자동 원인 판정기가 아니라 manual investigation board다. 사용자가 V1.7 / V1.8 SEC preview와 digest를 검토한 뒤 "표 아래 추가물"이 제품 판단에 앞서 너무 앞서 나갔다고 판단했으므로, 현재 SEC lane은 metadata table-only 상태로 유지한다.

뉴스 쪽은 사용자가 "왜 주가가 움직였는지 직접 확인하기 위한 한글 기사 단서"를 원하므로, 기사 본문 수집이나 요약 대신 credentialed Korean news metadata lane을 추가한다. 이 lane은 Naver News Search API의 bounded search-result fields만 사용한다.

## Current SEC Lane Scope

- 기존 SEC metadata table은 `Form / Filing Date / Title / Open` 중심으로 유지한다.
- UI 표시 라벨은 `양식 / 공시일 / 제목 / 열기`를 사용한다.
- SEC URL은 clickable `열기` link로 유지한다.
- SEC 공시 원문 fetch, preview selector, `선택 공시 원문 미리보기` 버튼, `공시 Digest`, bounded snippet / table / exhibit UI는 제거한다.
- DB schema, registry JSONL, saved JSONL, article body, filing body, AI summary, sentiment, automatic catalyst judgement는 추가하지 않는다.

## Service Contract

서비스는 compact SEC metadata만 반환한다.

- `fetch_market_mover_compact_metadata`는 `sec_filings`를 `Form / Filing Date / Title / URL` column으로 제한한다.
- `sort_market_mover_sec_filings_by_form_priority`는 표시 순서만 정한다.
- SEC filing body fetch / parse helper는 현재 contract에서 제외한다.

## UI Contract

`조사 단서 > SEC 공시`는 metadata table만 렌더링한다.

1. 섹션 제목과 caption
2. `양식 / 공시일 / 제목 / 열기` table
3. provider 실패 / empty 상태 메시지

재무제표형 표 preview가 필요하면 별도 후속 기능으로 다시 설계한다. 그 후속 기능은 8-K digest가 아니라 10-Q / 10-K 또는 SEC XBRL/companyfacts 기반 재무제표 preview로 분리하는 것이 적합하다.

## Korean News Boundary

`조사 단서`는 기존 `뉴스 메타데이터`, `SEC 공시`, collapsed `외부 검색`에 더해 `한국어 뉴스` lane을 가진다.

- `한국어 뉴스`는 `NAVER_SEARCH_CLIENT_ID` / `NAVER_SEARCH_CLIENT_SECRET`가 있을 때만 Naver official Search API를 호출한다.
- 표시 column은 `제목 / 출처 / 게시 시각 / 단서 / 열기`다.
- `title`과 `description`의 Naver `<b>` highlight tag는 제거하고, `description`은 bounded snippet인 `단서`로만 표시한다.
- clickable URL은 `originallink`를 우선 사용하고, 없으면 `link` / `url`을 fallback한다.
- Naver credentials가 없으면 optional setup message를 표시하고 전체 lookup failure로 취급하지 않는다.
- Naver request가 실패하면 `한국어 뉴스 메타데이터 조회 실패` provider failure로 표시한다. 다른 provider row가 있으면 `PARTIAL`이다.
- 기사 본문 수집, AI summary, sentiment, automatic catalyst judgement, DB schema, registry JSONL, saved JSONL, article body 저장은 추가하지 않는다.
