# README Product / Onboarding Overhaul V1 Plan

Status: Verbal Design Approved — Written Spec Awaiting Review
Created: 2026-07-25

## 이걸 하는 이유?

현재 root `README.md`는 2026-05-13 기준의 Backtest 중심 프로토타입 설명에 머물러 있다.
실제 제품은 `Research / Portfolio / Data / Help` navigation과 Today, Market Research,
Institutional Holdings, Portfolio Lab, Portfolio Monitoring, Reference Center까지 확장되었다.

새 README는 첫 방문자가 제품의 목적과 사용 흐름을 이해하고 앱을 실행한 뒤,
개발자가 구현 언어·계층·검증 경계를 따라갈 수 있는 하나의 균형형 진입점이 되어야 한다.

## Goal

root README를 “기능 목록”에서 “제품 이해 → 실제 사용 흐름 → 5분 실행 → 구현 구조 → 상세 문서”로 이어지는
Evidence-first 퀀트 투자 리서치 워크스페이스의 첫 관문으로 전면 재작성한다.

## Scope

포함한다.

- `README.md` 정보구조와 본문 전면 재작성
- 현재 `Research / Portfolio / Data / Help` navigation 및 화면 책임 반영
- 대표 Today 화면 1장과 제품 workflow Mermaid
- 5분 실행 경로와 상세 데이터 준비 runbook handoff
- Python / Streamlit / React / TypeScript / Vite / MySQL / JSONL 역할 설명
- `Ingestion -> DB -> Loader / Service -> Runtime -> UI` 구현 경계
- point-in-time correctness, 투자 해석 경계, 저장·commit 정책
- README link, 명령, Markdown, 현재 앱 화면명 검증
- 이번 task와 최소 root handoff 문서 정리

포함하지 않는다.

- 앱 코드, DB schema, 수집 workflow, 화면 동작 변경
- MySQL 연결 방식을 환경변수 기반으로 리팩터링
- registry / saved / run history JSONL 변경
- 기존 generated QA 산출물 정리 또는 삭제
- 모든 화면별 상세 매뉴얼을 README에 복제
- `financial_advisor`를 active product scope로 확장

## Four-Round Roadmap

### 1차 — 제품 서사와 사용자 흐름

- 제품 정의, 해결하려는 문제, 화면 지도, 실제 사용자 workflow를 재작성한다.
- 완료 조건: README가 현재 navigation과 사용자-facing surface를 정확히 설명한다.

### 2차 — 실행과 기술 구조

- 5분 빠른 시작, 기술 스택, 계층별 책임, 저장 경계와 검증 방법을 보강한다.
- 완료 조건: 사용자와 개발자가 각각 필요한 시작점을 README에서 찾을 수 있다.

### 3차 — 대표 화면과 문서 연결

- Today 대표 화면을 README 전용 asset으로 만들고 workflow / architecture Mermaid와 canonical link를 정리한다.
- 완료 조건: 이미지와 상대 링크가 저장소 기준으로 정상 해석된다.

### 4차 — 검증과 closeout

- 실행 명령, 앱 화면명, Markdown, link, diff를 검증하고 task / handoff 문서를 동기화한다.
- 완료 조건: 관련 검증이 통과하고 unrelated user files를 제외한 coherent commit이 생성된다.

## Done Criteria

- README의 제품 정의가 `Evidence-first 퀀트 투자 리서치 워크스페이스`로 읽힌다.
- 현재 앱의 `Research / Portfolio / Data / Help`와 7개 top-level surface가 일치한다.
- 제품 workflow가 `Research -> Portfolio Lab -> Practical Validation -> Final Review -> Portfolio Monitoring`으로 설명된다.
- Data Operations는 선형 첫 화면이 아니라 전 흐름을 받치는 DB-backed evidence layer로 표현된다.
- `uv sync`와 `uv run streamlit run app/web/streamlit_app.py`가 빠른 시작에 포함된다.
- Node.js는 앱 runtime 필수가 아니라 React 개발 / build dependency로 구분된다.
- 구현 언어와 framework뿐 아니라 각 계층의 소유 책임이 설명된다.
- active task 목록을 README에 복제하지 않고 canonical roadmap / task 문서로 연결한다.
- 대표 화면 1장, Mermaid, 상대 link, Markdown과 관련 명령이 검증된다.
- registry / saved / run history와 기존 QA artifact는 변경 또는 stage하지 않는다.

## Stop Condition

4차 검증과 문서 정렬이 끝나고 README 개편 commit이 만들어지면 종료한다.
제품 코드나 데이터 준비 방식 자체의 결함이 발견되면 README에서 현재 한계로 정확히 설명하고 별도 task로 넘긴다.
