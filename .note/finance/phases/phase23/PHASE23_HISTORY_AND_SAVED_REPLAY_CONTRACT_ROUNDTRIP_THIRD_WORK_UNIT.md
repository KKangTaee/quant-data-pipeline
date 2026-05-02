# Phase 23 History And Saved Replay Contract Roundtrip Third Work Unit

## 이 문서는 무엇인가

`Phase 23`의 세 번째 작업 단위 문서다.

이번 작업은 quarterly strict family에서 고른 `Portfolio Handling & Defensive Rules`가
실행 직후 결과에만 남는 것이 아니라,
history와 saved portfolio replay로 넘어갈 때도 사라지지 않는지 확인하고 보강한 기록이다.

## 쉽게 말하면

quarterly 전략을 실행할 때 사용자가 아래 값을 고를 수 있게 된 것만으로는 부족하다.

- `Weighting Contract`
- `Rejected Slot Handling Contract`
- `Risk-Off Contract`
- `Defensive Sleeve Tickers`

나중에 `History`에서 다시 열거나,
저장된 portfolio를 replay할 때도 같은 값이 따라와야 한다.

이번 작업은 그 “다시 열어도 같은 설정이 남아 있는가?”를 코드 레벨에서 확인한 작업이다.

## 왜 필요한가

quarterly 기능을 제품 기능으로 보려면 재현성이 필요하다.

한 번 실행한 결과를 다시 열었는데,
`Rejected Slot Handling`이나 `Weighting` 값이 빠져 있으면
사용자는 같은 전략을 다시 실행한다고 생각하지만 실제로는 다른 설정으로 실행할 수 있다.

이런 문제는 성과 숫자보다 더 위험하다.
나중에 QA나 비교 분석을 할 때 “같은 전략을 다시 돌렸다”는 전제가 무너지기 때문이다.

## 실제로 변경한 것

### 1. history record 저장 보강

`append_backtest_run_history()`가 아래 값을 history record에 저장하도록 보강했다.

- `weighting_mode`
- `rejected_slot_handling_mode`
- `rejected_slot_fill_enabled`
- `partial_cash_retention_enabled`

### 2. History > Saved Input 표시 보강

History 화면의 `Saved Input & Context`에서 위 contract 값이 보이도록 했다.

이제 사용자는 저장된 quarterly run을 열었을 때,
그 run이 어떤 portfolio handling contract로 실행되었는지 더 직접적으로 확인할 수 있다.

### 3. Run Again / Load Into Form payload 보강

history record에서 다시 payload를 만들 때도 위 contract 값을 포함하도록 했다.

즉 `Run Again`과 `Load Into Form`이 quarterly contract 값을 잃지 않는다.

### 4. saved portfolio strategy override 보강

weighted portfolio를 저장할 때 compare bundle에서 strategy override를 만들고,
나중에 `Replay Saved Portfolio`가 그 override를 사용한다.

이번 작업으로 saved portfolio override에도 `Rejected Slot Handling` 관련 값이 남게 했다.

## 코드 레벨 검증

대표 quarterly smoke bundle을 만든 뒤 아래 roundtrip을 확인했다.

1. result bundle meta
2. history record
3. history payload
4. saved portfolio strategy override

확인한 값:

| 항목 | 값 |
|---|---|
| `weighting_mode` | `rank_tapered` |
| `rejected_slot_handling_mode` | `fill_then_retain_cash` |
| `rejected_slot_fill_enabled` | `True` |
| `partial_cash_retention_enabled` | `True` |
| `risk_off_mode` | `defensive_sleeve_preference` |
| `defensive_tickers` | `SPY`, `TLT` |

검증 결과:

- history record 보존 통과
- history payload 재생성 통과
- saved portfolio override 보존 통과

## 이번 작업에서 하지 않은 것

Streamlit 브라우저 화면에서 직접 버튼을 누르는 manual QA는 아직 사용자가 확인해야 한다.

이번 작업은 UI를 대신 클릭한 것이 아니라,
UI가 사용하는 저장 / 재진입 데이터 경로가 같은 contract 값을 보존하는지 코드 레벨로 확인한 것이다.

## 다음 확인할 것

- `Backtest > History > Load Into Form`을 눌렀을 때 quarterly form에 contract 값이 복원되는지 확인한다.
- saved portfolio를 만든 뒤 `Replay Saved Portfolio`를 눌렀을 때 오류 없이 실행되는지 확인한다.
- saved replay 후 compare context와 weighted result가 자연스럽게 보이는지 확인한다.

## 한 줄 정리

Phase 23 quarterly contract 값은 이제 result, history, load-into-form payload, saved replay override까지 코드 레벨에서 보존된다.
