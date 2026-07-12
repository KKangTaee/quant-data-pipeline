# Final Review Guidance Actionability V1

## 이걸 하는 이유?

Final Review의 Monitoring 방향 가이드와 확인 필요 영역이 저장 evidence를 보여주고는 있지만, 사용자가 무엇을 판단하고 다음에 무엇을 해야 하는지까지 연결하지 못한다. 기술 trace와 Level2 보강 문구가 전면에 노출되고, 10개 패턴이 모두 비슷한 참고 문장으로 표시되는 문제를 해결한다.

## 단계

1. 10개 패턴의 적용 여부, 판정 상태, evidence trace 계약을 정형화한다.
2. Monitoring 방향 가이드를 현재 진단, 의미, 변화 조건, 다음 행동 중심으로 개편한다.
3. Level2에서 끝낼 일과 Final Review에서 결정할 일을 분리한다.
4. 해석 4개 항목을 총평 바로 아래의 세로형 사용자 문장으로 재구성한다.
5. service/contract test, React build, py_compile, diff check, Browser QA와 문서 동기화를 수행한다.

## 완료 조건

- 적용 가능한 패턴만 첫 화면에 표시되고 나머지는 상세 근거에서 확인할 수 있다.
- 기술 source path와 기준일은 접힌 상세 정보로 이동한다.
- Final Review 항목마다 의미와 사용자 행동이 명확하다.
- Level2 보강 지시가 Final Review의 직접 행동으로 노출되지 않는다.
- 해석 4개 행이 총평 직후에 표시된다.
- 저장 evidence만 사용하며 provider fetch, 재검증, registry write를 추가하지 않는다.
