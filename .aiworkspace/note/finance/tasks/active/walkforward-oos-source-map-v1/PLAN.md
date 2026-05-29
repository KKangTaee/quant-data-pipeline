# Walk-forward / OOS Source Map V1 Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Phase 10의 목표는 좋은 전체기간 백테스트가 특정 기간이나 국면에만 맞은 결과인지 더 엄격히 확인하는 것이다.
바로 split validation 코드를 추가하기 전에, 현재 Practical Validation / Robustness Lab / runtime replay / Final Review gate가 어떤 curve와 metadata를 읽는지 확인해야 한다.

이 task는 구현 전 source map / gap audit이다.
새 JSONL, 사용자 메모, preset 저장, 주문, 승인, 자동 리밸런싱을 추가하지 않는다.

## Scope

포함한다.

- Practical Validation curve source hierarchy 확인
- existing rolling / OOS / regime / robustness evidence 위치 확인
- Validation Efficacy Audit과 Final Review gate 연결 상태 확인
- Phase 10 다음 구현 task 범위와 test scope 제안

포함하지 않는다.

- walk-forward split engine 구현
- OOS holdout audit row 구현
- regime split calculation 구현
- 새 DB schema
- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance

## Done Criteria

- source map이 task 문서에 정리된다.
- 구현 gap과 다음 task 우선순위가 명확하다.
- Phase 10 task board가 10-1 Complete, 10-2 Next로 갱신된다.
- `git diff --check`와 finance hygiene check가 통과한다.
