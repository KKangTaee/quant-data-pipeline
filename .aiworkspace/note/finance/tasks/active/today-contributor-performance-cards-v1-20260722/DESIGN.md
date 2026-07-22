# Today Contributor Performance Cards V1 Design

Status: Approved
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

계산은 해당 item lane의 마지막 유효 `flow_adjusted_index - 1`이다. 추가매수·일부매도 등 외부 현금흐름이 있어도 성과를 왜곡하지 않는다. `flow_adjusted_index`가 없거나 마지막 값이 유효하지 않으면 `None`을 반환하며 `(current_value / initial_capital) - 1`로 임의 fallback하지 않는다.

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
- contribution row: 11px, `기여` label과 signed dollar amount
- card 자체에는 상태를 의미하는 좌측선이나 강한 배경색을 쓰지 않는다.
- contribution과 return의 부호가 다를 수 있으므로 각각 독립 tone을 적용한다.

수익률이 없으면 `수익률 자료 부족`을 표시하고 기여금은 계속 보여준다. section footer에는 `종목 수익률은 입출금 영향을 조정한 누적 성과 · 기준 YYYY-MM-DD`를 표시한다.

## Layout

- desktop/760px: contributor section 내부 2열 card grid
- 460px 이하: 1열
- 기존 `우선 확인`과의 1:1 outer grid는 유지하고 760px 이하에서 세로로 쌓는다.
- 카드 높이는 content-driven이며 고정 높이를 두지 않는다.

## Ownership And Boundaries

- Portfolio Monitoring read model: 정확한 item flow-adjusted return만 소유
- Today service: 상위/하위 selection과 JSON-safe projection 소유
- Today React: card hierarchy, formatting, responsive layout 소유
- Today fallback: 같은 두 단위를 읽기 전용으로 표시

DB·ingestion·provider·position event 계산·그룹 curve는 변경하지 않는다. Portfolio Monitoring의 기존 사용자 화면도 변경하지 않는다.

## Error Handling

- lane failure: 해당 row의 `total_return=None`; 기여금이 있으면 자료 부족 카드로 유지
- contribution 0: 기존처럼 selection에서 제외
- 양수 또는 음수 side가 2개 미만: 존재하는 항목만 표시
- contributor 없음: `기여 계산 자료가 없습니다.` 유지

## Verification

- Python RED/GREEN: 현금흐름 조정 index 기반 item return, missing index, Today projection/sorting
- Today contract: 카드 필드와 기존 read-only/fallback/navigation 회귀
- React source/typecheck/build: 명시 label, 독립 tone, responsive grid
- Portfolio Monitoring focused regression: item row additive field가 기존 payload와 계산을 바꾸지 않음
- Browser: root `/` 1280/760/420, 숫자 단위·footer·overflow·console 확인

## Tradeoffs

- 최대 4개만 보여 전체 종목 비교는 못 하지만 Today의 scan 속도를 보존한다.
- 정확한 flow-adjusted return을 사용하므로 단순 평가손익률과 값이 다를 수 있다. label과 footer에서 계산 의미를 밝힌다.
- shared item row가 additive하게 확장되지만 Portfolio Monitoring UI를 바꾸지 않아 영향 범위를 제한한다.
