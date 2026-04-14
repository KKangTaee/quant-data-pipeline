# Roadmap Rebase: Phase 18 To Phase 25

## 이 문서는 무엇인가

이 문서는 `Phase 18` 진행 중 시점에서,
앞으로 `Phase 25`까지 어떤 큰 흐름으로 갈지
다시 정리한 **논의용 상위 로드맵 초안**이다.

즉:

- 지금 어디까지 왔는지
- 왜 당장 deep backtest보다 구현이 먼저인지
- `Phase 19 ~ 25`를 어떤 순서로 여는 것이 자연스러운지

를 한 장으로 정리한 문서다.

## 현재 위치 요약

현재 기준으로 이미 확보한 것은 아래와 같다.

- strict annual family의
  - real-money contract
  - promotion / shortlist / deployment surface
  - backtest / compare / history / hub / one-pager / log workflow
- current practical candidates
  - `Value`
  - `Quality`
  - `Quality + Value`
- bounded refinement 결과
  - lower-MDD near-miss와 strongest practical point 정리 완료
- first structural lever 결과
  - `partial cash retention`
  - `defensive sleeve risk-off`
  - `concentration-aware weighting`
- larger structural redesign first slice 결과
  - `next-ranked eligible fill`

하지만 아직 남은 핵심 질문은:

- same-gate lower-MDD exact rescue가 가능한가
- 현재 strongest / near-miss / portfolio bridge를
  더 재현 가능하고 운영 가능하게 묶을 수 있는가
- deep rerun을 다시 열 때
  “기능이 덜 만들어진 상태”가 아니라
  충분히 갖춰진 구조 위에서 돌릴 수 있는가

## 현재 운영 원칙

지금부터는 한동안 아래 원칙으로 가는 것이 맞다.

1. broad deep backtest는 잠시 멈춘다
2. 구현 backlog를 먼저 닫는다
3. 각 구현 slice는 minimal validation만 붙인다
4. structural / operator backlog가 더 정리된 뒤
   integrated deep backtest를 다시 연다

## 제안하는 큰 흐름

### Phase 19. Structural Contract Expansion And Interpretation Cleanup

### 목적

- `Phase 18` first slice 이후 남아 있는
  larger structural redesign 후보를 실제 코드로 더 연결한다
- strict annual family에서
  rejection / risk-off / weighting contract를
  operator가 읽기 쉽게 정리한다

### 핵심 질문

- second slice는 무엇이 가장 타당한가
- current structural levers가 서로 어떻게 충돌하거나 보완되는가
- interpretation / history / meta surface를 충분히 설명적으로 만들 수 있는가

### 주요 산출물

- second / third structural slice implementation
- interpretation cleanup
- history/meta field cleanup
- minimal representative validation

### 한 줄 역할

`Phase 19`는 **구조 레버를 실제 usable contract로 다듬는 phase**다.

---

### Phase 20. Candidate Consolidation And Operator Workflow Hardening

### 목적

- strongest / near-miss 후보를
  compare -> weighted -> saved portfolio 흐름과 더 자연스럽게 연결한다
- single-strategy refinement와 portfolio bridge 사이의 운영 gap을 줄인다

### 핵심 질문

- current strongest candidate를 묶어서 다시 보기 쉽게 만들 수 있는가
- compare / weighted / saved portfolio를
  research artifact가 아니라
  **operator workflow object**로 더 잘 만들 수 있는가

### 주요 산출물

- candidate cards / bundle summary
- saved portfolio usability polish
- compare-to-portfolio bridge cleanup
- current candidate organization UX 보강

### 한 줄 역할

`Phase 20`은 **좋은 후보를 찾는 것만이 아니라,
그 후보를 다시 쓰고 비교하고 저장하는 흐름을 정리하는 phase**다.

---

### Phase 21. Research Automation And Experiment Persistence

### 목적

- 반복되는 refinement / validation / documentation 흐름을
  더 자동화한다
- 현재 plugin / skill / checklist script를
  더 실무적으로 쓸 수 있게 만든다

### 핵심 질문

- 실험 조합과 결과 기록을 더 자동으로 남길 수 있는가
- rerun pack / preset / candidate scenario를 더 재현 가능하게 만들 수 있는가
- Codex workflow를 현재 프로젝트 리듬에 맞게 더 붙일 수 있는가

### 주요 산출물

- experiment preset / scenario persistence
- documentation/checklist automation 보강
- repo-local plugin/skill practical upgrade

### 한 줄 역할

`Phase 21`은 **반복 연구를 더 빠르고 덜 흔들리게 만드는 자동화 phase**다.

---

### Phase 22. Integrated Deep Backtest Validation

### 목적

- `Phase 19 ~ 21`에서 구현을 더 붙인 뒤,
  다시 넓고 깊은 백테스트를 공식적으로 재개한다
- strongest / near-miss / redesigned contract를
  같은 기준으로 다시 검증한다

### 핵심 질문

- 새 구조가 실제로 same-gate lower-MDD rescue를 만드는가
- current strongest candidate가 여전히 strongest인가
- family별로 어느 redesign이 가장 유효한가

### 주요 산출물

- integrated rerun matrix
- family별 comparative validation
- anchor replacement 여부 정리

### 한 줄 역할

`Phase 22`는 **구현을 충분히 쌓아둔 뒤 다시 여는 본격 deep validation phase**다.

---

### Phase 23. Portfolio-Level Candidate Construction

### 목적

- single-strategy strongest candidate를 넘어,
  portfolio-level candidate를 만들 수 있는지 본다
- weighted bundle이 단순 연구용 조합인지,
  더 실전적인 portfolio candidate로 읽을 수 있는지 검토한다

### 핵심 질문

- single-strategy strongest point들을 묶으면
  더 나은 return/MDD tradeoff가 나오는가
- portfolio-level gate / interpretation이 별도로 필요한가

### 주요 산출물

- portfolio candidate design note
- multi-strategy bundle validation
- 필요시 portfolio-level promotion/readiness 초안

### 한 줄 역할

`Phase 23`은 **전략 하나를 넘어서 포트폴리오 단위 후보를 다루기 시작하는 phase**다.

---

### Phase 24. New Strategy Expansion

### 목적

- 기존 strongest family 고도화가 어느 정도 닫힌 뒤,
  다시 새로운 전략 family를 연다
- `quant-research`와 `quant-data-pipeline`을 더 명시적으로 연결한다

### 핵심 질문

- 어떤 새 전략이 current stack과 가장 잘 맞는가
- point-in-time / real-money contract / operator workflow와 자연스럽게 이어지는가

### 주요 산출물

- new strategy shortlist
- research-to-implementation bridge
- first new family implementation

### 한 줄 역할

`Phase 24`는 **새 전략을 다시 늘리는 phase**지만,
기존 기반이 충분히 정리된 뒤에 연다.

---

### Phase 25. Pre-Live Operating System And Deployment Readiness

### 목적

- 찾은 후보를 실제 paper / small-capital trial 관점에서 다루는 운영 체계를 정리한다
- 지금까지 만든
  `promotion / shortlist / probation / deployment`
  surface를 실제 operator workflow로 묶는다

### 핵심 질문

- 후보를 월별/분기별로 어떻게 review할 것인가
- saved portfolio / candidate summary / history를
  실제 운용 준비 루틴으로 연결할 수 있는가
- live 이전에 무엇이 더 필요하고,
  어디까지가 current scope인가

### 주요 산출물

- operator review workflow
- probation / monitoring persistence
- deployment readiness playbook

### 한 줄 역할

`Phase 25`는 **실전 직전 운영 체계를 정리하는 pre-live phase**다.

## 왜 이 순서가 맞는가

이 순서는 아래 이유 때문에 자연스럽다.

1. 지금은 전략을 더 많이 돌리는 것보다
   구조를 더 갖추는 것이 먼저다
2. 구현이 더 정리돼야
   deep rerun도 의미가 더 커진다
3. deep validation이 끝난 뒤에야
   portfolio-level candidate와 new strategy expansion도 덜 흔들린다
4. 마지막에야
   pre-live operator workflow가 현실적인 문서가 된다

## 현재 추천

지금 당장 가장 자연스러운 흐름은:

1. `Phase 18` implementation-first 유지
2. `Phase 19` structural contract expansion
3. `Phase 20` operator workflow hardening
4. `Phase 21` research automation / persistence
5. 그 다음 `Phase 22`에서 deep backtest 재개

## discussion 포인트

아래 3가지는 사용자 확인 후 고정하는 것이 좋다.

1. `Phase 19`를 strict annual structural redesign에 집중할지
2. `Phase 20` operator workflow를 메인으로 더 당길지
3. `Phase 24`의 new strategy expansion을
   어느 시점부터 다시 열지

## 한 줄 결론

지금 기준 가장 자연스러운 큰 그림은:

**Phase 18~21에서 구현과 운영 구조를 더 만든 뒤,
Phase 22에서 deep backtest를 다시 열고,
Phase 23~25에서 portfolio / new strategy / pre-live 운영 체계로 넓혀가는 흐름**이다.
