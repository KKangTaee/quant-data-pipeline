# Phase 19. Structural Contract Expansion And Interpretation Cleanup

## 이 문서는 무엇인가
- `Phase 19`에서 무엇을 만들고 정리하는지
- 왜 지금 이 phase가 필요한지
- 어떤 순서로 구현할지
를 한 번에 설명하는 kickoff 문서다.

## 목적
- `Phase 17~18`에서 strict annual 전략에 추가된 구조 옵션들을
  사용자가 실제로 계속 써도 덜 헷갈리게 정리한다.
- deep backtest를 다시 크게 열기 전에
  구조 옵션, history 복원, 해석 문구를 먼저 안정화한다.

## 쉽게 말하면
- 지금까지는 strict annual 전략에 구조 옵션이 점점 늘어났다.
  - 빈 자리를 현금으로 둘지
  - 다음 순위 종목으로 채울지
  - risk-off를 현금으로 할지 방어 자산으로 돌릴지
  - 종목 비중을 균등하게 둘지 순위 기반으로 줄지
- 그런데 옵션이 많아질수록
  "기능이 있다"만으로는 부족하다.
- 사용자가:
  - 화면에서 읽을 때도 이해되고
  - 저장된 실행 기록(history)을 다시 볼 때도 같은 뜻으로 보이고
  - 경고 문구와 해석 문장도 같은 언어를 쓰게
  정리해야 한다.
- `Phase 19`는 바로 그 정리 작업을 하는 단계다.

## 왜 필요한가
- 지금 구조 옵션이 커졌는데,
  UI와 저장값(payload)이 `true/false` 조합 중심이면
  나중에 "이 전략이 실제로 어떻게 동작했는지" 다시 읽기 어렵다.
- 예를 들어 사용자는
  - 체크박스 두 개를 켠 건지
  - 정말 하나의 의도된 처리 방식(contract)을 고른 건지
  헷갈릴 수 있다.
- 이 상태로 deep backtest를 더 많이 돌리면
  숫자는 쌓이지만 해석은 흔들릴 수 있다.
- 그래서 `Phase 19`는
  **백테스트를 더 넓게 돌리기 전에, 구조 옵션의 뜻과 기록 방식을 먼저 정리하는 phase**다.

## 이 phase가 끝나면 좋은 점
- strict annual 구조 옵션을 화면에서 더 읽기 쉬워진다.
- history를 다시 열었을 때
  "이 run이 어떤 처리 계약으로 돌았는지" 더 바로 이해된다.
- compare, prefill, interpretation이 같은 언어를 쓰게 되어
  다음 phase에서 deep validation을 다시 열어도 해석이 덜 흔들린다.

## 이 phase에서 다루는 대상
- strict annual family 3종
  - `Quality`
  - `Value`
  - `Quality + Value`
- 주요 정리 대상
  - rejected-slot 처리
  - risk-off 해석
  - weighting 해석
  - history / compare / prefill / meta의 용어 정렬

## 현재 구현 우선순위
1. `Rejected-Slot Handling`을 하나의 명시적 contract로 정리
   - 쉽게 말하면:
     trend filter가 일부 종목을 탈락시킨 뒤
     그 빈 자리를 어떻게 처리할지를
     사용자가 하나의 이름으로 고르는 방식으로 바꾸는 작업이다.
   - 왜 먼저 하는가:
     지금 가장 헷갈리기 쉬운 부분이
     체크박스 조합으로 뜻을 읽어야 하는 rejected-slot 처리이기 때문이다.
   - 기대 효과:
     form, history, rerun에서 같은 뜻으로 읽기 쉬워진다.

2. `Risk-Off / Weighting` 해석 문구 정리
   - 쉽게 말하면:
     위험할 때 현금/방어자산으로 어떻게 움직였는지,
     비중을 균등하게 뒀는지 순위 기반으로 뒀는지를
     결과 화면에서도 같은 언어로 읽히게 만드는 작업이다.
   - 왜 필요한가:
     구조 옵션마다 설명 방식이 다르면,
     숫자는 맞아도 사용자가 비교 해석을 어렵게 느끼기 때문이다.
   - 기대 효과:
     결과 요약과 interpretation에서
     구조 옵션별 차이를 더 직관적으로 이해할 수 있다.

3. `History / Compare / Prefill / Meta` alignment
   - 쉽게 말하면:
     한 화면에서 보이는 뜻과,
     저장 기록을 다시 불러왔을 때 보이는 뜻이 달라지지 않게 맞추는 작업이다.
   - 용어 설명:
     - `History`
       저장된 실행 기록을 다시 보는 화면
     - `Compare`
       여러 전략 후보를 나란히 비교하는 흐름
     - `Prefill`
       예전 run 설정을 폼에 다시 채워 넣는 기능
     - `Meta`
       결과와 함께 남는 보조 설명값이나 상태 요약
   - 왜 필요한가:
     form에서는 A처럼 보이고 history에서는 B처럼 읽히면
     다음 phase의 deep validation 신뢰도가 떨어지기 때문이다.
   - 기대 효과:
     single / compare / history / rerun 흐름이 더 일관되게 연결된다.

4. `Minimal Validation` 고정
   - 쉽게 말하면:
     새 구현을 하나 넣을 때마다 대규모 백테스트를 다시 돌리기보다,
     우선 코드가 깨지지 않았고 연결이 맞는지만 빠르게 확인하는 운영 원칙이다.
   - 왜 필요한가:
     지금은 구현 우선 phase이므로,
     deep rerun보다 contract 정리와 UX 안정화가 더 중요하기 때문이다.
   - 기대 효과:
     구현 속도를 유지하면서 회귀 위험을 빠르게 확인할 수 있다.

## 이 문서에서 자주 쓰는 용어
- `Contract`
  - 사용자가 고르는 명시적인 동작 규칙
- `Usable Contract`
  - 코드 내부 규칙이 아니라,
    사용자가 UI / history / interpretation에서 다시 읽어도 뜻이 바로 이해되는 contract
- `Payload`
  - 실행 시 저장되는 설정값 묶음
- `Boolean Combination`
  - `on/off` 값 여러 개를 사용자가 직접 조합해서 뜻을 해석해야 하는 상태
- `Interpretation`
  - 결과 숫자 아래에서 "이 run에서 무슨 일이 있었는지"를 설명하는 영역
- `Slice`
  - phase 전체를 한 번에 다 하지 않고,
    작고 안전한 구현 단위로 나눠 진행하는 조각 작업
- `Minimal Validation`
  - `py_compile`, import smoke, 작은 representative check 같은 최소 검증
- `Structural Redesign Lane`
  - factor나 top N만 바꾸는 수준이 아니라,
    전략 구조 자체를 바꾸는 실험 흐름

## 이번 phase의 운영 원칙
- 구현 우선
- broad rerun 보류
- compile / import smoke / minimal representative validation만 수행
- 기존 payload와 history는 가능한 한 계속 읽히도록 legacy compatibility 유지

## legacy compatibility가 왜 중요한가
- 이미 저장된 run history가 많다.
- 새 contract를 도입했다고 해서
  예전 실행 기록이 갑자기 안 열리면 안 된다.
- 그래서 `Phase 19`에서는
  - 새 방식은 더 읽기 쉽게 만들되
  - 예전 저장값도 계속 복원 가능하게 유지하는 쪽으로 구현한다.

## 첫 구현 단위
- `Rejected Slot Handling Contract`
- 목표:
  - 기존 `rejected_slot_fill_enabled + partial_cash_retention_enabled` 조합을
    사용자 입장에서 하나의 명시적 contract로 읽히게 만든다.
- 쉽게 말하면:
  - 예전에는
    "빈 자리를 채움 + 남은 빈 자리는 현금 유지"
    같은 뜻을 체크박스 두 개 조합으로 읽어야 했다.
  - 이제는
    사용자가 그냥 하나의 처리 방식 이름을 고르면 된다.
- current mode:
  - `reweight_survivors`
  - `retain_unfilled_as_cash`
  - `fill_then_reweight`
  - `fill_then_retain_cash`
- 기대 효과:
  - 폼에서 처리 방식이 더 직접적으로 보인다.
  - history / rerun에서 어떤 처리 방식으로 돌았는지 다시 읽기 쉬워진다.
  - 이후 interpretation과 warning도 같은 용어로 맞출 수 있다.

## 다음에 확인할 것
- history / compare / load-into-form에서 explicit mode가 자연스럽게 복원되는지
- runtime warning이 선택한 handling mode와 같은 언어로 읽히는지
- legacy run payload도 문제없이 다시 열리는지

## 한 줄 정리
- `Phase 19`는 새 전략을 찾는 phase가 아니라,
  이미 생긴 strict annual 구조 옵션들을
  **사람이 다시 읽고 비교하고 검증하기 쉬운 형태로 정리하는 phase**다.
