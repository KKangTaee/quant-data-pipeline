# Phase 8 Investability Data Evidence Expansion Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

Phase 0~7은 Backtest -> Practical Validation -> Final Review -> Selected Dashboard 흐름을 더 엄격한 investability decision workflow로 바꿨다.
하지만 데이터 근거 자체가 부족하면 gate가 엄격해도 실제 판단 효력은 제한된다.

특히 current listing snapshot, asset profile, SEC Form 25 delisting evidence는 각각 의미가 다르다.
current listing snapshot은 현재 살아 있는 종목 목록이고, Form 25는 delisting / withdrawal 근거이며, 둘 다 complete historical universe membership을 단독으로 증명하지 않는다.

Phase 8은 데이터 저장을 늘리기 위한 phase가 아니다.
실전 검토에서 중요한 survivorship bias, delisting, ticker change, merger, historical membership 근거를 DB-backed evidence로 정리해 Data Coverage Audit과 Final Review gate가 더 정확하게 판단하도록 만드는 phase다.

## Phase Goal

Data Coverage / Validation Efficacy / Final Review가 symbol lifecycle evidence를 더 엄격하고 구체적으로 읽도록 한다.

완료 상태는 아래와 같다.

- symbol lifecycle table이 delisting뿐 아니라 future ticker change / merger / historical membership source를 받을 수 있다.
- current snapshot, official delisting evidence, historical membership evidence, computed evidence를 혼동하지 않는다.
- survivorship PASS는 requested period를 덮는 실제 historical / computed lifecycle evidence가 있을 때만 가능하다.
- source가 불완전하면 PASS로 추론하지 않고 REVIEW / NEEDS_INPUT으로 남긴다.
- 수집 데이터는 DB에 저장하고 workflow JSONL에는 compact audit evidence만 남긴다.

## Scope

포함한다.

- Phase 8 공식 phase board 생성
- 기존 Historical Universe Survivorship / SEC Form 25 작업을 Phase 8 선행 완료 slice로 편입
- symbol lifecycle schema에 event semantics를 추가
- Form 25 / current listing snapshot row가 event type과 event date를 명시하게 정리
- historical membership / ticker change / merger source 후속 task 분해
- Data Coverage Audit이 lifecycle evidence를 계속 compact하게 읽도록 유지

포함하지 않는다.

- 새 workflow JSONL registry 생성
- 사용자 메모 / preset 저장
- broker 연결, 주문 지시, auto rebalance
- UI에서 SEC / provider / web 직접 fetch
- 유료 데이터 소스 전제
- complete commercial-grade corporate action database 구현

## Development Flow

| Phase Slice | Goal | Status |
| --- | --- | --- |
| 8-0 | Phase 8 board open / previous lifecycle work 편입 | Complete |
| 8-1 | Symbol lifecycle event field foundation | Implementation complete |
| 8-2 | Historical membership / ticker action source 후보 조사 | Pending |
| 8-3 | Free / official source ingestion slice 선정 | Pending |
| 8-4 | Symbol change / merger mapping collector or import path | Pending |
| 8-5 | Data Coverage Audit lifecycle evidence scoring refinement | Pending |
| 8-6 | Phase 8 integrated QA / closeout | Pending |

## Done Criteria

- Phase 8 문서가 앞으로 사용할 공식 phase 기준을 제시한다.
- `nyse_symbol_lifecycle` row가 event semantics를 담을 수 있다.
- SEC Form 25 row는 `event_type=delisting`으로 저장된다.
- current listing snapshot row는 historical membership proof가 아니라 `event_type=listing_observed` partial evidence로 저장된다.
- Data docs가 lifecycle row의 의미와 한계를 설명한다.
- 관련 service contract test와 compile check가 통과한다.

## Carry Forward To Later Phases

- Phase 9: cost / slippage / turnover / liquidity / capacity를 backtest realism engine에 반영한다.
- Phase 10: walk-forward / out-of-sample / regime split 검증을 강화한다.
- Phase 11: portfolio construction risk controls를 강화한다.
- Phase 12: selected monitoring / recheck operations를 정리한다.
- Phase 13: 전체 1차 hardening cycle closeout을 진행한다.
