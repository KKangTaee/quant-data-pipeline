# Master Phase Roadmap

## 목적
이 문서는 `finance` 프로젝트를
Phase 기반으로 어떻게 진행할지 큰 틀을 정리하는 상위 로드맵이다.

이 프로젝트의 핵심 목적은 두 가지다.

1. 데이터 수집
2. 백테스트

최종 목표:
- 사용자가 가상의 포트폴리오를 구성할 수 있어야 한다
- 다양한 전략을 선택하거나 직접 구성할 수 있어야 한다
- DB에 저장된 데이터 기반으로 백테스트를 실행할 수 있어야 한다
- 결과 수익률, 포트폴리오 변화, 전략 특성을 시각적으로 확인할 수 있어야 한다

즉 이 프로젝트는
“데이터를 모으는 도구”에서 끝나는 것이 아니라,
최종적으로는 **퀀트 전략 실행 및 백테스트 플랫폼**으로 가는 것을 목표로 한다.

---

## Phase 운영 원칙

앞으로는 아래 원칙으로 진행한다.

1. 큰 기능은 항상 Phase 기준으로 먼저 정리한다
2. 각 Phase는 별도 문서로 범위, 목표, 산출물, 검증 기준을 가진다
3. 실제 진행은 각 Phase의 TODO 보드 문서로 관리한다
4. 추가 요청이나 방향 변경이 생기면
   - 기존 Phase 문서를 업데이트하거나
   - 필요한 경우 새 Phase를 개설한다
5. 새로운 Phase를 열기 전에는
   - 왜 필요한지
   - 이전 Phase와 어떻게 연결되는지
   - 어떤 결과물이 나와야 하는지
   를 먼저 사용자와 확인한다

---

## 전체 상위 Phase 구조

## Phase 1. Internal Data Collection Console

### 목적
- 내부 운영용 데이터 수집 웹앱 구축
- 수집 작업을 버튼 기반으로 실행 가능하게 만들기

### 핵심 내용
- Streamlit 기반 운영 UI
- OHLCV / fundamentals / factors / asset profile / financial statements 수집
- 실행 결과, 로그, 실패 확인
- 기본적인 운영 UX 확보

### 상태
- `completed`

### 주요 문서
- `.note/finance/phase1/INTERNAL_WEB_APP_DEVELOPMENT_GUIDE.md`
- `.note/finance/phase1/PHASE1_WEB_APP_SCOPE.md`
- `.note/finance/phase1/PHASE1_JOB_WRAPPER_INTERFACE.md`

---

## Phase 2. Operational Hardening And Backtest Preparation

### 목적
- 수집 운영을 안정화
- 백테스트 진입을 위한 데이터/loader/point-in-time 기반 정리

### 핵심 내용
- 운영 파이프라인 분리
- 실행 이력 고도화
- 설정 외부화 준비
- backtest loader 설계
- point-in-time 보강
- 상세 재무제표 raw ledger 정리

### 상태
- `completed`

### 현재 하위 챕터
- 일반 운영 고도화 챕터
- point-in-time hardening 챕터
- 종료 요약 문서

### 주요 문서
- `.note/finance/phase2/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`
- `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`
- `.note/finance/phase2/PHASE2_COMPLETION_SUMMARY.md`
- `.note/finance/phase2/BACKTEST_LOADER_FUNCTION_DRAFT.md`
- `.note/finance/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`
- `.note/finance/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md`

---

## Phase 3. Backtest Loader Implementation And Strategy Runtime

### 목적
- 설계된 loader를 실제 코드로 구현
- 전략 실행 엔진과 DB loader를 연결

### 예상 핵심 내용
- price / fundamentals / factors / detailed statements loader 구현
- strict PIT loader와 broad research loader 구분
- universe resolution 표준화
- strategy input contract 정리
- 최소 1개 전략의 DB 기반 실행 경로 확보

### 상태
- `in_progress`

### 시작 전 확인 필요
- strict PIT loader 범위
- broad vs strict loader naming 규칙
- research-universe backfill 범위

### 주요 문서
- `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`
- `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`

---

## Phase 4. Portfolio Construction And Backtest UI

### 목적
- 사용자가 웹 UI에서 포트폴리오와 전략을 구성하고 백테스트를 실행할 수 있게 만들기

### 예상 핵심 내용
- 전략 선택 UI
- 포트폴리오 구성 UI
- 기간 / 유니버스 / 리밸런싱 규칙 입력
- 백테스트 실행 버튼
- 결과 차트 및 요약 지표 표시

### 상태
- `planned`

### 중요 전제
- loader 계층과 strategy runtime이 먼저 안정화되어야 함

---

## Phase 5. Strategy Library And Comparative Research

### 목적
- 다양한 전략을 축적하고 비교 가능한 연구 환경 구축

### 예상 핵심 내용
- 전략 템플릿
- factor / momentum / allocation / custom strategy 라이브러리
- 전략 간 비교 리포트
- 전략별 결과 저장 및 재실행

### 상태
- `planned`

---

## Phase 6. Automation, Maintenance, And Research Expansion

### 목적
- 운영 자동화 및 유지보수성 강화

### 예상 핵심 내용
- 스케줄 실행
- backfill 자동화
- 데이터 품질 점검
- 문서/인덱스 유지
- 향후 확장용 운영 규칙 정리

### 상태
- `planned`

---

## 현재 위치

현재 프로젝트는:
- `Phase 1` 완료
- `Phase 2` 완료
- `Phase 3` 진행 중

현재 바로 이어지는 핵심 포인트:
- Phase 3 첫 챕터 범위 확정
- loader 구현 시작 준비

즉 지금은
“운영용 수집 앱과 Phase 2 준비 작업이 끝난 상태에서,
실제 DB loader와 전략 실행 경로를 구현하기 시작하는 단계”
라고 보는 것이 가장 정확하다.

---

## 앞으로의 운영 방식

앞으로는 새 작업을 시작할 때 아래 순서를 기본으로 한다.

1. 이 작업이 어느 Phase에 속하는지 먼저 결정
2. 그 Phase 문서 또는 챕터 TODO 보드에서 현재 위치 확인
3. 필요하면 문서 업데이트 후 작업 시작
4. 작업 중 변경사항이 생기면
   - 해당 Phase 문서
   - TODO 보드
   - WORK_PROGRESS
   - QUESTION_AND_ANALYSIS_LOG
   를 함께 갱신
5. 새로운 큰 묶음으로 넘어갈 때는 사용자와 Phase 개설 여부를 먼저 확인
