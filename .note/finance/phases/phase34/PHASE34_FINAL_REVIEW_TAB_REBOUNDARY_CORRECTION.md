# Phase 34 Final Review Tab Reboundary Correction

## 이 문서는 무엇인가

Phase 34 구현 중 사용자가 제기한 UX / 제품 경계 이슈를 반영한 보정 작업 기록이다.

## 쉽게 말하면

기존 구현은 `Portfolio Proposal` 탭 안에 proposal 저장, paper ledger 저장, final decision 저장이 이어져 있어
사용자 입장에서는 "왜 계속 저장 버튼이 반복되는가"로 읽혔다.

이번 보정은 그 흐름을 바꿔서:

- `Portfolio Proposal`은 포트폴리오 초안 작성 / 저장까지만 맡고
- `Final Review`는 검증 근거, robustness 질문, paper observation 기준, 최종 판단 기록을 맡게 한다.

## 왜 필요한가

- 최종 실전 후보 선정은 포트폴리오 초안 작성과 성격이 다르다.
- paper observation은 현재 main flow에서 별도 ledger 저장 버튼으로 강제할 필요가 없다.
- 사용자는 "초안을 저장한다"와 "최종 검토 결과를 기록한다"만 구분하면 된다.
- 저장 버튼이 여러 번 반복되면 실제 투자 승인이나 주문 지시처럼 오해될 수 있다.

## 변경된 원칙

1. Portfolio Proposal 탭
   - 단일 후보 직행 가능성 확인
   - 다중 후보 proposal draft 작성 / 저장
   - 저장된 proposal의 monitoring / feedback / raw JSON 확인
   - Final Review로 이동

2. Final Review 탭
   - 단일 current candidate 또는 저장된 proposal 선택
   - validation / robustness / stress 질문 확인
   - paper observation 기준 확인
   - `최종 검토 결과 기록`으로 선정 / 보류 / 거절 / 재검토 판단 저장

3. Paper Ledger
   - 기존 JSONL helper와 registry는 호환성 / 운영 기록 artifact로 유지한다.
   - 이번 사용자-facing main flow에서는 별도 `Save Paper Tracking Ledger`를 필수 단계로 요구하지 않는다.
   - 관찰 기준은 final review record의 `paper_tracking_snapshot` 안에 포함한다.

## 이 보정 후 좋아지는 점

- 사용자가 Phase31~34를 "계속 저장하는 단계"로 느끼지 않는다.
- 최종 검토가 `Portfolio Proposal` 탭 안에 묻히지 않고 독립 탭으로 보인다.
- Phase35는 저장된 final review record를 읽어 운영 가이드로 이어갈 수 있다.
- live approval / order instruction 경계가 더 분명해진다.

## QA에서 확인할 것

- `Backtest > Portfolio Proposal`에서 `Save Paper Tracking Ledger`와 `Save Final Selection Decision`이 주 흐름에 노출되지 않는지
- `Backtest > Final Review`에서 `Paper Ledger Save = Not Required`가 보이는지
- 최종 저장 액션이 `최종 검토 결과 기록` 하나로 읽히는지
- 저장된 record가 live approval이나 order instruction으로 읽히지 않는지

## 한 줄 정리

이번 보정은 Phase 34의 핵심을 "또 하나의 저장 단계"가 아니라
**최종 검토 전용 탭에서 검증 / 관찰 / 판단을 하나로 묶어 기록하는 흐름**으로 재정렬한 작업이다.
