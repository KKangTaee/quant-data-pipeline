# Plan

## Goal

`Operations > Selected Portfolio Dashboard`를 사용자가 먼저 이해하는 3단계 흐름으로 재배치한다.

1. 나의 포트폴리오
2. 포트폴리오 상세 / 전략 구성
3. 모니터 시나리오

## 이걸 하는 이유?

현재 화면은 Final Review handoff, recheck readiness, provider evidence 같은 감사성 정보가 먼저 보여서 사용자가 "내 포트폴리오를 만들고 전략을 담아 지금 상태를 본다"는 핵심 흐름을 바로 이해하기 어렵다. Dashboard는 live approval이나 주문 도구가 아니라 Final Review selected 후보를 담는 사용자 monitoring container여야 한다.

## Scope

- Portfolio Card Shelf와 `+ 새 포트폴리오` 생성 흐름.
- Portfolio별 strategy slot 저장 구조.
- Final Review selected decision 중복 추가 방지 유지.
- strategy slot의 start / end latest mode / balance / memo 입력.
- scenario 실행과 strategy row 저장 분리.
- scenario-first aggregate summary, value curve, strategy comparison, rebalance target table.
- recheck readiness / symbol freshness / provider evidence / deployment readiness / audit 정보는 하단 상세로 이동.
- selected decision registry와 monitoring log는 쓰지 않는다.

## Stop Condition

- Streamlit 화면에서 portfolio shelf가 먼저 보이고, portfolio 선택 후 strategy builder와 monitoring scenario가 이어진다.
- 기존 saved `selected_decision_ids` row도 새 slot 구조로 읽힌다.
- service contract tests and focused compile pass.
- Browser QA screenshot is captured.
