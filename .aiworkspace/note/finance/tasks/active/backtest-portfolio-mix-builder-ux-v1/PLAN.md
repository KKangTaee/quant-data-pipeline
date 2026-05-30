# Backtest Portfolio Mix Builder UX V1

Status: Active
Started: 2026-05-30

## Goal

`Backtest Analysis > Portfolio Mix Builder`에서 component 실행 후 결과가 지나치게 크게, 많이, 원본 표 중심으로 노출되는 문제를 줄이고, 사용자가 "component 실행 -> weight 구성 -> mix 후보 판단 -> Practical Validation handoff" 순서로 읽을 수 있게 UI를 정리한다.

## 이걸 하는 이유?

Portfolio Mix Builder는 여러 전략을 비교 분석하는 화면이 아니라, 여러 component 전략을 하나의 mix 후보로 만드는 화면이다. 그런데 기존 화면은 `구성 포트폴리오 실행 결과`와 `구성 포트폴리오 실행 상세`가 중복되고, 9개 tab과 원본 summary table이 한꺼번에 보여 사용자가 다음 행동을 이해하기 어렵다.

## Scope

- `app/web/backtest_compare.py` 안의 Portfolio Mix Builder 화면 구조와 표시 순서 개선
- component 실행 결과를 summary-first로 표시하고 raw/detail은 접힘 영역으로 낮춤
- mix 후보 판단과 Practical Validation handoff의 위치와 의미를 더 선명하게 표시
- scoped CSS / Streamlit layout helper 사용

## Out Of Scope

- backtest 계산 로직 변경
- 새 DB / JSONL 저장 기능 추가
- saved mix persistence 정책 변경
- Practical Validation / Final Review 검증 기준 변경
- 브로커 주문, live approval, 자동 리밸런싱

## Stop Condition

- Portfolio Mix Builder component result section이 중복 heading 없이 표시된다.
- component result tab 수가 줄고, raw table은 기본 접힘 처리된다.
- mix 후보 판단 board가 먼저 결론을 보여주고 criteria/detail은 접힘 처리된다.
- focused compile/check와 browser smoke를 통과하거나 미실행 이유를 기록한다.
