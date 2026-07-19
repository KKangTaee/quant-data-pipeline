# Futures Macro Ribbon / Asset Status / V4 Runtime Design

## 이걸 하는 이유?

`최근 60거래일 체제`는 색으로 체제를, 사선으로 전환 시도를 표현하지만 화면에 색상 범례가 없어 사용자가 각 색의 의미를 추측해야 한다.

첨부 화면의 `자산별 확인 포인트`는 카드 전체를 `PROVISIONAL`로 표시한다. 이 화면은 현재 관측과 미래 전망을 분리하기 전 계약이며, 승인된 최신 계약은 카드 상단의 현재 관측 상태와 다음 5D·20D의 전체 전망 상태를 각각 표시한다.

로컬 worktree들은 같은 MySQL을 사용한다. 구버전 runtime이 `overview_current`를 다시 materialize하면 최신 V4 row가 구버전으로 덮일 수 있다. 실제 저장 row는 `2026-07-19 11:42:53`에 `pattern_outlook_v2_empirical_path`로 바뀌었고, 현재 `sub-dev`는 `pattern_outlook_v4_conservative_status_10y`를 기대한다.

이번 작업은 `sub-dev`의 표시 계약을 명확히 하고 현재 저장 일봉으로 V4 snapshot을 복구한다. 예측 모델이나 검증 기준을 바꾸지 않는다.

## 검토한 접근

### A. 범례 + 상태 역할 명시 + V4 재물질화 — 채택

- 60일 ribbon에 네 체제 색상과 전환 사선 범례를 직접 표시한다.
- 자산 카드 상단은 현재 관측 상태만 표시한다.
- 다음 5D·20D badge는 자산별 독립 검증이 아니라 `전체 전망`의 publication status임을 문구로 밝힌다.
- 현재 저장된 10년 일봉으로 V4 compact snapshot을 다시 materialize한다.
- desktop / 420px 실제 화면에서 검증한다.

장점은 사용자가 색과 상태의 소유자를 화면만 보고 이해할 수 있고, 모델·DB schema를 건드리지 않는다는 점이다.

### B. V4 snapshot만 재물질화 — 제외

구버전 row는 복구하지만 색상 범례와 상태 의미의 혼동은 남는다.

### C. algorithm version별 snapshot row를 즉시 저장 — 이번 범위에서 제외

공유 worktree의 구버전 덮어쓰기를 구조적으로 막지만 unique key / loader / migration 계약이 바뀐다. 이번 UI clarification과 별도 DB 설계로 다룬다.

## UI 계약

### 최근 60거래일 체제

가로 순서는 `과거 → 최근`이다.

- 초록: `위험선호`
- 빨강: `방어`
- 주황: `물가·금리 부담`
- 청회색: `혼재`
- 사선: `전환 시도`

범례는 색만 사용하지 않고 text label을 항상 함께 표시한다. 각 날짜 cell의 기존 hover / focus title은 유지한다.

### 자산별 확인 포인트

- 카드 header: `관측 완료 / 일부 관측 / 관측 불가`
- 현재 1D / 5D / 20D: 저장 일봉으로 계산한 관측 방향
- 다음 5D / 20D: 해당 자산 family의 보조 방향
- 미래 badge: `전체 전망 · VERIFIED/PROVISIONAL/UNAVAILABLE`

미래 badge는 개별 자산 가격 예측의 검증 상태가 아니다. 전체 5D 또는 20D 조건부 체제의 publication status를 상속한 보조 근거임을 표시한다.

## 데이터와 runtime 계약

- `sub-dev`의 기존 `pattern_outlook_v4_conservative_status_10y` 계산을 사용한다.
- 저장된 10년 futures daily OHLCV를 다시 읽어 compact snapshot을 materialize한다.
- provider 추가 수집은 필수 조건이 아니다. 최신 marker가 같아도 구버전 row를 교체하기 위해 force materialization은 허용한다.
- 완료 후 raw row의 algorithm version, current observation status, 5D / 20D status를 확인한다.
- 구버전 worktree의 후속 overwrite 가능성은 active task `RISKS.md`에 남기고 이번에 schema를 바꾸지 않는다.

## 파일 범위

- `app/web/streamlit_components/futures_macro_workbench/src/PatternRibbonSection.tsx`
- `app/web/streamlit_components/futures_macro_workbench/src/AssetPathwaysSection.tsx`
- `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- `app/web/streamlit_components/futures_macro_workbench/component_static/`
- `tests/test_service_contracts.py`
- 기존 Futures Macro active task closeout 문서

## 검증 계약

1. source contract는 네 색상 label, `과거 → 최근`, `전환 시도`를 요구한다.
2. 자산 카드 source contract는 current observation label을 유지하고 미래 status를 `전체 전망`으로 설명하도록 요구한다.
3. 기존 observation / future payload separation tests가 계속 통과한다.
4. Vite production build와 focused Python contracts가 통과한다.
5. 실제 V4 snapshot은 current `OBSERVED`, 5D / 20D는 현재 검증값에 따른 status를 반환한다.
6. desktop / 420px에서 범례와 카드가 잘리지 않고 browser console error가 없다.

## 제외 범위

- `main-dev` 또는 다른 worktree 파일 변경
- 예측 모델, Brier / calibration / path gate 변경
- 자산 family별 독립 예측 모델 추가
- DB schema / unique key migration
- 기존 worktree process 종료 또는 정리
