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

## 2026-07-18 Stable Coordinate Follow-up

### 문제와 원인

5D / 20D 전환 때 `20D 전 → 5D 전 → 현재`의 원본 관측 좌표는 같지만,
선택된 conditional path의 모든 step median과 숨겨진 step별 q25/q75까지 chart bound에 다시 넣어
화면 좌표가 달라진다. 실제 snapshot에서 x bound는 5D `1.503856`, 20D `2.003118`이고,
현재점 화면 x는 `221.335 → 255.896`으로 이동한다. 이는 관측값 변경이 아니라 selected-horizon auto-fit 결과다.

말일 range 하나만 보이는 현재 UI에서 숨겨진 중간 step range가 배율을 바꾸는 것은
관측과 전망을 같은 좌표계에서 비교한다는 화면 목적과 맞지 않는다.

### 검토한 방식

1. **5D / 20D 공통 visible-data bound — 채택**
   - 세 관측 anchor, 두 horizon의 step별 median path, 두 horizon 말일의 표시되는 q25/q75 range를 한 번 합쳐 bound를 계산한다.
   - 5D / 20D / 관측만 전환에서 축과 관측 anchor가 고정되고, 실제 표시되는 전망 요소도 잘리지 않는다.
2. **관측 anchor만으로 고정**
   - 관측 비교는 가장 안정적이지만 20D 예상 경로와 말일 range가 화면 밖으로 잘릴 수 있어 채택하지 않는다.
3. **selected-horizon auto-fit 유지 + 배율 변경 안내**
   - 각 전망을 크게 볼 수 있지만 toggle 비교 시 관측 이동처럼 보이는 문제가 남아 채택하지 않는다.

### 승인된 좌표 계약

- `patternMap.path`에서 만든 `20D 전 / 5D 전 / 현재`의 SVG `cx / cy`는 `관측만 / 다음 5D / 다음 20D`에서 완전히 동일해야 한다.
- chart bound는 selected card가 아니라 사용 가능한 5D / 20D conditional path 전체에서 한 번 계산한다.
- bound에는 두 horizon의 실제로 보이는 step별 median `x / y`를 포함한다.
- q25/q75는 실제로 표시하는 각 horizon 말일 terminal range만 bound에 포함한다.
- 화면에서 제거한 중간 step q25/q75는 bound에도 포함하지 않는다.
- selected horizon은 예상 polyline, terminal, terminal range, legend, 우측 확률만 바꾼다.
- `UNAVAILABLE` path는 공통 bound에서 제외하고 예측 layer도 기존 계약대로 숨긴다.
- 서비스 통계, 확률, episode, validation, payload 좌표는 변경하지 않는다.

### 검증 계약

- RED/GREEN source contract로 selected `forecastPoints`가 scale owner가 아닌지 확인한다.
- 5D와 20D의 공통 scale 입력에 두 median path와 두 terminal range가 포함되는지 확인한다.
- actual Browser QA에서 세 상태의 anchor `cx / cy`를 수집해 완전 동일성을 비교한다.
- 5D step-5 / 20D step-20 range와 서로 다른 terminal / polyline은 계속 변경되는지 확인한다.
- desktop과 420px overflow, label clipping, console error를 다시 확인한다.

## 2026-07-18 Net Direction Follow-up

### 문제와 원인

현재 조건부 점선은 현재점 뒤에 5개 또는 20개의 날짜별 중앙 위치를 모두 연결한다.
각 step의 x/y 중앙값은 유사 episode 집합에서 독립적으로 계산되므로 연결선은 하나의 실제 대표 episode가 아니고,
중간에 방향을 여러 번 바꾸는 것처럼 보일 수 있다. 이 지그재그는 통계 입력 오류가 아니지만
사용자가 원하는 `결국 어느 방향으로 얼마나 이동하는가`를 가린다.

### 검토한 방식

1. **현재 → 말일 중앙 위치의 예상 순이동 — 채택**
   - 현재와 5D/20D terminal을 한 개의 직선 점선으로 연결한다.
   - 기존 고정 크기 방향 marker와 terminal range를 유지해 방향과 최종 분산을 분리해 읽는다.
   - 중간 step median은 서비스·payload·검증에 남지만 지도에서는 실제 경로처럼 연결하지 않는다.
2. **날짜별 중앙값을 smoothing한 곡선**
   - 시각적으로 부드럽지만 계산되지 않은 중간 형상을 새로 만들어 통계적 의미가 불명확해지므로 채택하지 않는다.
3. **가장 대표적인 단일 과거 episode 경로**
   - 실제 한 경로라는 장점은 있지만 한 사례를 미래 대표 경로처럼 과대해석할 위험이 있어 채택하지 않는다.

### 승인된 화면 계약

- 조건부 점선은 `현재 → 선택 horizon 말일 예상 중앙 위치`의 한 방향 순이동만 표시한다.
- 점선은 1~N일의 실제 또는 중앙 일별 경로가 아니며, 중간 굴곡이나 waypoint를 표시하지 않는다.
- terminal circle, `5일 후 예상 위치` / `20일 후 예상 위치`, fixed 9-unit direction marker는 유지한다.
- 음영 박스는 선택 horizon 말일의 축별 q25~q75 도착 범위 하나를 유지한다.
- legend는 `5일 예상 순이동` / `20일 예상 순이동`으로 바꾼다.
- 우측 설명은 점선이 `시작점에서 말일 중앙 위치까지의 예상 순이동`이며 중간 일별 경로가 아님을 명시한다.
- 공통 scale은 세 관측 anchor와 두 horizon terminal/range만으로 계산한다. 화면에서 제거한 중간 median과 q25/q75는 scale을 바꾸지 않는다.
- `관측만 / 5D / 20D` 전환에서 세 관측 anchor 좌표는 계속 동일해야 한다.

### 데이터와 범위

변경하지 않는다.

- stepwise median과 q25/q75 서비스 계산
- chronological path validation, probability, episode, publication status
- payload, cache version, DB/provider/schema
- 현재 관측 실선과 네 체제 색상

변경 파일은 `PatternMapSection.tsx`, 관련 source contract, Vite production bundle과 최소 task/doc 기록으로 제한한다.

### 검증 계약

- RED/GREEN source contract는 forecast shape가 현재와 terminal만 소비하고 `forecastPoints.map`으로 polyline을 만들지 않는지 확인한다.
- 공통 scale에서 숨겨진 stepwise median이 제거되고 두 terminal range가 유지되는지 확인한다.
- 실제 Browser QA는 5D/20D 각각 조건부 직선 1개, direction 1개, terminal 1개, 말일 range 1개를 확인한다.
- 실제 SVG forecast의 시작점은 현재 anchor와 같고 끝점은 selected terminal과 같아야 한다.
- `관측만`은 forecast layer 0개, 세 상태의 관측 anchor 좌표는 동일해야 한다.
- desktop/420px overflow와 console error를 확인한다.

### 완료 조건

- 사용자가 점선을 한 번에 `현재에서 말일까지의 순방향`으로 읽을 수 있다.
- 중간 step별 중앙값 연결로 생기던 지그재그가 지도에서 사라진다.
- 최종 도착 범위와 확률·검증 상태는 그대로 유지된다.
