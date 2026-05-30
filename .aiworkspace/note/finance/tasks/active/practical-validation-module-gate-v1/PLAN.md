# Practical Validation Module Gate V1 Plan

Status: Active
Created: 2026-05-30

## 이걸 하는 이유?

Practical Validation은 Backtest Analysis에서 넘어온 후보를 Final Review로 보낼 수 있는지 판단하는 2단계다.
현재 화면은 많은 진단과 audit을 보여주지만, 어떤 검증이 후보 성격에 따라 필수인지, 어떤 것은 참고인지, 어떤 것이 다음 단계 gate를 막는지 한눈에 드러나지 않는다.

이번 작업의 목적은 Practical Validation을 모듈형 검증 흐름으로 재정리하는 것이다.
포트폴리오 특성과 검증 프로필에 따라 필요한 검증을 분류하고, 필수 검증이 준비됐을 때만 검증 결과를 저장하며 Final Review로 이동하게 만든다.

## Scope

- 선택 후보와 재검증 결과의 날짜 / 성과 숫자 표시를 사람이 읽기 좋은 형식으로 정리한다.
- 검증 프로필 copy와 threshold 의미를 명확히 한다.
- source traits와 validation module plan을 만들어 필수 / 조건부 / 참고 검증을 구분한다.
- Final Review 이동 gate를 module result 기반으로 강화한다.
- 기존 registry / saved / live approval / order / auto rebalance 경계는 유지한다.

## Out Of Scope

- 새 JSONL registry 생성
- 새 provider connector 또는 DB schema 구현
- Final Review 자체의 최종 판단 정책 변경
- broker order, live approval, account sync, auto rebalance
- registry / saved / generated artifact commit

## Done Criteria

- Practical Validation result에 module plan과 final review gate summary가 포함된다.
- UI가 필수 검증 / 조건부 검증 / 후속 참고 검증을 분리해서 보여준다.
- 최신 재검증이 필요한 source는 미실행 상태에서 Final Review 이동이 차단된다.
- 날짜는 date-only, CAGR / MDD는 소수 둘째 자리 percent로 표시된다.
- focused service contract tests와 compile checks를 통과한다.
