# Phase 19. Structural Contract Expansion And Interpretation Cleanup

## 목적
- `Phase 18`에서 새로 생긴 strict annual 구조 옵션들을
  사용자가 실제로 계속 써도 덜 헷갈리게 정리한다.
- deep backtest를 다시 크게 열기 전에
  구조 옵션, history 복원, 해석 문구를 먼저 안정화한다.

## 쉽게 말하면
- `Phase 17~18`에서 strict annual 전략에 새 옵션이 여러 개 생겼다.
  - 빈 자리를 현금으로 둘지
  - 다음 순위 종목으로 채울지
  - risk-off를 현금으로 할지 방어 자산으로 돌릴지
  - equal-weight로 둘지 순위 비중을 줄지
- 그런데 옵션이 늘어나면,
  그냥 "기능이 있다"만으로는 부족하다.
- 사용자가:
  - 화면에서 읽을 때도 이해되고
  - 저장된 실행 기록(history)을 다시 볼 때도 같은 뜻으로 보이고
  - 경고 문구와 해석 문장도 같은 언어를 쓰도록
  정리해야 한다.
- `Phase 19`는 바로 그 정리 단계다.

## 왜 필요한가
- 지금 구조 옵션이 커지고 있는데,
  UI와 저장값(payload)이 `true/false` 조합 중심이면
  나중에 "이 전략이 실제로 무슨 방식으로 동작했는지" 다시 읽기 어려워진다.
- 예를 들어 사용자는
  - 체크박스 두 개를 켠 건지
  - 정말 하나의 의도된 처리 방식(contract)을 고른 건지
  헷갈릴 수 있다.
- 이 상태로 deep backtest를 더 많이 돌리면
  숫자는 쌓이는데 해석이 흔들릴 수 있다.
- 그래서 `Phase 19`는
  **백테스트를 더 넓게 돌리기 전에, 구조 옵션의 뜻과 기록 방식을 먼저 정리하는 phase**다.

## 이 phase가 끝나면 좋은 점
- strict annual 구조 옵션을 화면에서 더 읽기 쉬워진다.
- history를 다시 열었을 때
  "이 run이 어떤 처리 계약으로 돌았는지" 더 바로 이해된다.
- compare, prefill, interpretation이 같은 언어를 쓰게 되어
  다음 phase에서 deep validation을 다시 열어도 해석이 덜 흔들린다.

## 여기서 쓰는 어려운 말 짧은 해설
- `structural redesign lane`
  - 전략 자체의 구조를 바꾸는 실험 흐름을 뜻한다.
  - 예:
    - 빈 자리를 현금으로 둘지
    - 다음 후보로 채울지
    - 위험할 때 현금 대신 방어 자산으로 돌릴지
- `contract`
  - 사용자가 고르는 명시적인 동작 규칙이다.
  - 예:
    - `Reweight Survivors`
    - `Fill Then Retain Unfilled Slots As Cash`
- `usable contract`
  - 코드 안에만 있는 규칙이 아니라,
    사용자가 화면과 history에서 다시 읽어도 바로 이해할 수 있는 형태의 규칙을 뜻한다.
- `payload`
  - 실행할 때 저장되는 설정값 묶음이다.
  - history에서 다시 불러오거나 rerun할 때 쓰인다.
- `booleans 조합`
  - `on/off` 체크 두세 개를 사용자가 스스로 조합해 뜻을 해석해야 하는 상태를 말한다.
  - `Phase 19`는 이걸 줄이려는 단계다.
- `interpretation`
  - 결과 표 아래에서 "이 run에서 무슨 일이 있었는지" 문장으로 설명해 주는 영역이다.
- `slice`
  - phase 전체를 한 번에 다 하지 않고,
    작고 안전한 구현 단위로 나눠 진행하는 한 조각 작업을 뜻한다.
- `minimal validation`
  - 큰 백테스트 대신,
    우선 코드가 깨지지 않았는지 확인하는 최소 검증이다.
  - 예:
    - `py_compile`
    - import smoke
    - 아주 작은 representative check

## 현재 구현 우선순위
1. `rejected-slot handling`을 하나의 명시적 contract로 정리
  - 지금은 사용자가 체크박스 조합을 머릿속으로 해석해야 하는 부분을 줄이기 위함
  - 쉽게 말하면:
    trend filter가 일부 종목을 탈락시킨 뒤
    그 빈 자리를
    - 남은 종목에 재배분할지
    - 현금으로 남길지
    - 다음 순위 종목으로 채울지
    를 한 번에 읽기 쉬운 이름으로 고정하는 작업이다
2. `risk-off / weighting`도 같은 방식으로 해석 문구 정리
  - 구조 옵션마다 결과 설명 방식이 달라지지 않게 만들기 위함
  - 쉽게 말하면:
    위험할 때 현금/방어자산으로 어떻게 움직였는지,
    비중을 균등하게 뒀는지 순위 기반으로 뒀는지를
    결과 화면에서도 같은 언어로 읽히게 만드는 작업이다
3. `history / compare / prefill / meta`가 같은 뜻으로 맞물리게 정리
  - 한 화면에서는 A라고 보이고, history에서는 B처럼 읽히는 문제를 줄이기 위함
  - 쉽게 말하면:
    - `history`
      저장된 실행 기록을 다시 보는 화면
    - `compare`
      여러 전략 후보를 나란히 비교하는 흐름
    - `prefill`
      예전 run 설정을 폼에 다시 채워 넣는 기능
    - `meta`
      결과와 함께 남는 보조 설명값이나 상태 요약
    이 네 군데가 서로 다른 뜻으로 보이지 않게 맞추는 작업이다
4. `minimal validation` 고정
  - 지금은 구현 우선 phase이므로, deep rerun보다 구현 안정화가 우선
  - 쉽게 말하면:
    새 구현을 하나 넣을 때마다 대규모 백테스트를 다시 돌리기보다,
    우선 코드가 깨지지 않았고 연결이 맞는지만 빠르게 확인하는 운영 원칙이다

## 현재 구현 우선순위에서 쓰는 용어 짧은 설명
- `rejected-slot handling`
  - trend filter 때문에 원래 뽑힌 종목 일부가 탈락했을 때,
    그 빈 자리를 어떻게 처리할지에 대한 규칙
- `risk-off`
  - 위험 신호가 나왔을 때 포트폴리오를 더 보수적으로 운용하는 방식
  - 예:
    현금으로 이동, 방어 자산으로 이동
- `weighting`
  - 선택된 종목들에 비중을 어떻게 나눌지에 대한 규칙
  - 예:
    equal weight, rank-tapered
- `interpretation cleanup`
  - 결과 숫자만 남기는 것이 아니라,
    "이 run에서 실제로 어떤 일이 있었는지" 설명 문구를 정리하는 작업
- `prefill`
  - 예전에 저장된 run 설정을 현재 폼에 다시 자동으로 채워 넣는 기능
- `meta`
  - 성과 수치 외에 함께 남는 실행 상태, contract mode, warning summary 같은 보조 정보

## 이번 phase의 운영 원칙
- 구현 우선
- broad rerun 보류
- compile / import smoke / minimal representative validation만 수행
- 기존 payload와 history는 가능한 한 계속 읽히도록 legacy compatibility 유지

## legacy compatibility가 왜 중요한가
- 이미 예전에 저장된 run history가 많다.
- 새 contract를 도입했다고 해서
  예전 실행 기록이 갑자기 안 열리면 안 된다.
- 그래서 `Phase 19`에서는
  - 새 방식은 더 읽기 쉽게 만들되
  - 예전 저장값도 계속 복원 가능하게 유지하는 쪽으로 구현한다.

## 첫 slice
- `Rejected Slot Handling Contract`
- 목표:
  - 기존 `rejected_slot_fill_enabled + partial_cash_retention_enabled` 조합을
    사용자 입장에서 하나의 명시적 contract로 읽히게 만든다
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

## 첫 slice의 효과
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
