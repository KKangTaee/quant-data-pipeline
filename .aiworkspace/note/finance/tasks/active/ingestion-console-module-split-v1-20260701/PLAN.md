# Ingestion Console Module Split V1 Plan

## 이걸 하는 이유?

`Workspace > Ingestion`은 기능이 늘면서 `app/web/ingestion_console.py`와 `app/jobs/ingestion_jobs.py`에 UI orchestration과 job wrapper가 과도하게 모였다.
이번 작업은 동작을 바꾸기보다 스크립트 구조를 나눠 이후 수집 기능 검증, 중복 제거, 잘못된 수집 경로 보강을 안전하게 만들기 위한 구조 개선이다.

## 1차

- 목적: `app/web/ingestion/` 패키지와 old import compatibility facade를 만든다.
- 파일 범위: `app/web/ingestion_console.py`, `app/web/ingestion/page.py`, package `__init__`, 구조 계약 테스트.
- 완료 조건: 기존 `app.web.ingestion_console.render_ingestion_page` import가 유지되고 새 package entrypoint도 동작한다.

## 2차

- 목적: action registry, section constants, compatibility/action helper를 전용 registry 모듈로 분리한다.
- 파일 범위: `app/web/ingestion/registry.py`, page/facade imports.
- 완료 조건: active / compatibility action 분류 계약이 새 모듈과 old facade 양쪽에서 유지된다.

## 3차

- 목적: CSS, 결과 요약, 실행 기록 / 로그 preview 렌더링을 page 본문에서 분리한다.
- 파일 범위: `app/web/ingestion/styles.py`, `results.py`, `records.py`.
- 완료 조건: page entrypoint는 공통 결과/기록 영역을 전용 모듈에 위임한다.

## 4차

- 목적: running job state, progress callback, dispatch 경계를 분리한다.
- 파일 범위: `app/web/ingestion/runtime.py`, `dispatcher.py`, `progress.py`.
- 완료 조건: progress-enabled job과 diagnostic job이 기존 scheduled job 흐름을 유지한다.

## 5차

- 목적: operational/manual/records section entry를 분리하고 큰 section 함수 크기를 줄인다.
- 파일 범위: `app/web/ingestion/sections/`.
- 완료 조건: selected section dispatch가 dedicated section module을 통해 이루어진다.

## 6차

- 목적: `app/jobs/ingestion/` package facade를 추가하고 durable docs를 새 구조에 맞춘다.
- 파일 범위: `app/jobs/ingestion/`, `app/jobs/ingestion_jobs.py`, finance docs / task logs.
- 완료 조건: 기존 `app.jobs.ingestion_jobs` import는 유지되고 새 package 구조가 문서화된다.
