# Phase 4 Weighted Portfolio Contribution First Pass

## 목적
이 문서는 Phase 4 Backtest 탭에서
weighted portfolio 결과를
단순 최종 성과 확인을 넘어서
전략별 기여도로 읽을 수 있게 만든 first-pass 구현을 기록한다.

## 추가된 기능

### 1. Contribution 탭

weighted portfolio 결과에 새 `Contribution` 탭이 추가되었다.

이 탭은 현재 두 층으로 구성된다.

- `Weight Snapshot`
- `Contribution Amount`
- `Contribution Share`

### 2. Weight Snapshot

표시 항목:

- `Strategy`
- `Configured Weight`
- `Ending Share`

의미:

- 사용자가 처음 설정한 비중과
  실제 종료 시점에서 각 전략이 차지하는 비중이
  어떻게 달라졌는지 빠르게 비교할 수 있다

### 3. Contribution Amount

stacked area chart로
각 전략이 weighted portfolio 총 balance에
얼마나 기여하는지 보여준다.

의미:

- 단순히 어떤 전략이 더 좋았는지가 아니라
  시간이 지나며 실제 포트폴리오 balance를
  누가 더 많이 끌고 갔는지 볼 수 있다

### 4. Contribution Share

같은 기여도를 퍼센트 share 기준으로 보여준다.

의미:

- 성장 과정에서 전략 간 상대 영향력이
  어떻게 달라졌는지 볼 수 있다

## 구현 파일

- `app/web/pages/backtest.py`

## 계산 방식

first-pass 기준:

- source는 compare 실행으로 생성된 strategy result bundle
- 월말 기준으로 다시 정렬
- `date_policy`
  - `intersection`
  - `union`
  규칙을 그대로 따름
- weighted portfolio를 만들 때 사용한 비중을 기준으로
  월별 contribution amount / contribution share를 계산

즉 구현 목적은
strict attribution engine이 아니라
현재 weighted portfolio 결과를 해석하기 위한
UI-friendly contribution view다.

## 검증

synthetic helper 검증:

- `50 / 50` 조합에서
  - `100 / 100`
  - `110 / 90`
  - `105 / 95`
  예시가
  amount / share 기준으로 기대값대로 분해되는 것 확인

real strategy 검증:

- `Dual Momentum`
- `GTAA`
- weights `50 / 50`
- `intersection`

확인 결과:

- contribution amount shape: `(62, 2)`
- 종료 시점 share:
  - `Dual Momentum`: `0.5213`
  - `GTAA`: `0.4787`

## 현재 한계

- transaction-level attribution은 아니다
- rebalance 시점 이벤트나 전략 교체 이벤트는 아직 직접 표시하지 않는다
- contribution은 현재 compare 결과를 재사용하는 UI layer 계산이다

## 다음 자연스러운 확장

- rebalance event marker
- strategy contribution과 weighted portfolio drawdown 연계
- compare된 개별 전략의 contribution toggle / highlight
