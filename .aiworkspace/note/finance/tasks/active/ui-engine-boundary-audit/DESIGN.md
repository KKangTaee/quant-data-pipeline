# UI Engine Boundary Audit Design

Status: Active
Created: 2026-05-19

## 이걸 하는 이유?

이 task의 design은 새 코드를 설계하는 문서가 아니라, 분리 기준을 흔들리지 않게 잡는 audit 기준이다.
첫 구현에서 너무 많은 책임을 한 번에 옮기면 Streamlit UI 동작, history 저장, registry handoff, runtime dispatch가 동시에 바뀌어 검증하기 어려워진다.

따라서 audit design은 `UI가 계속 가져야 하는 책임`과 `service로 먼저 옮길 책임`을 분리해, 다음 task가 작은 단위로 안전하게 시작되도록 한다.

## Boundary Questions

| Question | Decision |
| --- | --- |
| UI framework를 바꿀 것인가? | No. 현재 phase에서는 Streamlit을 유지한다. |
| `finance/*` engine을 다시 설계할 것인가? | No. 이미 engine / strategy / transform / performance 책임이 존재하므로 재사용한다. |
| 새 boundary 위치는 어디인가? | `app/web`과 runtime / engine 사이의 `app/services` layer다. |
| 첫 구현에서 어디까지 옮길 것인가? | Single Backtest runtime dispatch, elapsed timing, error normalization까지만 service로 옮긴다. |
| UI에 남길 것은 무엇인가? | form render, spinner, session state write, history append, success / warning render다. |

## Service Eligibility Rule

다음 조건을 만족하는 코드만 첫 service extraction 후보로 본다.

- Streamlit 없이 실행할 수 있다.
- 입력 payload와 결과 bundle로 표현할 수 있다.
- UI session state key를 직접 알 필요가 없다.
- registry JSONL append contract를 직접 바꾸지 않는다.
- `finance/*` strategy behavior를 변경하지 않는다.

## First Task Handoff

다음 구현 task는 `backtest-execution-service-boundary`로 연다.

예상 변경:

- create `app/services/backtest_execution.py`
- modify `app/web/backtest_single_runner.py`

초기 service는 성공 / 입력 오류 / 데이터 오류 / 예기치 못한 오류를 normalized result로 반환하고, Streamlit render와 상태 저장은 기존 UI 파일에 남긴다.
