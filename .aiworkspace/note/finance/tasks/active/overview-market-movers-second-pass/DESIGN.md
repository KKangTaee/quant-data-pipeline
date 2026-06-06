# Design

## Why This Exists

`Overview > Market Movers > Why It Moved`는 자동 원인 판정기가 아니라 manual investigation board다. 사용자가 V1.7 / V1.8 SEC preview와 digest를 검토한 뒤 "표 아래 추가물"이 제품 판단에 앞서 너무 앞서 나갔다고 판단했으므로, 현재 SEC lane은 metadata table-only 상태로 되돌린다.

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

한국 뉴스는 이번 rollback 범위에 넣지 않는다. 후속 task에서 Naver News Search API 같은 credentialed metadata provider를 검토할 수 있지만, 기사 본문 수집과 사이트 scraping은 제외한다.
