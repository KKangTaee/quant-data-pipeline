# Phase 21 Next Phase Preparation

## 이 문서는 무엇인가
- `Phase 21` deep validation이 끝난 뒤,
  어떤 질문으로 다음 phase를 여는 것이 자연스러운지 정리하는 handoff 문서다.

## handoff 상태

- `Phase 21` manual validation은 완료되었다.
- `Phase 22`는 proposal이 아니라 active main phase로 열어도 되는 상태다.
- 다음 작업은 portfolio-level candidate를 무엇으로 정의할지 먼저 정리한 뒤,
  representative weighted portfolio를 실제 candidate pack으로 다시 다루는 것이다.

## 현재 기준에서 예상되는 다음 질문

### 1. portfolio-level candidate construction을 바로 열 것인가

- `Phase 21`에서 weighted / saved portfolio bridge까지 검증하면,
  다음 질문은 자연스럽게
  **"이제 portfolio-level candidate를 별도 phase로 본격화할 것인가"**
  로 이어질 가능성이 크다.

### 2. quarterly prototype productionization을 언제 올릴 것인가

- 지금까지는 annual strict family가 main track이었다.
- `Phase 21`이 annual strict family를 다시 고정해주면,
  그 다음엔 quarterly prototype을 언제 practical lane으로 올릴지
  더 현실적으로 판단할 수 있다.

### 3. new strategy expansion을 지금 열어도 되는가

- `Phase 21` 결과가 current strongest family를 충분히 고정해주면,
  그 다음에는 새로운 전략 family를 다시 늘릴 여지가 커진다.
- 반대로 validation 결과가 많이 흔들리면,
  expansion보다 current family 정리가 더 우선일 수 있다.

## 현재 기준 추천 해석

- `Phase 21` 결과를 보면,
  다음 main phase는 `Phase 22` portfolio-level candidate construction이 가장 자연스럽다.
- 이유:
  - annual strict family current anchor는 모두 유지됐다.
  - lower-MDD alternative들은 의미 있지만 아직 representative replacement는 아니다.
  - representative weighted portfolio는 `28.66% / -25.42% / Sharpe 1.51`로 의미 있는 조합 결과를 냈다.
  - saved portfolio replay도 exact match로 재현되어 workflow 신뢰성이 확인됐다.
- 따라서 다음 순서는 아래처럼 읽는 것이 좋다.
  - `Phase 22` portfolio-level candidate construction
  - `Phase 23` quarterly / alternate cadence productionization
  - `Phase 24` new strategy expansion
  - `Phase 25` pre-live operating system

## 한 줄 정리
- `Phase 21` 이후에는, 새 단일 전략을 더 찾기보다
  **검증된 annual strict 후보들을 portfolio-level candidate로 어떻게 올릴지**
  를 먼저 보는 것이 맞다.
