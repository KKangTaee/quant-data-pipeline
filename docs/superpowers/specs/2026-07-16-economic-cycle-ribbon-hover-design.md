# Economic Cycle Ribbon And Hover Design

Status: Approved
Last Updated: 2026-07-16

## Purpose

최근 60개월로 줄인 Regime Ribbon이 기존 121열 CSS 때문에 왼쪽 절반만 채우는 표시 결함을 수정하고, 최근 12개월 Cycle Map을 평소에는 단순하게 유지하면서 지점별 정보를 필요할 때만 읽게 한다.

## Ribbon Contract

- DB의 121개월 replay와 service의 최근 60개월 read model 계약은 유지한다.
- Ribbon grid의 history 열 수는 고정값이 아니라 실제 `history.length`를 사용한다.
- 현재 history 60개와 forecast 2개는 전체 ribbon 너비를 채운다.
- history 개수가 60보다 적은 partial payload도 남은 공간 없이 실제 개수만큼 균등 배치한다.
- desktop과 420px 모두 같은 동적 열 수를 사용한다.

## Cycle Map Hover Contract

- Cycle Map은 최근 12개월을 유지한다.
- 과거 월별 지점과 현재·+1M·+2M forecast 지점에 투명한 hit area를 둔다.
- 평상시에는 툴팁을 표시하지 않는다.
- pointer hover 또는 keyboard focus 때만 다음 내용을 표시한다.
  - 과거: `YYYY.MM · 국면 우세`
  - forecast: `현재/+1개월/+2개월 · 국면 우세`
  - 우세 국면 확률
  - `검증된 모델 추정 / 잠정 모델 추정`
- 툴팁은 SVG 경계 안으로 위치를 보정하며 경로와 점의 계산값을 변경하지 않는다.
- 결측 월과 결측 forecast에는 hover 지점이나 합성 정보를 만들지 않는다.

## Accessibility And Boundaries

- hover target은 keyboard focus가 가능하고 동일한 한국어 `aria-label`을 제공한다.
- UI에서 provider fetch, model calculation, DB write를 추가하지 않는다.
- NBER 공식 경기판정이나 매매 신호로 표현하지 않는다.

## Acceptance Criteria

- CSS에 `repeat(121, ...)`이 남지 않고 `--history-month-count`를 사용한다.
- 60 history + 2 forecast가 ribbon 전체 너비를 채운다.
- Cycle Map source에 `cycle-hover-target`과 `cycle-tooltip`이 있고 hover/focus 전에는 tooltip이 숨겨진다.
- 현재 actual 화면에서 최근 12개월 문구, 62 ribbon cell, hover tooltip, browser error 0, 420px overflow <= 1px를 확인한다.
