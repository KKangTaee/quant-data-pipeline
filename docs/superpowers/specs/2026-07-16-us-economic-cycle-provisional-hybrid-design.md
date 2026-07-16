# U.S. Economic Cycle Provisional Hybrid Design

Status: Approved
Last Updated: 2026-07-16

## Purpose

경제사이클 계산 결과가 존재해도 validation gate가 미달이면 전부 `판단 제한`으로 숨기던 V1을 개선한다. 검증 기준은 유지하면서 사용자가 현재와 +1M/+2M 모델 결과, 과거 이동 경로, 검증 상태를 함께 읽을 수 있게 한다.

## Result States

각 horizon은 아래 세 상태 중 하나다.

1. `PROVISIONAL`
   - 유효한 네 국면 확률을 계산했다.
   - 해당 horizon의 publication gate는 `LIMITED`다.
   - UI 표기: `잠정 모델 추정`.
2. `VERIFIED`
   - 유효한 네 국면 확률을 계산했다.
   - 해당 horizon의 publication gate는 `READY`다.
   - UI 표기: `검증된 모델 추정`.
3. `UNAVAILABLE`
   - artifact가 없거나 확률 계산·완결성 확인이 불가능하다.
   - UI 표기: `판단 불가`.

`PROVISIONAL`은 검증 실패를 숨기지 않는다. 확률·우세 국면과 함께 첫 번째 실패 사유를 표시한다. `VERIFIED`와 `PROVISIONAL` 모두 모델 추정이며 NBER 공식 판정이 아니다.

## Persistence And Read Model

- 기존 `economic_cycle_snapshot` schema를 유지한다.
- artifact가 존재하면 publication status와 무관하게 확률을 계산해 `forecast_path_json`에 저장한다.
- `publication_status`는 기존 `READY | LIMITED`를 유지한다.
- Overview service가 유효 확률과 publication status를 조합해 `estimate_status`를 만든다.
- history 역시 `LIMITED` 확률을 버리지 않고 `PROVISIONAL`로 전달한다.
- 계산 불가 상태에서는 확률·dominant phase를 합성하지 않는다.

## Hybrid Visualization

V1 원형 clock을 사용자가 선택한 2×2 혼합형으로 교체한다.

- 가로축: 성장 레벨
- 세로축: 성장 모멘텀
- 사분면: 좌상 회복, 우상 확장, 우하 둔화, 좌하 침체
- 확률 좌표:
  - `x = expansion + slowdown - recovery - recession`
  - `y = recovery + expansion - slowdown - recession`
- 최근 최대 18개월은 실선으로 표시한다.
- 현재→+1M→+2M은 점선으로 표시한다.
- `PROVISIONAL` 지점·선은 주황색과 점선/사선 표기로 검증 미달임을 드러낸다.
- 과거 ribbon은 우세 국면 색을 유지하고 `PROVISIONAL` 월에는 hatch를 겹친다.

## Horizon Cards

- 현재, +1M, +2M 카드 모두 유효 확률이 있으면 네 국면 분포를 표시한다.
- 제목은 `확장 우세`처럼 dominant phase와 `우세`를 결합한다.
- `VERIFIED`: `검증 완료` badge.
- `PROVISIONAL`: `잠정 추정` badge와 검증 미달 사유.
- `UNAVAILABLE`: 확률 bar 대신 판단 불가 사유.

## Safety And Boundaries

- publication threshold를 낮추지 않는다.
- revised-latest data, 합성 history, 미래 데이터 사용을 허용하지 않는다.
- UI에서 provider fetch, training, materialization을 실행하지 않는다.
- 수익률 예측, 매매 지시, NBER 공식 판정으로 표현하지 않는다.
- 기존 S&P 500과 미국 개별주식 selector 동작을 보존한다.

## Acceptance Criteria

- 현재 actual `LIMITED` snapshot이 `잠정 모델 추정` 확률을 표시한다.
- `READY` fixture는 `검증된 모델 추정`으로 표시된다.
- artifact/확률이 없는 fixture만 `판단 불가`다.
- 2×2 사분면, 과거 실선, 미래 점선, history ribbon이 렌더링된다.
- desktop과 420px에서 가로 overflow가 없다.
- 경제사이클 focused Python tests, TypeScript build, valuation navigation regression, Browser QA를 통과한다.
