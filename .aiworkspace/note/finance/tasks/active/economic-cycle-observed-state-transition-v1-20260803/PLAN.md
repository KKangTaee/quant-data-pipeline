# Economic Cycle Observed State / Transition V1 Plan

State: active
Last Updated: 2026-08-03

## 이걸 하는 이유?

현재 경제사이클 화면은 결정 규칙으로 만든 현재 국면을 다시 확률모델로 추정하고,
검증 기준을 통과하지 못한 1·2개월 확률과 확률분포 좌표를 실제 경기 경로처럼
표시한다. 사용자는 현재 상태와 향후 확인 조건을 알고 싶지만, 현재 화면은 낮은
신뢰도의 월별 예측값을 먼저 해석하게 한다.

현재 국면을 실제 실물지표의 수준·변화 속도로 직접 판정하고, 미래 월별 확률 대신
국면 유지 근거와 조건부 전환 상태를 제공한다. 기존 `자산별 확인 포인트`는 사용자가
명시적으로 유지하기로 결정했으므로 디자인·계산·카드 구조를 모두 동결한다.

## Roadmap

### 1차 — Observed-state domain contract

- 3개월 평균 경기 수준, 직전 3개월 대비 변화 속도, 실물지표 확산도를 계산한다.
- 회복 / 확장 / 둔화 / 위축의 상대 성장순환 국면을 deterministic하게 판정한다.
- NBER 침체는 current-state override가 아닌 별도 historical reference로 둔다.
- 완료 조건: 같은 입력에서 현재 국면과 그래프 좌표가 항상 일치한다.

### 2차 — Transition monitor / persistence

- 최근 1·3·6개월 변화와 다음 인접 국면의 조건을 계산한다.
- 상태를 `유지 / 전환 감시 / 전환 확인`으로 제한한다.
- 선행·금융·물가·정책 요인은 전환 설명에만 사용하고 현재 국면을 바꾸지 않는다.
- 완료 조건: 단일 월의 변화는 전환 확인이 되지 않고, 명시된 세 조건이 충족될 때만
  확인 상태가 된다.

### 3차 — Persistence / read model / UI replacement

- snapshot에 observed-state, recent-change, transition-monitor 결과를 저장한다.
- service payload를 `economic_cycle_v3`로 바꾸고 미래 확률을 제품 계약에서 제거한다.
- 실제 좌표의 과거 경로, 현재점과 조건 방향만 표시한다.
- 완료 조건: 현재/+1M/+2M 확률 카드, 미래점과 probability coordinate가 화면에 없다.

### 4차 — Regression / replay / Browser QA

- PIT replay, revision sensitivity, transition persistence를 검증한다.
- desktop / tablet / phone에서 레이아웃과 문구를 확인한다.
- `market_implications` payload와 기존 자산 카드 렌더링의 deep-equality 회귀를 검증한다.
- 완료 조건: 관련 Python/React 테스트, build, DB round-trip과 Browser QA가 통과한다.

## Scope

- `finance/economic_cycle_features.py`
- 신규 observed-state domain module
- `finance/economic_cycle_pipeline.py`
- `finance/data/db/schema.py`
- `finance/data/economic_cycle_results.py`
- `finance/loaders/economic_cycle.py`
- `app/services/overview/economic_cycle.py`
- `app/web/streamlit_components/economic_cycle_workbench/`의 상단 국면 영역
- 관련 Python / React / persistence tests
- economic-cycle durable docs와 task 기록

## Frozen Scope

- `finance/economic_cycle_asset_pathways.py` 계산과 출력 계약
- `finance/economic_cycle_interpretation.py`의 자산별 해석 계약
- `MarketImplicationCard` 이하 자산 카드 구성과 CSS
- `market_implications` payload의 필드, 순서와 의미
- 자산별 현재 움직임, 관찰 경로, 현재 해석, 다음 확인 조건

상단 phase vocabulary를 연결하기 위해 자산 영역의 계산·카피·레이아웃을 바꾸지 않는다.

## Out Of Scope

- dynamic-factor / Markov-switching 모델의 제품 공개
- 확률 예측의 재보정 또는 새로운 1·2개월 확률 UI
- NBER 공식 침체 판정 대체
- 자동 매매, 자산배분 추천 또는 포트폴리오 조정 지시
- 경제사이클 데이터 수집 provider 교체

## Stop Condition

observed-state와 transition-monitor의 도메인·저장·service·UI 계약이 일치하고, 미래
확률 노출이 제거되며, 기존 자산 영역이 payload와 화면에서 동일함을 회귀 검증한 뒤
desktop·tablet·phone Browser QA와 문서 동기화까지 끝나면 완료한다.
