# Phase 4 Visualization Enhancement Second Pass

## 목적
이 문서는 Phase 4 Backtest 탭의
시각화 강화 second pass를 기록한다.

이번 단계의 초점:

- compare overlay 차트가 더 바로 읽히도록 만들기
- 전략별 핵심 극값을 table 형태로도 한 번에 확인하게 만들기

## 추가된 기능

### 1. Compare Overlay End Markers

적용 대상:

- `Equity Overlay`
- `Drawdown Overlay`
- `Return Overlay`

추가된 것:

- 각 전략의 latest point marker
- 전략 이름 label

의미:

- compare chart를 보고 있을 때
  각 선이 현재 어디에서 끝나는지 바로 읽을 수 있다
- overlay가 겹쳐도 최신 상태를 더 쉽게 구분할 수 있다

### 2. Strategy Highlights 탭

compare 결과에 새 `Strategy Highlights` 탭이 추가되었다.

표시 항목:

- `High Date / High Balance`
- `Low Date / Low Balance`
- `End Date / End Balance`
- `Best Period Date / Return`
- `Worst Period Date / Return`

의미:

- compare를 그래프만으로 읽지 않고,
  전략별 핵심 극값을 compact table로 바로 비교할 수 있다

## 구현 파일

- `app/web/pages/backtest.py`

## 검증

확인한 것:

- compare overlay chart 함수가 end marker를 포함해 정상 렌더링 가능한 형태로 생성됨
- `Equal Weight` / `GTAA` 비교 기준 highlight row 생성 확인
- end balance 예시:
  - `Equal Weight`: `30188.4`
  - `GTAA`: `22589.1`

## 현재 한계

- compare overlay 위에는 아직 high / low marker까지는 직접 찍지 않는다
- end marker가 많아지면 4개 전략 비교에서는 약간 혼잡할 수 있다
- help `?` 스타일은 일부 영역만 통일됐고 전면 통일은 아직 아님

## 다음 자연스러운 확장

- compare chart highlight toggle
- high / low marker까지 직접 overlay할지 검토
- `?` help UI 전반 스타일 통일
