# Inflation Policy Yield Path Phase Design

## Approved Direction

- 사용자 UI는 `PCE 발표치로 결과 보기`와 `10년물 목표에서 필요 조건 보기`를 제공한다.
- 10년물 4.7%, Core PCE 3.5%, 월 0.4~0.5%, S&P 500 6,400은 날짜가 붙은
  시나리오 또는 사용자 기준이며 전역 상수가 아니다.
- 점도표와 Core PCE 분포는 익명 집계로 저장하며 개인별 대응 관계를 만들지 않는다.
- 기존 경제 사이클 확률·요인·snapshot·artifact는 입력, 대체값, label, 검증 target으로
  사용하지 않는다.
- 상세 설계는 `docs/superpowers/specs/2026-08-02-inflation-policy-yield-path-design.md`를
  따른다.

## Layer Boundary

```text
Official sources -> Ingestion -> PIT DB -> Loader -> Model artifact/snapshot
  -> Service -> Streamlit/React
```

UI는 provider를 직접 호출하거나 canonical probability를 계산하지 않는다.
