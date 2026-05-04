# Post-Selection Final Investment Guide

## 목적

이 문서는 `Backtest > Post-Selection Guide`의 의미와 사용 경계를 설명한다.

Phase35 보정 이후 이 화면은 별도 operating guide registry를 저장하지 않는다.
Final Review에서 저장한 final selection decision을 읽어
사용자가 마지막에 투자 가능성 및 운영 전 지침을 확인하는 화면이다.

## 쉽게 말하면

Final Review는 "최종 판단을 기록하는 곳"이다.
Post-Selection Guide는 "그 판단을 보고 실제 투자 후보로 읽을 수 있는지 확인하는 곳"이다.

## 입력 source

기본 입력은 아래 파일이다.

```text
.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl
```

Phase35 선택 대상은 아래 조건을 만족하는 final review record다.

- `decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO`
- 신규 row: `phase35_handoff.handoff_route = READY_FOR_FINAL_INVESTMENT_GUIDE`
- 기존 QA row: `READY_FOR_POST_SELECTION_OPERATING_GUIDE`도 읽기 호환

## 최종 판단 읽는 법

| Final Review decision route | Post-Selection Guide에서 읽는 의미 |
|---|---|
| `SELECT_FOR_PRACTICAL_PORTFOLIO` | 투자 가능 후보 |
| `HOLD_FOR_MORE_PAPER_TRACKING` | 내용 부족 / 관찰 필요 |
| `REJECT_FOR_PRACTICAL_USE` | 투자하면 안 됨 |
| `RE_REVIEW_REQUIRED` | 재검토 필요 |

## 화면에서 확인하는 것

- source final decision id
- source type / source id
- selected components
- target weight total
- evidence route
- capital boundary
- rebalancing cadence
- reduce / stop trigger
- re-review trigger
- live approval disabled
- order instruction disabled

## 저장 경계

Phase35는 새 파일을 만들지 않는다.

아래 파일은 사용하지 않는다.

```text
.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl
```

이전 구현에서는 별도 operating guide registry를 만들었지만,
사용자 피드백 이후 Final Review의 final decision을 원본 판단으로 유지하고
Phase35는 read / preview 화면으로 보정했다.

## 기본 흐름

```text
Backtest / Compare
  -> Candidate Review
  -> Portfolio Proposal
  -> Final Review
     -> final selection decision 기록
  -> Post-Selection Guide
     -> 투자 가능성 / 운영 전 지침 확인
```

## 중요한 경계

- 이 화면은 final decision을 다시 저장하지 않는다.
- 이 화면은 live approval이 아니다.
- 이 화면은 broker order가 아니다.
- 이 화면은 자동매매 지시가 아니다.
- 이 화면은 수익 보장이 아니다.
- 이 화면은 사용자가 실전 후보 포트폴리오를 운영 전 검토할 때 따라갈 확인표다.
