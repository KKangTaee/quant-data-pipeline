# Final Review Decision Surface Consolidation V1

## 이걸 하는 이유?

Final Review 투자 검토서의 하단 근거 탭은 내용과 시각적으로 분리되어 있고, REVIEW trace는 저장된 세부 audit evidence가 있어도 상위 카드와 연결되지 않아 빈 필드로 보인다. 대안 실험은 실행 기능처럼 읽히지만 실제로는 후속 backtest 가설이며, Decision Cockpit과 Final Decision Action은 투자 검토서와 같은 상태를 반복해 최종 판단 흐름을 길게 만든다.

## 단계

1. 하단 탭을 하나의 연결된 shell로 만들고 점수 근거를 압축한다.
2. Level2 REVIEW와 세부 audit evidence를 연결하는 trace 계약을 보강한다.
3. 대안 실험을 적용 가능한 `다음 실험 아이디어`로 재구성한다.
4. 독립 Decision Cockpit을 제거하고 핵심 상태를 간소화한 최종 판단 영역에 통합한다.
5. focused test, React build, py_compile, diff check, Browser QA와 문서 동기화를 수행한다.

## 완료 조건

- 활성 탭과 내용이 하나의 패널로 읽히고 점수 중복이 줄어든다.
- REVIEW 항목이 측정 근거, 파생 근거, 정성 판단, 연결 미완료를 구분한다.
- 다음 실험 아이디어가 현재 판단과 별도 backtest 가설임을 명확히 표시한다.
- Decision Cockpit의 독립 visible surface가 사라지고 최종 판단 저장에 필요한 정보만 남는다.
- React는 표시만 담당하고 gate, evidence adapter, 저장과 registry append는 Python boundary를 유지한다.
