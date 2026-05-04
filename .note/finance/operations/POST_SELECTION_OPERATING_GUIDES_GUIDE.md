# Post-Selection Operating Guides Guide

## 목적

이 문서는 `.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl`의 의미와
`Backtest > Post-Selection Guide` 사용 경계를 설명한다.

## 쉽게 말하면

Final Review에서 최종 실전 후보로 고른 포트폴리오를
"어떻게 운영할지" 정리한 기록이다.

## 왜 필요한가

- 최종 후보 선정만으로는 실제 운영 기준이 부족하다.
- 사용자는 리밸런싱, 축소, 중단, 재검토 기준을 한곳에서 확인해야 한다.
- 운영 기준은 final decision 원본을 덮어쓰지 않고 별도 append-only 기록으로 남긴다.

## 저장 위치

```text
.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl
```

첫 운영 가이드를 기록할 때 파일이 생성된다.
이 파일은 로컬 운영 artifact이므로 보통 commit하지 않는다.

## 입력 source

Phase35 운영 가이드 대상은 아래 조건을 만족하는 final review record다.

- `decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO`
- `phase35_handoff.handoff_route = READY_FOR_POST_SELECTION_OPERATING_GUIDE`

보류 / 거절 / 재검토 record는 operating guide 대상이 아니다.

## 주요 필드

- `guide_id`: 운영 가이드 id
- `source_decision_id`: 원본 Final Review decision id
- `target_components`: 운영 대상 component와 target weight
- `operating_policy`: 자본 경계, 리밸런싱, 축소, 중단, 재검토 기준
- `guide_readiness_snapshot`: 운영 가이드 기록 가능 여부와 blocker
- `post_selection_handoff`: 저장된 guide가 기본 흐름 완료 상태인지 표시
- `live_approval`: 항상 `false`
- `order_instruction`: 항상 `false`

## 사용자 흐름

```text
Backtest > Final Review
  -> SELECT_FOR_PRACTICAL_PORTFOLIO 기록
  -> Backtest > Post-Selection Guide
  -> selected final decision 선택
  -> 리밸런싱 / 축소 / 중단 / 재검토 기준 작성
  -> 운영 가이드 기록
  -> 기록된 운영 가이드 확인
```

## 중요한 경계

- 이 기록은 live approval이 아니다.
- 이 기록은 broker order가 아니다.
- 이 기록은 자동매매 지시가 아니다.
- 이 기록은 수익 보장이 아니다.
- 이 기록은 사용자가 실전 후보 포트폴리오를 운영 전 검토할 때 따라갈 기준표다.
