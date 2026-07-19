# Backtest Component Static Distribution V1 Design

Status: User-approved direction, written-spec review pending
Date: 2026-07-19

## 이걸 하는 이유?

Overview의 시장맥락·매크로 React 컴포넌트는 빌드 결과를 `component_static/`에 만들고 Git으로 배포한다. 따라서 새 worktree나 clean checkout에서도 Streamlit만 실행하면 디자인이 바로 열린다.

Backtest React 컴포넌트는 `frontend/build/`을 사용한다. 저장소의 전역 `.gitignore`가 `build/`을 제외하기 때문에 최근 컴포넌트의 빌드 산출물이 병합되지 않았고, clean worktree에서는 Python fallback UI가 표시됐다. 이 차이를 없애고 Backtest도 checkout 자체로 실행 가능한 정적 컴포넌트 계약을 갖게 한다.

## 목표

- `app/web/components/*` 아래 현재 React frontend 12개를 모두 `frontend/component_static/` 출력으로 통일한다.
- 모든 Python component loader가 `component_static/index.html`이 있을 때만 React 컴포넌트를 선언한다.
- 12개 빌드 결과를 Git에 포함해 별도 `npm ci && npm run build` 없이 Streamlit 실행만으로 React UI가 열린다.
- 기존 Backtest·Practical Validation·Final Review UI 동작과 Python/React ownership은 바꾸지 않는다.

## 대상 컴포넌트

1. `backtest_analysis_decision_workspace`
2. `backtest_analysis_result_workspace`
3. `backtest_factor_readiness_panel`
4. `backtest_handoff_action`
5. `backtest_policy_signal_board`
6. `backtest_price_freshness_preflight`
7. `backtest_price_refresh_action`
8. `backtest_workflow_shell`
9. `final_review_investment_report`
10. `practical_validation_data_action_board`
11. `practical_validation_decision_workspace`
12. `practical_validation_fix_queue`

## 검토한 접근

### A. 전체를 `component_static/`으로 통일 — 채택

- Overview와 같은 저장·로딩 규칙을 사용한다.
- 전역 `build/` ignore 예외를 만들지 않는다.
- 새 컴포넌트가 추가될 때 같은 패턴을 복사할 수 있다.
- 기존 추적 `build/` 파일 삭제와 새 정적 파일 추가로 최초 diff가 크다.

### B. `build/`을 `.gitignore`에서 예외 처리

- Python/Vite 코드 변경은 가장 작다.
- 저장소 전역 ignore와 컴포넌트별 예외가 충돌하고 Overview와 다른 규칙이 계속 남는다.
- 새 component 경로마다 예외 누락 가능성이 있다.

### C. `build/`과 `component_static/`을 모두 읽는 과도기 loader

- 단계적 전환에는 안전하다.
- 이번 변경은 같은 커밋에서 소스와 산출물을 함께 옮길 수 있어 이중 경로가 필요하지 않다.
- 어느 산출물이 canonical인지 모호해지고 stale build가 우선 로드될 위험이 있다.

## 채택 설계

### Vite 출력 계약

각 `frontend/vite.config.ts`의 `build.outDir`을 `component_static`으로 바꾸고 `emptyOutDir: true`를 명시한다. 빌드할 때 이전 hashed asset이 남지 않게 한다.

### Python loader 계약

각 `component.py`는 다음 경로를 canonical 정적 root로 사용한다.

```text
Path(__file__).parent / "frontend" / "component_static"
```

단순히 디렉터리가 존재하는지가 아니라 `component_static/index.html`이 실제로 존재할 때만 `streamlit.components.v1.declare_component`를 호출한다. 산출물이 불완전하면 기존 fallback 동작을 유지한다.

### Git 산출물 계약

- 기존에 추적되던 `frontend/build/` 산출물은 제거한다.
- 새 `frontend/component_static/index.html`과 hashed JS/CSS assets를 Git에 포함한다.
- `node_modules/`, Vite cache, source map 임시 파일은 포함하지 않는다.
- 프런트엔드 소스를 바꾸는 후속 작업은 해당 package를 다시 빌드하고 변경된 정적 산출물까지 같은 커밋에 포함해야 한다.

### 테스트 계약

구현 전 회귀 테스트를 추가하거나 기존 테스트를 강화해 12개 package 모두에 대해 아래를 확인한다.

- Vite 출력 경로가 `component_static`이다.
- Python loader가 `component_static/index.html`을 기준으로 availability를 판정한다.
- canonical 정적 entry와 asset이 Git 추적 대상이다.
- 과거 `frontend/build/` 경로를 loader/test가 더 이상 요구하지 않는다.

기존 개별 service contract test의 fixture 경로도 `component_static`으로 옮긴다. UI payload, event, state ownership assertion은 변경하지 않는다.

## 전체 진행 로드맵

### 1차 — 배포 계약과 회귀 테스트

- 목적: 12개 컴포넌트가 따라야 할 단일 static distribution contract를 고정한다.
- 범위: packaging/service contract tests.
- 완료 조건: 기존 코드에서 새 테스트가 실패하고, 누락 컴포넌트를 정확히 식별한다.

### 2차 — loader/Vite/산출물 마이그레이션

- 목적: 모든 Backtest 계열 React component를 Overview 방식으로 전환한다.
- 범위: 12개 `component.py`, 12개 `vite.config.ts`, 기존/신규 빌드 산출물.
- 완료 조건: 전체 npm build 성공, 정적 entry/assets Git 추적, 기존 build 산출물 제거.

### 3차 — clean checkout 및 실제 화면 검증

- 목적: 별도 frontend build 없이 Streamlit만으로 React UI가 열리는지 증명한다.
- 범위: Git 추적 검사, Python tests, Streamlit Browser QA.
- 완료 조건: clean-tree 상당의 복제본에서 component availability가 true이고 Backtest 실제 화면에 React shell이 표시되며 QA 스크린샷을 확보한다.

## 오류 처리와 롤백

- 특정 package 빌드가 실패하면 그 package의 산출물을 커밋하지 않고 전체 마이그레이션을 완료 처리하지 않는다.
- `index.html`이 없으면 loader는 React를 선언하지 않고 기존 fallback을 사용한다. `index.html`은 있지만 참조 asset이 없으면 browser load error가 되므로 repository contract가 entry와 참조 asset의 존재·Git 추적을 검증한다.
- 문제가 있으면 설계 이후 구현 commit sequence를 함께 revert해 기존 `build/` loader 계약으로 돌아갈 수 있다.

## 위험과 trade-off

- 정적 JS/CSS가 Git에 들어가 저장소 크기와 frontend 변경 diff가 증가한다.
- 소스만 수정하고 재빌드를 빠뜨리면 source/artifact drift가 생길 수 있다. 공통 contract는 path·entry·asset·Git 추적을 검증하고, closeout build가 source/bundle 일치를 확인한다. 자동 deterministic rebuild 비교는 후속 CI 보강 과제다.
- 현재 다른 Backtest 개발이 frontend source를 바꾸고 있다면 마지막 통합 시 정적 산출물을 최신 HEAD에서 한 번 더 빌드해야 한다.

## 비범위

- UI 디자인, 문구, layout 변경
- Backtest 계산·registry·DB·validation 정책 변경
- Streamlit 시작/종료 alias 또는 launcher 재도입
- Overview 컴포넌트 구조 변경

## 완료 정의

1. 12개 loader와 Vite 설정이 `component_static/`을 canonical로 사용한다.
2. 12개 `component_static/index.html`과 참조 assets가 Git에 포함된다.
3. 기존 추적 `frontend/build/` 파일이 제거된다.
4. 관련 Python/frontend tests와 builds가 통과한다.
5. 별도 npm build 없이 실행한 Backtest Browser QA에서 React 디자인을 확인한다.
