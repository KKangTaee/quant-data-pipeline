# Today Contributor Performance Cards V1 Design

Status: Implemented and Verified
Last Updated: 2026-07-22

## Problem

현재 Today contributor row는 `{symbol, value, tone}`만 제공하고 React는 `AMD $11,915`처럼 한 줄 chip으로 표시한다. `value`는 종목 수익률이 아니라 `현재 평가액 + 누적 출금 - 누적 입금`으로 계산한 포트폴리오 손익 기여금이다. 금액만 표시하면 사용자가 종목 자체 수익률로 오해할 수 있고, 같은 $4,000 기여도 투자금 규모에 따라 성과의 질이 다르다는 점을 알 수 없다.

## Approved Information Scope

Today의 compact 성격을 유지하기 위해 현재 selection을 보존한다.

- 양수 기여 상위 2개
- 음수 기여 하위 2개
- 최대 4개 카드
- 전체 종목은 기존 `포트폴리오 전체 점검`으로 이동

섹션 제목은 `종목별 성과 기여`, 보조 문구는 `기여 상위 2 · 하위 2`로 한다.

## Data Contract

### Portfolio Monitoring Item Row

`app/services/portfolio_monitoring/read_model.py`의 item row에 다음 additive field를 넣는다.

```text
total_return: Decimal | None
```

계산은 그룹 공통 `basis_date`와 날짜가 정확히 같은 item lane row의 `flow_adjusted_index - 1`이다. 기준일 이후 관측을 사용하거나, 기준일 row가 없거나 null일 때 더 오래된 non-null 값을 재사용하지 않는다. 이런 경우 `None`을 반환하며 `(current_value / initial_capital) - 1`로 임의 fallback하지 않는다.

### Selected Position Compatibility

같은 helper를 쓰는 `_project_selected_position`은 group `basis_date`가 아니라 해당 lane의 `latest_usable_date`를 exact date로 전달한다. 그 날짜의 유효 index는 return으로 투영하고, row가 없거나 null이면 `None`으로 남긴다. selected-position의 자체 최신일·평가액·보유수량 의미는 유지한다.

### Today Contributor Row

Today projection은 다음 의미를 명시한다.

```text
symbol
contribution_value
total_return
tone
```

기존 `value`는 Python fallback과 이전 내부 fixture 호환을 위해 같은 기여금 alias로 한 차례 유지하되 React는 `contribution_value`만 사용한다. sorting은 `contribution_value`로 수행한다. `tone`도 contribution 부호를 뜻하며, 수익률 색상은 `total_return` 자체 부호로 별도 결정한다.

## Card Design

각 카드는 neutral surface를 사용하고 두 단위를 label로 분리한다.

```text
AMD
종목 누적 수익률
+358.0%
포트폴리오 누적 기여  +$11,915
```

- symbol: 11px metadata/heading
- return label: 10px muted
- return value: 15px, return 부호에 따른 green/red text
- contribution row: 11px, `기여` label과 양수 `+$…` / 음수 `-$…` signed dollar amount
- card 자체에는 상태를 의미하는 좌측선이나 강한 배경색을 쓰지 않는다.
- contribution과 return의 부호가 다를 수 있으므로 각각 독립 tone을 적용한다.

수익률이 없으면 `수익률 자료 부족`을 표시하고 기여금은 계속 보여준다. section footer에는 `종목 수익률은 입출금 영향을 조정한 누적 성과 · 기준 YYYY-MM-DD`를 표시한다.

## Layout

- desktop/760px: contributor section 내부 2열 card grid
- 460px 이하: 1열
- 기존 `우선 확인`과의 1:1 outer grid는 유지하고 760px 이하에서 세로로 쌓는다.
- 카드 높이는 content-driven이며 고정 높이를 두지 않는다.

## Ownership And Boundaries

- Portfolio Monitoring read model: group item에는 공통 `basis_date`, selected-position에는 `latest_usable_date`의 정확한 item flow-adjusted return만 소유
- Today service: 상위/하위 selection과 JSON-safe projection 소유
- Today React: card hierarchy, formatting, responsive layout 소유
- Today fallback: 같은 두 단위를 읽기 전용으로 표시

DB·ingestion·provider·position event 계산·그룹 curve는 변경하지 않는다. Portfolio Monitoring의 기존 사용자 화면도 변경하지 않는다.

## Error Handling

- exact basis-date row 또는 유효 index 부재: 해당 row의 `total_return=None`; 기여금이 있으면 자료 부족 카드로 유지
- contribution 0: 기존처럼 selection에서 제외
- 양수 또는 음수 side가 2개 미만: 존재하는 항목만 표시
- contributor 없음: `기여 계산 자료가 없습니다.` 유지

## Verification

- Python RED/GREEN: 공통 basis-date의 exact item return, future observation 배제, trailing-null, selected-position exact latest, missing index, Today projection/sorting
- Today contract: 카드 필드와 기존 read-only/fallback/navigation 회귀
- React unit/source/typecheck/build: 명시 label, 독립 tone, `+$…` / `-$…`, responsive grid
- Portfolio Monitoring focused regression: item row additive field가 기존 payload와 계산을 바꾸지 않음
- Browser: root `/` 1280/760/420, 숫자 단위·footer·overflow·console 확인

## Tradeoffs

- 최대 4개만 보여 전체 종목 비교는 못 하지만 Today의 scan 속도를 보존한다.
- exact common-date flow-adjusted return을 사용하므로 종목의 더 최신 관측이 있어도 공통 기준일 이후 값은 보여 주지 않는다. 기준일 값이 없으면 오래된 값을 보간하지 않고 자료 부족으로 표시한다.
- shared item row가 additive하게 확장되지만 Portfolio Monitoring UI를 바꾸지 않아 영향 범위를 제한한다.

## Implemented Result

- Portfolio Monitoring item row는 그룹 공통 `basis_date`의 정확한 `flow_adjusted_index - 1`만 `total_return`으로 투영하고, 해당 날짜의 row/value가 없으면 `None`을 반환한다.
- selected-position은 `lane.latest_usable_date`의 정확한 row만 평가해 valid latest는 유지하고 trailing-null/missing latest는 `None`으로 남긴다.
- Today는 `contribution_value`로 상위 양수 2개·하위 음수 2개를 고르고 `total_return`과 함께 JSON-safe하게 전달한다. `value`는 Python compatibility alias로만 남는다.
- React primary와 Python fallback은 `종목 누적 수익률`과 `포트폴리오 누적 기여`를 독립 label/tone으로 표시하고 contribution을 `+$…` / `-$…`로 맞추며 동일한 기준일 footer를 사용한다.
- root `/` actual QA에서 1280·760의 카드 2열, 760의 contributor/우선 확인 세로 적층, 420의 카드 1열과 overflow/clipping/console clean 상태를 확인했다.
