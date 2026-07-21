# Reference Center React V1 Design

Status: User-Approved Design / Written Spec Approved
Date: 2026-07-20

## Summary

`Reference > Guides`와 `Reference > Glossary`를 단일 React `Reference Center`로 통합한다.
선택한 정보 구조는 Search-first Hybrid다.
검색을 첫 행동으로 두고, 검색어를 모르는 사용자는 6개 사용자 여정에서 시작한다.

Reference는 읽기 전용 설명 surface다.
데이터 수집, 저장, 검증 판정, 모니터링 mutation이나 거래 행동을 소유하지 않는다.

## Approved Decisions

- 상단 navigation에는 `Reference` 하나만 둔다.
- 기존 `Guides`, `Glossary`, `Portfolio Selection Journey` 독립 page/mode는 제거한다.
- legacy·개발자 용어는 사용자 Reference 검색에서 완전히 제외하고 내부 `GLOSSARY.md`에만 보존한다.
- 검색 중심 하이브리드 A안을 사용한다.
- 데스크톱 상세는 side drawer, 520px 이하는 full-width sheet로 표시한다.
- Runtime / Build, log, run history, failure artifact, raw registry는 first-read와 Reference 기능 범위에서 제외한다.

## User Experience

### First View

화면 순서는 아래와 같다.

1. 제목과 짧은 목적 설명
2. 통합 검색 input
3. `전체 / 사용 흐름 / 상태·용어 / 문제 해결` scope filter
4. 검색 전 기본 진입용 6개 journey card
5. 검색 결과 list
6. 선택 항목 detail drawer/sheet

긴 hero, runtime chip, 시스템 ownership 설명을 검색보다 먼저 표시하지 않는다.

### Six User Journeys

| ID | 사용자 질문 | 주요 화면 |
| --- | --- | --- |
| `journey.market_understanding` | 지금 시장을 어떻게 읽는가? | Overview: Market Context, Market Movers, Futures Macro, Sentiment, Events |
| `journey.institutional_portfolios` | 기관의 13F 보유를 어떻게 해석하는가? | Institutional Portfolios |
| `journey.data_preparation` | 필요한 데이터를 어디서 준비하는가? | Ingestion |
| `journey.candidate_creation` | 전략·mix 후보를 어떻게 만드는가? | Backtest Analysis |
| `journey.validation_decision` | 무엇을 검증하고 최종 판단하는가? | Practical Validation, Final Review |
| `journey.monitoring` | 선정 후 무엇을 추적하는가? | Portfolio Monitoring |

데이터 준비 journey는 로그 관리 화면이 아니다.
사용자가 어떤 데이터가 왜 필요한지와 owning action surface만 설명한다.

### Unified Search

검색 대상은 사용자-facing catalog만 포함한다.

- 기능명과 화면명
- 상태와 용어
- 사용 흐름
- 증상과 문제 해결
- 한글/영문 alias와 keyword

같은 개념이 Guide와 Glossary에 중복되면 하나의 item으로 반환한다.
기본 ranking은 exact title/alias, prefix, keyword, summary 순이다.
여러 검색어는 모든 token이 item search text에 포함될 때 match한다.

### Detail Contract

모든 상세는 아래 순서로 읽는다.

1. 뜻 또는 목적
2. 어디서 보이는가
3. 어떤 영향을 주는가
4. 다음 행동
5. 관련 항목
6. 가능한 경우 owning surface로 이동

상세 선택과 검색/필터는 React local state에서 처리해 Streamlit rerun을 만들지 않는다.

## Architecture

### `app/services/reference_center.py`

- 사용자-facing canonical catalog를 소유한다.
- catalog schema와 search projection을 만든다.
- current surface / legacy exclusion / destination whitelist drift report를 제공한다.
- Streamlit과 web module을 import하지 않는다.

### `app/web/reference_center.py`

- 단일 Reference page shell이다.
- query parameter의 initial item을 검증한다.
- `navigate_to_surface` event만 처리한다.
- 유효한 destination인지 다시 확인한 뒤 `st.switch_page` 또는 기존 page-target 경계로 이동한다.

### `app/web/reference_center_react_component.py`

- `component_static` 존재 여부를 확인한다.
- Python payload를 JSON-safe value로 변환한다.
- `reference_center_v1` component를 선언하고 event dict만 반환한다.

### `app/web/streamlit_components/reference_center_workbench/`

- 통합 검색, filter, journey card, result list, detail drawer/sheet를 렌더링한다.
- DB, registry, provider, Streamlit session state를 직접 읽지 않는다.
- 검색과 상세 선택은 client-local state다.
- 외부 화면 이동만 typed intent로 반환한다.

### Contextual Help

기존 contextual help service는 stable Reference item ID를 사용하도록 바꾼다.

- 기존 `/guides`, `/glossary` target을 `/reference?item=<id>`로 통합한다.
- Backtest Analysis, Practical Validation, Final Review, Portfolio Monitoring coverage를 유지한다.
- Overview, Institutional Portfolios, Ingestion coverage를 추가한다.
- 각 help item은 실제 catalog item과 허용 destination에 연결돼야 한다.

## Payload Contract

Top-level payload:

```text
schema_version = reference_center_v1
component = ReferenceCenterWorkbench
filters
journeys
items
initial_item_id
empty_state
```

Common item fields:

```text
id
kind
category
title
summary
aliases
keywords
related_surfaces
meaning
impact
next_action
related_item_ids
destination
```

허용 `kind`는 `journey`, `concept`, `playbook` 세 가지다.
화면 기능 설명도 독립 문서 유형을 추가하지 않고 관련 journey 또는 concept로 표현한다.
`destination`은 allowlist의 user-facing route만 가질 수 있다.
raw file path, registry path, job identifier를 사용자 navigation destination으로 사용하지 않는다.

## Data Flow

```text
Current product docs / surface contracts
  -> curated user-facing Reference catalog
  -> Streamlit-free search/read model
  -> reference_center_v1 payload
  -> React local search/filter/detail
  -> optional navigate_to_surface intent
  -> Python destination validation
  -> owning product surface
```

`GLOSSARY.md`는 내부 durable document로 유지하지만 payload 생성 시 자동 파싱하지 않는다.
사용자-facing 항목은 product review를 거친 curated catalog만 사용한다.

## Deep Link Contract

다른 화면은 stable item ID로 Reference를 연다.

```text
/reference?item=status.not_run
/reference?item=journey.institutional_portfolios
/reference?item=playbook.final_review_candidate_missing
```

initial item이 없거나 잘못됐으면 Reference home으로 fallback한다.
React 내부 선택마다 query parameter를 갱신하지 않는다.
따라서 local drawer/sheet는 명시적 닫기 action으로 닫고 browser history entry를 만들지 않는다.
다른 화면에서 deep link로 들어온 경우의 browser back은 원래 제품 화면으로 돌아간다.

## Error And Empty States

- zero result: 추천 검색어와 6개 journey로 돌아가는 action을 표시한다.
- invalid deep link: 기본 화면과 변경/삭제 안내를 표시한다.
- invalid destination: 이동하지 않고 현재 상세와 경고를 유지한다.
- missing/failed React build: 기존 대형 Guide fallback을 렌더링하지 않고 compact load error를 표시한다.
- invalid catalog item: UI payload에서는 해당 item만 제외할 수 있지만 자동 contract test는 실패해야 한다.
- empty catalog: 검색 UI 대신 명확한 unavailable state를 표시한다.

## Content Drift Guard

필수 current surface:

- Overview
- Institutional Portfolios
- Ingestion
- Backtest Analysis
- Practical Validation
- Final Review
- Portfolio Monitoring

Overview 관련 current concept에는 Market Context, Market Movers, Futures Macro,
Sentiment, Events와 Market Context 내부 Economic Cycle을 포함한다.

사용자 catalog 금지 예시:

- Futures Monitor
- Macro Thermometer
- Candidate Review
- Portfolio Proposal
- Selected Portfolio Dashboard
- Main Worktree / Sub Worktree / Phase / Task / Fixture

모든 item은 unique ID, kind, category, summary, meaning/purpose, impact, next action을 가져야 한다.
모든 related item과 contextual help ID는 실제 item을 참조해야 한다.

## Testing

### Python

- catalog schema / unique ID / required field
- search projection과 multi-token match
- current surface coverage / legacy term exclusion
- related item / contextual help referential integrity
- deep-link initial item validation
- destination allowlist와 event validation
- Streamlit-free service boundary
- JSON-safe component payload와 component availability

### React

- exact/prefix/keyword ranking
- scope filter와 zero result
- journey selection / result selection / related item navigation
- initial item deep link
- invalid/empty payload state
- drawer close와 520px sheet presentation
- search/detail local state가 rerender에도 유지됨

### Build And Distribution

- TypeScript typecheck
- Vitest
- Vite production build
- `component_static` Git distribution contract
- Python py_compile / focused unit tests / `git diff --check`

### Browser QA

- desktop, 900px, 420px
- 검색 -> 필터 -> 상세 열기
- 6개 journey card 접근
- contextual deep link initial detail
- valid product surface navigation
- drawer/sheet 명시적 close
- contextual deep link에서 browser back으로 origin surface 복귀
- text overlap, clipping, horizontal overflow 없음

QA screenshot은 generated artifact로 두고 명시 요청 없이는 commit하지 않는다.

## Migration And Removal

새 catalog와 React component가 검증된 후 아래 legacy primary surface를 제거한다.

- `Reference > Guides` page entry
- `Reference > Glossary` page entry
- `Portfolio Selection Journey` mode
- `app/web/reference_guides.py` active renderer
- markdown glossary auto-render path
- old catalog 중 새 service로 승격되지 않은 사용자 UI path

내부 `GLOSSARY.md`와 과거 task/research 기록은 삭제하지 않는다.

## Acceptance Criteria

- 상단 navigation에 `Reference` 하나만 있다.
- 첫 viewport에서 검색이 hero/runtime/build보다 먼저다.
- 6개 current journey가 모두 검색/선택 가능하다.
- legacy·개발자 용어와 로그 관리 기능이 사용자 Reference에 없다.
- contextual help deep link가 정확한 item을 연다.
- React는 검색/상세을 local state로 처리하고 Python은 navigation intent만 검증한다.
- focused Python/React/build tests와 actual responsive Browser QA가 통과한다.
