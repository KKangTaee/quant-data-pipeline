# Futures Macro Conditional Path Readability Design

## 이걸 하는 이유?

경험적 5D / 20D 조건부 경로는 horizon별로 다른 계산 결과를 보여주지만,
현재 화면은 1일·중간·말일의 넓은 q25~q75 박스가 같은 위치에 겹치고
현재점·예상점·큰 endpoint 화살표까지 한곳에 모여 실제 이동 방향을 읽기 어렵다.

이번 후속은 계산과 검증 계약을 바꾸지 않고,
사용자가 `과거 관측 이동`, `선택 horizon의 예상 이동`, `말일 도착 분산`을
한눈에 구분하도록 시각 레이어를 정리한다.

## 승인된 사용자 해석

- 점선 경로는 현재점에서 시작하는 과거 유사 흐름 기반 1D~5D 또는 1D~20D 중앙 이동이다.
- 예상점은 `5일 후 예상 위치` 또는 `20일 후 예상 위치`로 읽는다.
- 예상점은 가격 목표, 가장 확률 높은 정확한 미래점, 실제 특정 과거 episode가 아니다.
- 음영 박스는 이동경로 전체의 통로가 아니라 선택 horizon 말일의 도착 분산이다.
- 박스는 risk-on x축과 macro-pressure y축의 q25~q75를 각각 조합한 축 정렬 사각형이다.
- 현재 계산은 공동 확률 contour나 covariance ellipse가 아니므로 원·타원으로 바꾸지 않는다.
- probability estimate와 conditional-path publication 상태는 계속 분리하고 더 보수적인 상태를 화면에 쓴다.

## 승인된 화면 계약

### 레이어 순서

뒤에서 앞으로 다음 순서를 유지한다.

1. 기존 네 체제 4분면 색상
2. 선택 horizon 말일의 단일 음영 박스
3. `20D 전 → 5D 전 → 현재` 관측 실선
4. 현재에서 선택 horizon 말일까지의 조건부 점선
5. 관측 anchor, 현재점, 예상점, 분리된 라벨

음영 박스가 선·점·텍스트를 덮지 않도록 항상 첫 번째 데이터 레이어에 둔다.

### 음영 박스

- 5D 선택: step 5의 `lower_x / upper_x / lower_y / upper_y`만 표시한다.
- 20D 선택: step 20의 bounds만 표시한다.
- 기존 step 1과 midpoint 박스는 표시하지 않는다.
- fill은 기존 blue 계열의 약 10% opacity, border는 약 60% opacity의 dashed outline을 사용한다.
- 그래프 내부에 `표본 120개`, `축별 25~75%` 같은 상세 통계 문구를 넣지 않는다.
- legend는 선택에 맞춰 `5일 후 도착 범위` 또는 `20일 후 도착 범위`라고만 쓴다.
- q25~q75와 joint coverage 한계는 우측 설명 또는 방법론 disclosure에 남긴다.

### 점과 화살표

- 현재점 반지름: 10 SVG units.
- 예상점 반지름: 8 SVG units.
- 과거 anchor 반지름: 약 7~8 SVG units.
- 관측·조건부 화살표는 9 SVG units의 고정 크기로 렌더링한다.
- SVG marker는 `markerUnits="userSpaceOnUse"`를 사용해 stroke width에 따라 확대되지 않게 한다.
- 화살표는 endpoint circle 위가 아니라 선 중간의 짧은 direction segment에 둔다.
- 관측 direction은 navy solid, 조건부 direction은 blue dashed/blue arrow로 색과 선 형태를 함께 구분한다.
- 현재 라벨과 예상 라벨은 서로 반대 방향으로 빼고 leader line을 사용해 겹침을 피한다.

### 사용자 문구

- terminal label: `5일 후 예상 위치` / `20일 후 예상 위치`.
- legend: `관측 이동`, `1~5일 예상 이동` / `1~20일 예상 이동`, `5일 후 도착 범위` / `20일 후 도착 범위`.
- 우측 probability reading은 현재 확률, episode count, `PROVISIONAL` / `VERIFIED` / `UNAVAILABLE`를 유지한다.
- 우측 설명은 `과거 유사 흐름 기반 예상 이동이며 실제 미래 경로를 보장하지 않습니다.`로 읽는다.

## 데이터와 계산 경계

변경하지 않는다.

- `app/services/futures_macro_pattern_validation.py`의 stepwise median, q25/q75, chronological path metrics
- `app/web/overview/futures_macro_helpers.py`의 finite coordinate normalization과 unavailable suppression
- 30 / 60 independent episode publication gate
- probability rows, path status, cache version, DB/provider/schema

UI는 기존 `conditional_path.points`의 마지막 point만 박스에 사용하며 새 통계를 계산하지 않는다.

## 변경 파일

- `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`
- `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- `tests/test_service_contracts.py`
- Vite `component_static/` production bundle
- active task `STATUS.md`, `RUNS.md`, `NOTES.md`, `RISKS.md`
- 구현 의미가 달라질 때만 최소 durable Futures Macro docs

## 오류·가용성 처리

- selected horizon 또는 conditional path가 `UNAVAILABLE`이면 점선·예상점·음영 박스를 모두 숨긴다.
- terminal bounds 중 하나라도 finite number가 아니면 박스만 숨기고 기존 unavailable 계약을 따른다.
- 관측 anchor가 부족하면 존재하는 anchor만 표시하며 없는 날짜를 합성하지 않는다.
- 5D / 20D 전환 때 bounds와 labels는 selected card에서만 읽는다.

## 검증 계약

### Source / unit contract

- uncertainty rect는 selected path terminal 하나만 렌더링한다.
- step 1 / midpoint uncertainty selection 로직이 active source에서 제거된다.
- `markerUnits="userSpaceOnUse"`와 고정 arrow size가 존재한다.
- current / terminal radius와 dynamic `일 후 예상 위치` copy를 확인한다.
- dynamic legend가 selected horizon과 일치한다.
- fixed categorical targets, probability fabrication, unavailable path rendering은 다시 생기지 않는다.

### Browser QA

- 관측만: 예상 line / arrow / terminal / box가 모두 0개다.
- 다음 5D: 점선 1, direction arrow 1, 예상점 1, step-5 box 1이다.
- 다음 20D: 점선 1, direction arrow 1, 예상점 1, step-20 box 1이다.
- current / terminal circles와 두 direction arrow가 서로 가리지 않는다.
- desktop과 420px에서 label clipping과 horizontal overflow가 없다.
- console error가 없다.

## 범위 밖

- 통계 모델, 유사 episode 선택, probability calibration 변경
- joint confidence ellipse 또는 경로 전체 uncertainty corridor 계산
- DB schema, provider, ingestion, registry, saved setup 변경
- 가격 목표, 매매 신호, 확정 예측 문구

## 완료 조건

- 선택 horizon당 음영 박스가 정확히 하나만 보인다.
- 화살표와 원이 겹치지 않고 관측·예상 이동 방향이 구분된다.
- 사용자는 그래프에서 `현재 → 예상 위치`를 먼저 읽고 상세 통계는 우측/방법론에서 확인한다.
- focused contracts, Vite build, Python compile/diff check, actual desktop/420px Browser QA가 통과한다.
