# Design

## Current-State Continuity

RTDSM RUC는 월별 관측값을 분기 빈티지로 제공한다. 2026-02 빈티지에서 2025-10
관측치 하나가 비어 있어 정확히 3개월 전 값만 찾는 기존 transform은 2026-02~04
신호를 모두 잃고, 후속 3개월 level/momentum rolling까지 2026-07에 영향을 준다.

정확한 lag가 없을 때 과거 방향으로 최대 한 달 이내의 실제 관측값만 허용한다.
연율 변화는 실제 경과 개월수로 계산하고, level change는 목표 3개월에 맞춰
`target_lag / actual_lag`로 정규화한다. 값을 보간하거나 미래 관측을 사용하지 않으며
fallback 사용 origin은 `LIMITED`로 표시한다.

## Required Credit Contract

`BAMLH0A0HYM2`는 current FRED 공개 이력이 최근 3년으로 제한돼 required historical
feature가 될 수 없다. 이미 자산 경로 DB에 저장된 일별 `BAA10Y`를 observation-date
known market-like 신용 스프레드로 사용한다. required pressure feature는 다음 다섯 개다.

- `FEDFUNDS_delta_3m`
- `PCEPILFE_gap_2pct`
- `yield_curve_delta_3m`
- `BAA10Y_delta_3m`
- `PERMIT_change_6m_pct`

BAML/ANFCI는 보조 관찰 근거로만 남고 required common intersection을 제한하지 않는다.

## Task-Specific Models

공통 compact core는 `level`, `momentum`, `phase_duration`, `positive_breadth`, 네 phase
one-hot이다.

- transition pressure: compact core + 다섯 directional driver
- next destination: compact core

pressure는 extended model이 compact core보다 common-origin OOS skill이 양수여야 하고
기존 pressure publication gate를 통과해야 한다. destination은 compact core가 strongest
baseline, calibration, 네 국면 support 기준을 통과해야 한다. 모든 목적지를 비교하며
고정 순환 순서를 강제하지 않는다.

## Production Boundary

이 task는 1~3차 read-only 검증까지만 소유한다. `GO` 전에는 writer, Overview service,
React를 호출하지 않는다. 자산별 확인 포인트는 별도 기존 pathway 계약을 유지한다.
