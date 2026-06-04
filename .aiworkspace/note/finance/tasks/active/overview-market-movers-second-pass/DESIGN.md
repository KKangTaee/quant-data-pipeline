# Design

## Why This Exists

`Overview > Market Movers > Why It Moved`는 자동 원인 판정기가 아니라 manual investigation board다. V1.7은 선택한 SEC filing 1건을 버튼으로만 session-only preview 하도록 만들었다. V1.8은 이 preview를 더 읽기 쉬운 digest로 재구성해, 사용자가 official SEC link로 이동하기 전에 앱 안에서 공시의 조사 위치를 빠르게 잡을 수 있게 한다.

## V1.8 SEC Digest Scope

- 기존 SEC metadata table은 계속 `Form / Filing Date / Title / Open` 중심으로 표시한다.
- Filing 원문 fetch는 `선택 공시 원문 미리보기` 버튼을 누른 선택 filing 1건에 대해서만 실행한다.
- Selectbox 변경은 fetch를 실행하지 않는다.
- Preview 결과는 Streamlit session state에만 남긴다.
- DB schema, registry JSONL, saved JSONL, article body, filing body, AI summary, sentiment, automatic catalyst judgement는 추가하지 않는다.
- Official SEC `Open/열기` link와 external original URL은 계속 보존한다.

## Service Contract

`parse_market_mover_sec_filing_preview` / `fetch_market_mover_sec_filing_preview`는 기존 bounded preview payload에 `digest`를 추가한다.

Digest는 저장 가능한 원문이 아니라, 화면 렌더링용 compact read model이다.

- `digest.type`: `8k_items`, `periodic_sections`, or `generic_sections`
- `digest.cards`: heading, kind, snippet, investigation hint, optional item code
- `digest.tables`: bounded table previews only when SEC HTML has small inspectable tables
- `digest.exhibits`: exhibit/document link clues when visible in bounded preview
- `digest.messages`: partial parse / failure / boundary messages

8-K는 `Item 2.02`, `7.01`, `8.01`, `9.01` 같은 Item heading을 카드로 보여준다. `9.01` 또는 Exhibit row가 보이면 exhibit clue를 별도 표로 낮게 보여준다.

10-Q / 10-K는 Table of Contents, Part / Item heading, MD&A, Risk Factors, Financial Statements 위치 단서를 카드화한다. 작은 HTML table은 caption / nearby heading / bounded rows / columns만 보여주고 원문 전체 table dump는 하지 않는다.

## UI Contract

SEC preview 결과는 metadata, official SEC link, status strip 다음에 digest-first로 렌더링한다.

1. fetch status / fetched_at / session-only boundary
2. form / filing date / title / accession / document
3. official SEC `열기` link
4. `공시 Digest` 카드 / bounded table / exhibit clue
5. 기존 bounded section expander fallback

실패, non-HTML, oversize, parse partial 상태에서는 official SEC `열기` link와 메시지를 먼저 보여주고 digest 영역은 비어 있거나 partial message만 표시한다.

## Korean News Boundary

한국 뉴스는 이번 SEC V1.8 구현 범위에 넣지 않는다. 후속 task에서 Naver News Search API 같은 credentialed metadata provider를 검토할 수 있지만, 기사 본문 수집과 사이트 scraping은 제외한다.
