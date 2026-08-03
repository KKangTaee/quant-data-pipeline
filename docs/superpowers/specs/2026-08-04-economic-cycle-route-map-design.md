# Economic Cycle Route Map Design

Status: User-selected; pending written-spec review
Date: 2026-08-04

## 이걸 하는 이유

현재 4분면은 경기 수준과 모멘텀을 좌표로 보여준다는 장점이 있지만, 여러 과거
시점을 같은 작은 영역에 찍으면서 점과 라벨이 겹친다. 이 겹침은 현재 위치와 다음
확인 방향을 약하게 만들고, 월별 좌표가 실제보다 정밀한 미래 경로처럼 보이게 한다.

경제사이클 화면의 우선 질문은 아래 두 가지다.

1. 지금 어떤 국면에 있는가?
2. 다음 정식 발표에서 어느 인접 국면 방향을 확인해야 하는가?

따라서 사용자가 선택한 `순환 경로 지도`로 4분면을 교체한다.

## 사용자 선택

검토한 대안은 다음과 같다.

- A. 순환 경로 지도: 현재 국면과 구조적 다음 인접 국면을 원형 경로로 표현
- B. 단일 좌표 나침반: 4분면은 유지하되 현재점과 방향 범위만 표현
- C. 전환 브리지: 현재와 다음 확인 국면을 조건 화살표로 연결

사용자는 A안을 선택했다.

## 화면 구조

### 1. 네 국면 순환 경로

아래 순서를 시계 방향의 고정 경로로 표시한다.

```text
회복 -> 확장 -> 둔화 -> 위축 -> 회복
```

각 노드는 리본과 동일한 국면 색상을 사용한다.

- 회복: 파랑
- 확장: 초록
- 둔화: 주황
- 위축: 빨강

현재 관측 국면 노드는 가장 크게 표시하고 `현재` 라벨을 붙인다. 다른 노드는 얇은
중립 경로 위에 둔다. 중앙에는 현재 국면, 지속 개월과 `현재 관측` 문구를 표시한다.

### 2. 향후 방향 표현

지도 화살표는 확률 예측이 아니라 현재 국면에서 순서상 다음에 확인하는 인접 국면을
표시한다. 기존 `resolveMapDirectionPhase()` 의미를 유지한다.

- anchor와 observed가 인접하면 transition monitor target을 사용한다.
- `non_adjacent_observation`이면 현재 observed phase의 다음 인접 국면을 사용한다.
- 현재 위축 사례에서는 위축에서 회복으로 향하는 경로를 표시한다.

상태별 표현은 다음과 같다.

| Monitor status | Route 표현 | 사용자 문구 |
|---|---|---|
| `MAINTAIN` | 방향 arc 없음 | `현재 국면 유지` |
| `WATCH` | 다음 인접 노드까지 점선 arc | `회복 방향 관찰 · 예측 아님` |
| `CONFIRMED` | anchor에서 target까지 실선 arc | `국면 전환 확인` |
| monitor 없음 | 방향 arc 없음 | `전환 자료 부족` |

점선 arc의 끝 노드는 outline으로 강조한다. 화살표만으로 미래 가능성이 높다고
해석하지 않도록 `예측 아님`을 지도 안과 범례에 함께 둔다.

`WATCH` arc는 현재 observed node에서 `resolveMapDirectionPhase()`가 반환한 node로
향한다. `CONFIRMED` arc는 이미 일어난 전환을 표시하므로 monitor의 anchor node에서
target node로 향한다. 두 phase가 없거나 같으면 arc를 만들지 않는다.

### 3. 과거 흐름 요약

6개월·3개월·1개월·현재 좌표와 개별 점은 지도에서 제거한다. 최근 흐름은 하나의
짧은 문장으로만 요약한다.

- 네 checkpoint 국면이 같으면: `최근 6개월 · 위축 유지`
- 시작과 현재 국면이 다르면: `최근 6개월 · 회복에서 위축으로 변화`
- 자료가 짧으면: `조회 가능한 기간 · 위축 유지`

월별 상세 이력은 이미 존재하는 `최근 12개월 국면 흐름` 리본이 계속 담당한다.
따라서 순환 지도는 현재와 방향, 리본은 월별 과거 이력이라는 역할을 분리한다.

### 4. 수준·모멘텀 정보

순환 지도는 정확한 x/y 좌표를 표시하지 않는다. 경기 수준, 3개월 모멘텀, 지속기간과
수정 민감도는 바로 위 `현재 관측 국면` 카드에 이미 표시되므로 중복하지 않는다.

이 선택으로 정밀 좌표를 한 화면에서 보는 장점은 줄지만, 사용자의 핵심 판단인 현재
국면과 다음 확인 방향은 더 명확해진다.

## 인접 전환 카드와의 관계

오른쪽 `현재 관측과 전환 기준` 카드는 유지한다.

- 순환 경로 지도: 현재 관측 국면 기준의 구조적 다음 방향
- 전환 카드: state machine anchor, target, 날짜와 상세 확인 조건

현재처럼 observed가 위축이고 anchor가 회복인 비인접 사례에서는 지도는
`위축 -> 회복`, 전환 카드는 `회복 -> 확장 확인 조건`을 표시한다. 서로 다른 기준임을
각 제목과 설명에서 명시한다.

## Data Flow

새 provider fetch, DB schema와 service payload 변경은 없다.

```text
cycle_map.points + observed_state + transition_monitor
  -> React route-map view helpers
  -> current node / adjacent direction / history summary
```

`cycle_map.points`의 최대 12개월 payload는 리본과 과거 요약에 계속 사용한다.

## 오류·자료 부족 처리

- current phase가 없으면 원형 경로만 표시하고 중앙에 `판단 제한`을 표시한다.
- history가 없으면 과거 요약을 `과거 이력 부족`으로 표시한다.
- transition monitor가 없으면 방향 화살표를 만들지 않는다.
- 알 수 없는 phase나 status를 임의 국면으로 보정하지 않는다.

## 접근성

- 순환 지도 SVG에 현재 국면과 다음 확인 방향을 포함한 accessible name을 제공한다.
- 현재 노드, 다음 확인 노드와 status는 색뿐 아니라 텍스트와 선 모양으로 구분한다.
- 불필요한 자동 애니메이션은 사용하지 않는다.
- 화면 폭이 좁아지면 지도와 전환 카드를 세로로 배치한다.

## 변경 범위

- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
  - `QuadrantChart`를 `CycleRouteMap`으로 교체
  - route history summary helper 추가
- `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
  - 기존 quadrant 전용 스타일 제거 또는 미사용 정리
  - route node, arc, current/next/status 스타일 추가
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx`
  - 순환 노드, 방향 상태, 과거 요약과 asset freeze 회귀 테스트
- `tests/test_market_context_economic_cycle.py`
  - React source contract를 route-map 구조로 갱신
- `component_static/`
  - 테스트 통과 후 production bundle 재생성

`자산별 확인 포인트`의 payload, markup, copy, card order와 CSS는 수정하지 않는다.

## 검증 기준

1. 네 국면 노드가 고정 순서로 표시된다.
2. 현재 위축 노드가 강조되고 중앙에 지속기간이 표시된다.
3. `WATCH` 상태에서 위축에서 회복으로 점선 arc가 표시된다.
4. `MAINTAIN`에서는 방향 arc가 표시되지 않는다.
5. 지도에 6M/3M/1M/current 개별 점과 좌표축이 남지 않는다.
6. 최근 흐름은 단일 문장으로 요약된다.
7. 12개월 리본과 자산별 확인 포인트는 기존 구조를 유지한다.
8. React test, focused Python test, Vite build와 Browser QA가 통과한다.

## 중요한 Trade-off

- 장점: 점 겹침 제거, 현재 위치와 다음 확인 방향의 즉시 이해, 미래 예측 오해 감소
- 비용: level/momentum의 정확한 좌표 관계를 지도에서 직접 비교할 수 없음
- 보완: 숫자는 현재 관측 카드가, 월별 이력은 12개월 리본이 계속 제공
