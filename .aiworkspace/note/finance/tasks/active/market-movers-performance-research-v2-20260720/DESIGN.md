# Market Movers Performance And Research V2 Design

Status: Approved
Last Updated: 2026-07-20

## 이걸 하는 이유?

현재 Market Movers 통합 화면은 캐시가 비면 `sector / industry × daily / weekly / monthly` 여섯 확산 snapshot을 모두 선계산한다. DB-only 계산인데도 실제 첫 진입이 약 46초 걸렸고, Top Rank 선택도 Streamlit 전체 rerun을 일으켜 120초 cache 만료 후 같은 계산을 반복한다. 상세 조사는 가격 hover가 없고, 재무 이력을 연간 8개·분기 32개로 잘라 표시하며, local tab 변경 뒤 iframe 높이 갱신을 놓쳐 하단이 잘릴 수 있다. 새 one-shell은 기존 수동 갱신 action, 현재/기준/최종 갱신 시각과 뉴스·공시 근거도 렌더링하지 않는다.

이번 개편은 진단값을 늘리는 작업이 아니라 사용자가 `무엇이 움직였는지 → 어디까지 확산됐는지 → 선택 종목의 가격·재무·사건 근거가 무엇인지`를 기다림과 화면 단절 없이 끝내게 만드는 실사용 개선이다.

## Approved Scope

### 1. 점진 로딩과 선택 경계

- 첫 진입은 현재 선택한 group/period 한 건만 계산한다. 기본은 `sector / daily`다.
- breadth의 다른 조합은 사용자가 전환할 때 bounded Streamlit event로 요청한다.
- 공통 market date window 계산은 group 종류와 무관하게 재사용하고 cache TTL을 현재 120초보다 길게 유지한다.
- Top Rank 선택은 React에서 quick research를 즉시 바꾸고, Python에서는 선택 종목 research만 갱신한다. 이미 로드된 breadth context를 다시 여섯 건 계산하지 않는다.
- 외부 provider 수집은 첫 진입에서 실행하지 않는다.

### 2. 상단 상태와 수동 갱신

- `현재 시각`, `시장 기준일`, `데이터 기준 시각`, `마지막 화면 갱신`을 서로 다른 의미로 표시한다.
- Daily primary action은 `일중 스냅샷 수동 갱신`, weekly/monthly primary action은 `가격 이력 수동 갱신`이다.
- `유니버스 기준 갱신`은 secondary action으로 유지한다.
- 실행 job/raw row 진단 패널은 새로 만들지 않는다. 기존 progress/notice만 사용한다.

### 3. 시장 확산과 semantic return color

- toolbar는 한 줄의 두 labeled group으로 구분한다: `분류 [섹터 | 산업] │ 기간 [일 | 주 | 월]`.
- 좁은 폭에서는 group 단위로 두 줄 wrap하되 label과 divider가 구분을 유지한다.
- 수익률은 양수 green, 음수 red, 0 neutral을 적용하고 `+/-` 기호를 보존한다.
- 적용 대상은 ranking, breadth 상대수익률, 선택 종목 quick facts, 가격 chart readout/tooltip이다.

### 4. 가격·모멘텀

- SVG pointer 위치에서 가장 가까운 point를 선택한다.
- hover/focus 상태에 날짜, 가격, 정규화 수익률을 표시하고 vertical guide와 active dot을 제공한다.
- YTD/최근/범위 최고/범위 최저 readout은 의미별 tint와 return tone을 사용한다.

### 5. 재무 최대 10년과 chart mode

- annual은 최대 10개, quarterly는 최대 40개를 사용한다. 저장된 데이터가 더 적으면 가능한 rows를 모두 표시한다.
- currency/currency-per-share factor는 bar 기본, percent/ratio factor는 line 기본으로 시작한다.
- 사용자는 `막대 | 선` toggle로 같은 factor의 표현을 바꿀 수 있다.
- bar와 line은 동일 point/source를 사용하며 별도 dual-axis overlay는 만들지 않는다.
- `ResizeObserver`가 document/root 높이 변화를 관찰해 tab, factor, chart mode, viewport 변화 뒤 Streamlit iframe 높이를 동기화한다.

### 6. 뉴스·공시 근거

- SEC는 이미 저장된 EDGAR filing ledger를 우선 읽어 최신 10-K/10-Q 등 compact metadata와 link를 표시한다.
- 뉴스는 기존 manual investigation metadata 경로를 selected symbol에 연결하며 자동 조회하지 않는다.
- 뉴스 조회 action은 사용자가 명시적으로 누를 때만 bounded Python action을 실행하고 세션 전용 metadata를 화면에 반영한다.
- 자동 원인 판정, 매매 신호, 기사 본문 저장은 포함하지 않는다.

## Architecture

```text
Streamlit controls/session
  ├─ market snapshot + current breadth key cache
  ├─ selected-symbol research cache
  └─ explicit refresh / evidence actions
          ↓
market_movers_decision_workbench_v2 payload
          ↓
React one-shell
  ├─ timestamp + manual actions
  ├─ ranking + lazy breadth controls
  └─ quick/detail research (price / financial / events)
```

Python이 DB/read-model과 bounded action을 소유하고 React는 local visualization과 event를 소유한다. UI render 중 provider fetch는 금지한다.

## Error And Empty States

- 요청한 breadth가 아직 없으면 해당 card 안에 loading/empty state를 표시하고 ranking은 유지한다.
- research가 아직 선택 symbol과 일치하지 않으면 quick facts는 ranking row를 유지하고 상세 panel만 loading 상태를 표시한다.
- 뉴스 row가 없으면 `저장/조회된 뉴스 근거 없음`과 explicit 조회 action을 표시한다.
- SEC ledger가 없으면 공시 없음과 데이터 기준을 표시한다.
- chart point가 2개 미만이면 이유가 있는 local empty state를 표시한다.

## Acceptance Criteria

1. cold entry가 여섯 group snapshot을 선계산하지 않는다.
2. Top Rank 선택이 breadth 여섯 건을 다시 계산하지 않는다.
3. 현재/시장/데이터/화면 갱신 시각과 manual refresh action이 상단에서 구분된다.
4. breadth controls가 labeled group으로 분리되고 positive/negative return color가 전 화면에서 일관된다.
5. 가격 hover가 날짜·가격·수익률을 표시한다.
6. 재무는 최대 annual 10 / quarterly 40 points와 bar/line toggle을 제공한다.
7. 상세 tab 변경 후 하단이 잘리지 않는다.
8. 뉴스·공시 탭이 실제 DB/session metadata와 action을 표시하며 자동 causal judgement를 만들지 않는다.
9. focused tests, React build, Browser desktop/narrow QA를 통과한다.
