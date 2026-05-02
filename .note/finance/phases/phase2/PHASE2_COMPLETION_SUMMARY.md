# Phase 2 Completion Summary

## 목적
이 문서는 `finance` 프로젝트의 Phase 2를 마무리하면서,
무엇이 완료되었고 무엇이 다음 Phase로 넘어가는지를 정리하는 종료 요약 문서다.

Phase 2의 정식 이름:
- `Operational Hardening And Backtest Preparation`

---

## Phase 2의 목표

Phase 2의 핵심 목표는 다음 두 가지였다.

1. 데이터 수집 운영을 안정화
2. DB 기반 백테스트 진입을 위한 준비를 끝낸다

즉,
- 내부 운영용 수집 웹앱을 실제 운영 도구 수준으로 끌어올리고
- 이후 loader / strategy runtime / backtest UI로 넘어갈 수 있는 설계 기반을 만드는 단계였다

---

## 완료된 주요 항목

## 1. 운영 수집 콘솔 고도화

완료 내용:
- 운영 파이프라인 분리
  - `Daily Market Update`
  - `Weekly Fundamental Refresh`
  - `Extended Statement Refresh`
  - `Metadata Refresh`
- 실행 이력 고도화
  - `pipeline_type`
  - `execution_mode`
  - `symbol_source`
  - `symbol_count`
  - `input_params`
  - `execution_context`
- 운영 UX 보강
  - 대량 실행 경고
  - 실행 중 전역 잠금
  - 카드별 로딩 표시
  - OHLCV progress bar
  - 최근 실행 / 영속 실행 이력 / 로그 / 실패 CSV 확인

결과:
- 수집 앱은 단순 실행 UI를 넘어서 운영 콘솔로 볼 수 있는 수준이 되었다

---

## 2. 설정 외부화 준비 완료

완료 내용:
- 하드코딩 상수 inventory 작성
- 외부화 우선순위 분류
- 설정 파일 경로 확정
  - `config/finance_web_app.toml`
- TOML 구조 초안 작성

결과:
- 아직 실제 설정 로더 구현은 다음 Phase로 넘기더라도,
  설정 외부화를 바로 시작할 수 있는 준비는 끝난 상태다

---

## 3. Backtest Loader 설계 기반 정리

완료 내용:
- loader 함수 초안
- loader 입력 계약
- point-in-time 가이드
- strict PIT query 초안

핵심 정리:
- 전략 코드는 DB 테이블을 직접 만지지 않도록 한다
- loader 계층을 표준 진입점으로 둔다
- `symbols`, `universe_source`, `start/end`, `as_of_date`, `freq`, `timeframe` 의미를 통일했다

결과:
- Phase 3에서 loader를 실제 코드로 구현할 기준이 문서화됐다

---

## 4. 상세 재무제표 point-in-time 정리

완료 내용:
- `nyse_financial_statement_filings` 기반 filing metadata 보존
- `available_at` fallback 보수화
- accession/unit 기반 raw identity 정리
- `nyse_financial_statement_values` strict raw ledger 방향으로 재정의
- `nyse_financial_statement_labels`를 concept-centered summary table로 재정의
- 로컬 DB에서 labels / values 테이블 재생성 및 샘플 재적재 검증

결과:
- 상세 재무제표는 이제 초기 추정형 테이블보다
  point-in-time 가능성이 있는 raw ledger 구조에 더 가까워졌다

---

## Phase 2의 최종 산출물

대표 문서:
- `.note/finance/phases/phase2/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`
- `.note/finance/phases/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`
- `.note/finance/phases/phase2/BACKTEST_LOADER_FUNCTION_DRAFT.md`
- `.note/finance/phases/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`
- `.note/finance/phases/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md`
- `.note/finance/phases/phase2/STRICT_PIT_LOADER_QUERY_DRAFT.md`
- `.note/finance/phases/phase2/POINT_IN_TIME_SCHEMA_REVIEW_AND_PATCH_PLAN.md`
- `.note/finance/phases/phase2/POINT_IN_TIME_BACKFILL_AND_CONSTRAINT_STRATEGY.md`

대표 코드 산출물:
- `app/web/streamlit_app.py`
- `app/jobs/*`
- `finance/data/financial_statements.py`
- `finance/data/db/schema.py`

---

## Phase 2에서 다음 Phase로 넘기는 항목

Phase 2에서 일부러 설계/정리까지만 하고,
실제 구현은 Phase 3으로 넘긴 항목:

1. strict PIT loader 실제 코드 구현
2. broad research loader와 strict PIT loader naming 규칙 확정
3. research-universe backfill 실제 범위 결정
4. price / fundamentals / factors / statements loader 구현
5. strategy runtime과 loader 연결

즉, Phase 2는 “준비 완료”까지고,
Phase 3부터는 “실제 실행 계층 구현”으로 넘어간다.

---

## 결론

Phase 2는 완료로 본다.

이제 프로젝트는:
- 운영용 데이터 수집 콘솔을 가진 상태
- point-in-time을 고려한 상세 재무 원장 방향을 잡은 상태
- loader 설계 문서를 가진 상태

이며,
다음 Phase의 핵심은
**이 설계를 실제 DB loader와 전략 실행 코드로 바꾸는 것**이다.

