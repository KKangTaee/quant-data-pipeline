# Futures Macro Observation Status And History Upgrade Design

## 이걸 하는 이유?

현재 Futures Macro 화면은 실제 저장 일봉으로 계산을 마친 `현재 관측`까지
미래 조건부 전망과 같은 `PROVISIONAL` 배지로 표시한다. 그 결과 사용자는
현재 상태가 임시 데이터인지, 미래 전망의 검증 기준이 잠정인지 구분하기 어렵다.

자산별 카드도 1D / 5D / 20D 현재 관측과 다음 5D / 20D 전망을 한 카드에 담으면서,
두 미래 전망 중 낮은 publication status 하나를 카드 전체 배지로 사용한다.
현재 관측값까지 잠정 추정처럼 보이는 원인이다.

또한 core futures 17종의 저장 일봉을 실제 점검한 결과 13종은
`2021-06-01`부터 약 5년, 4종은 `2016-07-18`부터 약 10년이 있다.
현재 snapshot materializer도 전망 loader에 `years=5`를 전달하므로,
20D 조건부 전망은 독립 표본 42개에 머물러 verified 최소 표본 60개를 충족하지 못한다.

이번 작업은 현재 관측과 미래 전망의 상태 체계를 분리하고, 일봉 이력을 10년으로
확장한 뒤 기존 검증 기준을 그대로 다시 적용한다. 기준을 낮춰 `VERIFIED`를 만들거나
결과를 강제로 승격하지 않는다.

## 승인된 전체 흐름

### 1차 — 현재 관측 상태 분리

- hero와 `현재 관측` horizon은 미래 전망용 `estimate_status`를 사용하지 않는다.
- 별도 `observation_status`를 사용한다.
  - `OBSERVED`: compatible 저장 snapshot이 있고 현재 pattern이 `READY`
  - `PARTIAL`: 현재 관측은 표시할 수 있지만 pattern 또는 coverage가 `PARTIAL / LIMITED`
  - `UNAVAILABLE`: compatible snapshot이나 현재 pattern을 표시할 근거가 없음
- 화면 문구는 각각 `관측 완료`, `일부 관측`, `관측 불가`로 표시한다.
- 현재 관측에는 확률, 예측 정확도 또는 `VERIFIED` 개념을 적용하지 않는다.

### 2차 — 자산 카드의 현재와 전망 상태 분리

- 각 카드 상단에는 `현재 · 관측 완료/일부 관측/관측 불가`를 표시한다.
- 다음 5D와 다음 20D에는 horizon별 publication status를 각각 표시한다.
  - `VERIFIED`: 고정된 외부 공개 기준을 모두 통과한 조건부 전망
  - `PROVISIONAL`: 계산은 가능하지만 공개 기준 일부 미달
  - `UNAVAILABLE`: 계산 또는 공개할 표본 부족
- 한 horizon의 낮은 상태가 다른 horizon 또는 현재 관측 상태를 덮어쓰지 않는다.
- 현재 방향 텍스트와 미래 방향 텍스트는 기존 계산 결과를 유지한다.

### 3차 — 10년 일봉 백필과 snapshot 재계산

1. 사용자가 기존 `일봉 갱신` 버튼을 누른다.
2. core futures 17종에 `10y / 1d`를 요청하고 기존 UPSERT 경로로 저장한다.
3. 공급자가 10년 전체를 반환하지 않는 종목은 실제 반환된 범위만 저장한다.
4. 누락 구간을 보간하거나 합성하지 않는다.
5. 수집된 latest daily marker를 기준으로 10년 lookback의 compact snapshot을 재계산한다.
6. 평상시 Overview 진입은 기존처럼 저장 snapshot 한 행만 읽으며 재계산하지 않는다.

`일봉 갱신`을 매번 누를 때 10년 범위를 다시 요청하지만 UPSERT이므로 기존 행을
중복 생성하지 않는다. 별도 백필 버튼이나 전망 재계산 버튼은 만들지 않는다.

### 4차 — 동일 publication gate 재평가

다음 기준은 변경하지 않는다.

- minimum independent episodes `30`
- verified episodes `60`
- probability: Brier baseline 개선, calibration error `<= 0.10`,
  chronological fold improvement ratio `>= 0.60`
- path: median error baseline 개선, middle-50% coverage `0.35~0.65`,
  evaluated chronological folds `>= 2`
- 최종 horizon status는 probability와 path 중 더 낮은 상태
- 통계적으로 구분되는 방향 우위 기준도 그대로 유지

10년 백필 뒤 실제 usable feature 기간, 독립 표본, Brier, calibration,
fold stability, path error, coverage를 다시 기록한다. 20D가 표본 60개를 넘더라도
나머지 기준을 통과하지 못하면 계속 `PROVISIONAL`이다.

### 5차 — 결과 기반 조건부 모델 개선

4차 결과에서 남은 실패 항목이 있을 때만 별도 설계와 테스트로 시작한다.

- 표본만 부족하면 데이터 범위 / 공통 usable 기간 문제로 분류한다.
- probability calibration 또는 fold stability 실패는 similarity / weighting 후보를
  chronological walk-forward로 비교한다.
- path error 또는 coverage 실패는 terminal distribution / interval construction 후보를
  baseline과 비교한다.
- out-of-sample 개선이 확인되지 않은 후보는 채택하지 않는다.
- gate 하향, in-sample 성능만으로 승격, status hard-code는 금지한다.

5차는 이번 1~4차 구현 커밋에 섞지 않는다. 실제 재평가 결과가 입력 계약이다.

## 상태 데이터 계약

### Python payload

- `ObservationStatus = OBSERVED | PARTIAL | UNAVAILABLE`
- `EstimateStatus = VERIFIED | PROVISIONAL | UNAVAILABLE`
- hero: `observation_status`
- current horizon: `observation_status`, `kind=observation`
- future horizon: `estimate_status`, `kind=conditional_outlook`
- asset pathway:
  - `observation_status`
  - `outlook.five_day_status`
  - `outlook.twenty_day_status`

현재 horizon에 `estimate_status=PROVISIONAL`을 채우는 호환용 mapping은 제거한다.
React는 `kind`에 따라 올바른 status field만 읽는다.

### React 표시 계약

- hero side label은 `관측 상태`, 값은 한국어 `관측 완료/일부 관측/관측 불가`
- 현재 horizon 배지는 관측 상태 색을 사용한다.
- 미래 horizon 배지는 기존 estimate 상태 색과 영문 status를 유지하되,
  보조 문구로 검증 의미를 설명한다.
- asset card header는 현재 관측 상태를 표시한다.
- 각 전망 행에는 `5D PROVISIONAL`, `20D VERIFIED`처럼 독립 status를 표시한다.
- 색만으로 상태를 구분하지 않고 text label을 항상 함께 둔다.

## 10년 계산 계약

- shared constant로 history horizon `10`년과 provider period `10y`를 관리한다.
- overview daily action, snapshot materializer, pattern validation loader,
  command / trace copy가 같은 값을 사용한다.
- training / validation은 실제 feature가 존재하는 날짜만 사용한다.
- 모든 required family가 없는 과거 행을 완전한 행처럼 간주하지 않는다.
- point-in-time rolling feature와 chronological split을 유지한다.
- forward horizon 이후 데이터를 현재 feature 계산에 사용하지 않는다.
- history window 변경은 계산 결과 계약 변경이므로 algorithm version을 올리고
  이전 5년 snapshot을 compatible latest로 읽지 않는다.

## 변경 가능성이 있는 파일

### Service / payload

- `app/jobs/overview_actions.py`
- `app/services/futures_macro_snapshot.py`
- `app/services/futures_macro_pattern_validation.py`
- `app/web/overview/futures_macro_helpers.py`

### React

- `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
- `MacroContextSection.tsx`
- `PatternHorizonSection.tsx`
- `AssetPathwaysSection.tsx`
- `style.css`
- production bundle

### Tests / task records

- focused Python service / contract tests
- React source contract and production build
- active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- 구현 종료 시 durable finance docs와 root handoff log

## 오류와 경계 처리

- 일부 종목 10년 미확보: 수집 성공 행은 보존하고 실제 usable 기간을 표시한다.
- 일봉 수집 실패: 기존 compatible snapshot을 보존하고 새 snapshot으로 덮어쓰지 않는다.
- 수집 partial success: 저장된 marker가 바뀐 경우 실제 보유 행으로 materialize하되
  observation coverage가 부족하면 `PARTIAL`로 표시한다.
- snapshot 계산 실패: ingestion 결과와 오류를 분리하고 이전 snapshot을 보존한다.
- snapshot schema / algorithm 불일치: 탭 진입 중 계산하지 않고 `일봉 갱신`을 안내한다.
- 10년 재평가 후 전망 기준 미달: 정상 결과로 `PROVISIONAL`을 유지한다.

## 테스트 계약

### Python TDD

- current hero / horizon은 `observation_status`를 내고 `estimate_status`를 내지 않는다.
- READY / PARTIAL / unavailable 입력이 각각 OBSERVED / PARTIAL / UNAVAILABLE로 매핑된다.
- asset card는 current status와 5D / 20D status를 독립적으로 보존한다.
- daily refresh가 `10y / 1d`를 요청한다.
- materializer가 outlook loader에 10년을 전달한다.
- algorithm version 변경으로 이전 snapshot이 incompatible 처리된다.
- publication gate 상수와 판정 경계가 변경되지 않는다.
- 10년 synthetic history에서도 chronological / point-in-time 계약이 유지된다.

### Actual data verification

- core 17종별 first / last date, row count, 누락 종목을 백필 전후 기록한다.
- materialized snapshot의 usable date range와 5D / 20D independent episode를 기록한다.
- 기존과 새 Brier, calibration, fold ratio, path error, coverage를 비교한다.
- `VERIFIED` 여부와 무관하게 각 gate pass / fail을 그대로 보고한다.

### React / Browser QA

- TypeScript / Vite production build가 통과한다.
- hero와 current horizon에 `PROVISIONAL`이 표시되지 않는다.
- asset card의 현재, 5D, 20D status가 서로 독립적으로 보인다.
- 방법론 / 원본 추적에는 실제 10년 요청과 usable 기간이 모순 없이 표시된다.
- desktop과 420px에서 clipping / horizontal document overflow가 없다.
- console error가 없다.
- QA screenshot 한 장을 generated artifact로 남기고 commit하지 않는다.

## 검토한 대안

1. **채택 — 관측/전망 status type 분리 + 10년 동일 gate 재평가**
   - 현재 사실과 미래 불확실성을 가장 명확하게 구분한다.
   - 데이터 증가 효과와 모델 효과를 분리해서 평가할 수 있다.
2. **기각 — 단일 status 유지, 문구만 변경**
   - asset card와 current horizon에서 같은 의미 혼합이 반복된다.
3. **기각 — 현재 status 제거, 미래 status만 표시**
   - 현재 관측의 coverage 부족이나 snapshot 부재를 사용자가 확인할 수 없다.
4. **기각 — 10년 백필과 동시에 gate 완화**
   - 데이터 증가 효과를 평가할 수 없고 `VERIFIED` 의미가 약해진다.

## 완료 조건

- 현재 관측 어디에도 미래 전망 의미의 `PROVISIONAL`이 붙지 않는다.
- hero, current horizon, asset pathway가 관측 상태를 일관되게 표시한다.
- 5D와 20D는 서로 독립된 publication status를 유지한다.
- 기존 `일봉 갱신` 한 번으로 core 17종 10년 요청과 compact snapshot 재계산이 끝난다.
- Overview 첫 진입은 저장 snapshot만 읽는 현재 성능 계약을 유지한다.
- 변경하지 않은 gate로 actual 10년 데이터 재평가 결과가 남는다.
- focused tests, production build, diff / compile check, desktop / 420px Browser QA가 통과한다.
- 5차 모델 개선은 실제 실패 근거가 있을 때만 새 설계로 시작한다.
