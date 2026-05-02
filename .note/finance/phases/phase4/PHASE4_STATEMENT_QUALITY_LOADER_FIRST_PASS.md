# Phase 4 Statement Quality Loader First Pass

## 목적
이 문서는 strict statement 기반 quality path를
sample/prototype 코드 내부의 임시 조합이 아니라
loader 계층에서도 재사용 가능하게 만든 first-pass 작업을 기록한다.

핵심 추가:
- `finance/loaders/factors.py`
  - `load_statement_quality_snapshot_strict(...)`

---

## 역할

이 loader는 아래 경로를 하나의 읽기 경계로 묶는다.

```text
load_statement_snapshot_strict(...)
  -> build_quality_factor_snapshot_from_statement_snapshot(...)
  -> quality factor snapshot DataFrame
```

즉 caller 입장에서는:
- strict statement snapshot row structure를 직접 알 필요 없이
- quality ranking에 필요한 factor snapshot만 받으면 된다.

---

## 현재 계약

입력:
- `symbols`
- `as_of_date`
- `freq`
- `factor_names` optional

출력:
- `symbol`
- `freq`
- `statement_period_end`
- `as_of_date`
- requested factor columns

현재 지원 quality factor:
- `roe`
- `gross_margin`
- `operating_margin`
- `debt_ratio`

---

## 왜 필요한가

이전 상태에서는 sample prototype이:
- strict statement snapshot 로드
- data-layer builder 호출
- snapshot dict 구성

을 직접 조합하고 있었다.

이번 정리 후:
- loader가 strict statement quality snapshot read path를 담당
- sample/runtime는 loader를 소비하는 쪽으로 단순화된다

즉 구조가 아래처럼 더 명확해졌다.

```text
DB
  -> loader
  -> sample/runtime
  -> strategy
```

---

## 현재 의미

이 loader가 추가되었다고 해서
public UI quality strategy가 strict statement path로 바뀐 것은 아니다.

현재 의미는 정확히:
- strict statement quality path도 이제 loader 계층을 가진다
- future statement-driven rebuild / prototype / public candidate 모두 같은 read boundary를 공유할 수 있다

---

## 다음 자연스러운 사용처

1. statement-driven quality prototype sample
2. future statement-driven runtime wrapper
3. statement-driven coverage audit / backfill tooling
