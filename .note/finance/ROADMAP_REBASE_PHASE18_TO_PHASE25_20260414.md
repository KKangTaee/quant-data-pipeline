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

### 쉽게 말하면

- 지금까지는 구조 레버를 하나씩 열어보는 단계였다
- `Phase 19`는 그 레버들을
  **“실제로 계속 쓸 수 있는 기능”**
  으로 다듬는 단계다
- 즉:
  - 옵션은 있는데 의미가 헷갈리는 상태
  - 구현은 됐는데 surface가 덜 정리된 상태
  를 줄이는 phase다

### 왜 해야 하는가

- 지금 바로 deep backtest를 더 크게 돌려도,
  기능이 덜 정리된 상태면 결과 해석이 흔들린다
- 특히 strict annual family는 이제
  rejection / cash / sleeve / weighting 같은 계약이 많아졌기 때문에,
  **먼저 읽기 쉬운 contract로 정리**해야
  나중에 돌린 큰 검증도 의미가 커진다
- 이 phase를 건너뛰면:
  - 결과는 많이 쌓이는데
  - “어떤 설정이 왜 그렇게 동작했는지”가 흐려질 수 있다

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

### 이 phase가 끝나면 좋은 점

- 새 구조 옵션을 더 자신 있게 켜고 끌 수 있다
- 나중에 deep rerun을 돌릴 때 해석 혼선이 줄어든다
- strongest / near-miss 후보 비교도 더 안정적이 된다

---

### Phase 20. Candidate Consolidation And Operator Workflow Hardening

### 목적

- strongest / near-miss 후보를
  compare -> weighted -> saved portfolio 흐름과 더 자연스럽게 연결한다
- single-strategy refinement와 portfolio bridge 사이의 운영 gap을 줄인다

### 쉽게 말하면

- 좋은 후보를 찾는 것만으로는 부족하고,
  **그 후보를 다시 꺼내 보고, 비교하고, 저장하고, 조합하는 흐름**
  도 편해야 한다
- `Phase 20`은 그 운영 흐름을 정리하는 단계다

### 왜 해야 하는가

- 지금도 strongest candidate는 있지만,
  다시 보려면 여러 문서와 탭을 오가야 한다
- 후보가 늘어날수록
  “무슨 후보를 지금 보고 있는지”
  “어떤 조합을 전에 봤는지”
  관리가 더 중요해진다
- 이 phase를 건너뛰면:
  - 연구는 계속 되는데
  - 후보 관리와 비교 workflow가 점점 피곤해진다
  - 결국 좋은 후보를 놓치거나 중복 실험이 늘어날 수 있다

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

### 이 phase가 끝나면 좋은 점

- strongest / near-miss 후보를 더 빠르게 다시 볼 수 있다
- compare -> weighted -> saved workflow가 더 실용적으로 변한다
- 이후 portfolio-level 실험으로 넘어갈 준비가 된다

---

### Phase 21. Research Automation And Experiment Persistence

### 목적

- 반복되는 refinement / validation / documentation 흐름을
  더 자동화한다
- 현재 plugin / skill / checklist script를
  더 실무적으로 쓸 수 있게 만든다

### 쉽게 말하면

- 지금은 좋은 흐름이 생겨도
  사람이 손으로 반복하는 부분이 여전히 많다
- `Phase 21`은
  **반복 작업을 줄이고, 재현성을 높이는 phase**
  다

### 왜 해야 하는가

- 구현과 전략 탐색이 계속 커질수록
  문서 업데이트, 체크리스트 확인, rerun scenario 관리도 늘어난다
- 이걸 매번 수동으로 하면:
  - 속도가 느려지고
  - 빠뜨리는 문서가 생기고
  - 같은 검증을 여러 번 하게 될 수 있다
- 이 phase를 건너뛰면:
  - deep validation 단계에서
    실험 관리 비용이 너무 커질 수 있다

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

### 이 phase가 끝나면 좋은 점

- rerun과 문서화가 더 일관된다
- plugin / skill / script를 실제 작업 리듬에 맞게 쓸 수 있다
- Phase 22 deep validation을 훨씬 안정적으로 돌릴 수 있다

---

### Phase 22. Integrated Deep Backtest Validation

### 목적

- `Phase 19 ~ 21`에서 구현을 더 붙인 뒤,
  다시 넓고 깊은 백테스트를 공식적으로 재개한다
- strongest / near-miss / redesigned contract를
  같은 기준으로 다시 검증한다

### 쉽게 말하면

- 여기서부터가 다시
  **“깊게 돌려서 진짜 누가 strongest인지 다시 판정하는 단계”**
  다
- 단, 예전처럼 기능이 덜 닫힌 상태에서 돌리는 게 아니라
  충분히 갖춰진 구조 위에서 돌린다는 점이 다르다

### 왜 해야 하는가

- 지금은 구현을 먼저 쌓는 게 맞지만,
  결국 실전형 후보를 다시 고르는 큰 검증은 반드시 필요하다
- `Phase 22`는 그 검증을
  더 좋은 조건에서 다시 여는 phase다
- 이 phase를 해야만:
  - current strongest candidate가 여전히 strongest인지
  - 새 구조가 실제 rescue를 만드는지
  - family별로 어떤 redesign이 가장 유효한지
  를 다시 확정할 수 있다

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

### 이 phase가 끝나면 좋은 점

- strongest / near-miss / redesign 결과를 한 번에 다시 정리할 수 있다
- 이후 portfolio-level 후보나 new strategy expansion도 더 안정적으로 연다
- “지금 무엇이 정말 좋은 후보인가”가 다시 선명해진다

---

### Phase 23. Portfolio-Level Candidate Construction

### 목적

- single-strategy strongest candidate를 넘어,
  portfolio-level candidate를 만들 수 있는지 본다
- weighted bundle이 단순 연구용 조합인지,
  더 실전적인 portfolio candidate로 읽을 수 있는지 검토한다

### 쉽게 말하면

- 여기서부터는
  “전략 하나가 좋은가?”를 넘어서
  **“좋은 전략들을 묶으면 더 좋은 포트폴리오가 되는가?”**
  를 본다

### 왜 해야 하는가

- 실제 실전 운용은 전략 하나만 쓰는 것보다
  여러 후보를 묶는 방식이 더 자연스러울 수 있다
- 지금까지는 single-strategy candidate를 고도화하는 데 집중했으니,
  그 다음에는 portfolio-level construction을 볼 차례다
- 이 phase를 건너뛰면:
  - strongest candidate는 있어도
  - “묶어서 더 나은가”라는 질문은 계속 비어 있게 된다

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

### 이 phase가 끝나면 좋은 점

- strategy-level에서 portfolio-level로 시야가 넓어진다
- weighted portfolio가 연구용을 넘어서 candidate construction 도구가 될 수 있다
- 이후 pre-live 운영 문서도 더 현실적으로 쓸 수 있다

---

### Phase 24. New Strategy Expansion

### 목적

- 기존 strongest family 고도화가 어느 정도 닫힌 뒤,
  다시 새로운 전략 family를 연다
- `quant-research`와 `quant-data-pipeline`을 더 명시적으로 연결한다

### 쉽게 말하면

- 지금은 기존 핵심 전략을 다듬는 게 우선이었고,
  여기서부터는 다시
  **“새로운 전략을 늘릴 타이밍”**
  이다

### 왜 해야 하는가

- 새로운 전략은 계속 중요하지만,
  너무 일찍 열면 기존 strongest family 정리가 덜 된 상태에서 범위만 커진다
- 반대로 이 시점 이후에 열면:
  - 현재 stack이 충분히 성숙했고
  - research-to-implementation bridge도 더 잘 정리된 상태라
  새 전략을 붙여도 덜 흔들린다

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

### 이 phase가 끝나면 좋은 점

- 전략 라이브러리가 다시 넓어진다
- `quant-research`에서 발굴한 아이디어를 더 자연스럽게 구현할 수 있다
- 기존 strongest family와 새 family를 같은 validation frame에서 비교할 수 있다

---

### Phase 25. Pre-Live Operating System And Deployment Readiness

### 목적

- 찾은 후보를 실제 paper / small-capital trial 관점에서 다루는 운영 체계를 정리한다
- 지금까지 만든
  `promotion / shortlist / probation / deployment`
  surface를 실제 operator workflow로 묶는다

### 쉽게 말하면

- 여기서는 드디어
  **“좋은 후보를 실제로 어떻게 관리하고 운용 준비할 것인가”**
  를 문서와 흐름으로 정리한다
- 즉 연구와 구현의 끝이 아니라,
  pre-live 운영 체계의 시작이다

### 왜 해야 하는가

- 좋은 전략을 찾는 것만으로는 실전에 바로 못 간다
- paper tracking, review cadence, probation, deployment readiness 같은
  운영 루틴이 같이 있어야
  진짜 실전형 시스템이 된다
- 이 phase를 해야:
  - 후보를 어떻게 review할지
  - 언제 probation으로 올릴지
  - 무엇이 live 전 마지막 체크인지
  를 일관되게 정할 수 있다

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

### 이 phase가 끝나면 좋은 점

- 후보 평가 시스템이 실제 운영 준비 시스템으로 연결된다
- paper / small-capital trial workflow가 더 분명해진다
- 프로젝트의 long-term goal과 가장 가까운 문서/흐름이 생긴다

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

## 아주 짧은 버전

- `Phase 19`
  - 구조 옵션을 더 usable하게 만든다
- `Phase 20`
  - 후보를 관리하고 다시 보는 흐름을 정리한다
- `Phase 21`
  - 반복 연구를 자동화한다
- `Phase 22`
  - 그 뒤에 다시 깊게 검증한다
- `Phase 23`
  - 전략을 포트폴리오 단위로 본다
- `Phase 24`
  - 새 전략을 다시 늘린다
- `Phase 25`
  - 실전 직전 운영 체계를 정리한다

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
