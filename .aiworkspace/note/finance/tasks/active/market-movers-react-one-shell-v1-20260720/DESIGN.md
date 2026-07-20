# Market Movers React One-Shell V1 Design

Status: Approved A-Option Implementation
Last Updated: 2026-07-20

## Approved Source

- `.aiworkspace/note/finance/researches/active/2026-06-market-movers-redesign-v2-benchmark/RECOMMENDATION.md`
- 사용자가 A안과 재무 `보고 주기 / factor` 독립 grouping을 승인했다.

## Architecture

```text
DB-backed market/group/research loaders
  -> market_movers_decision_payload_v1
  -> pure decision UI adapter
  -> MarketMoversDecisionWorkbench React shell
  -> selected symbol / bounded action event
  -> Streamlit session or ingestion job -> DB -> rerun
```

- Python은 ranking, group state, Top 3, financial factor와 unavailable 이유를 계산한다.
- React는 presentation state와 사용자 선택만 소유한다.
- global coverage/period/ranking 변경과 selected symbol 변경은 Streamlit event로 보낸다.
- group mode/period/group, research tab, financial frequency/factor는 payload 안에서 local state로 전환한다.

## Layout

1. compact hero + command line + trust line
2. desktop 62/38 ranking/breadth workbench
3. selected quick research strip
4. expandable research with price, financial, events tabs
5. method/source disclosure

## Financial Controls

- 보고 주기: `분기 | 연간`
- factor group: `손익 | 수익성 | 안정성`
- factor button: group 안에서 한 개 선택
- unavailable factor는 disabled이며 available/excluded count 근거를 표시한다.
- 단위가 다른 factor를 한 chart에 겹치지 않는다.

## Error Handling

- BLOCKED는 ranking을 현재 결과처럼 노출하지 않는다.
- PARTIAL은 metric denominator와 primary action만 compact하게 표시한다.
- group/bellwether가 없으면 그 section만 local empty state로 둔다.
- 재무 factor points가 없으면 chart 대신 이유를 표시한다.
- schema mismatch는 React empty state를 표시하고 Python legacy fallback으로 계산을 재구성하지 않는다.
