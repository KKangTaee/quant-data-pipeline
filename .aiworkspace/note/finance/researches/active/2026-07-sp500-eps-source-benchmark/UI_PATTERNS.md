# UI And Workflow Patterns

Status: Active
Access date: 2026-07-12

## 권장 표시 구조

```text
예상 EPS 기반 적정 지수
├─ 현재 EPS 기준값
│  ├─ 공식 S&P actual EPS
│  └─ Shiller TTM proxy (fallback)
├─ 성장 가정
│  ├─ SEP 실질 GDP
│  └─ SEP PCE inflation
├─ 자체 예상 EPS
│  └─ 현재 EPS × (1 + GDP + PCE)
├─ 적정 멀티플
│  └─ 그래프 1의 5년 PER 기준선/범위
└─ 결과
   ├─ 예상 적정 SPX 밴드
   ├─ 현재 SPX
   └─ 괴리율
```

## 반드시 노출할 근거

- EPS source badge: `S&P 공식 actual` 또는 `Shiller TTM proxy`
- EPS 기준일과 SEP 발표일
- `거시 기반 자체 추정치이며 시장 컨센서스가 아님` 안내
- fallback 사용 이유

## 향후 유료 컨센서스 도입 시

SEP 자체 예상 EPS와 consensus NTM EPS를 덮어쓰지 않고 별도 시리즈로 나란히 보여준다. 두 값은 방법론과 목적이 다르므로 단일 숫자로 합치지 않는다.
