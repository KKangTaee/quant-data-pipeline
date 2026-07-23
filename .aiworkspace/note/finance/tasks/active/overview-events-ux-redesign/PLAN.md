# Plan

## 이걸 하는 이유?

Events 탭은 FOMC / earnings / 미국 휴장 일정을 저장해서 보여주지만, 실제 Overview 실행 경로가 상승률 상위 종목만 실적 일정 대상으로 삼아 Alphabet 같은 중요 기업을 누락할 수 있다. 화면도 수집 상태와 전체 행 수를 먼저 보여줘 사용자가 "무슨 일정이 언제 있고 믿을 만한가"를 빠르게 판단하기 어렵다.

## 2026-07-23 Current Scope

- earnings 기본 수집 범위를 `latest_movers`에서 혼합 보장 방식으로 바꾼다.
  - 시가총액 상위 100, 보유 포트폴리오, 관심종목, 45일 이내 기존 실적 종목은 매일 확인한다.
  - S&P 500 전체는 약 100종목씩 5개 배치로 순환 탐색한다.
- 종목별 수집 성공 여부와 전체 탐색 완성도를 저장하는 coverage checkpoint를 추가한다.
- GOOG / GOOGL 같은 복수 주식 클래스를 issuer 단위의 한 일정으로 표시한다.
- FOMC와 미국 휴장 / 조기폐장 일정은 earnings 행 수와 무관하게 날짜 범위와 유형별로 조회한다.
- React 화면은 승인된 `A · 브리프 + 캘린더` 구조로 재편한다.
- provider / DB fetch는 UI에서 직접 수행하지 않고 `Ingestion -> DB -> Service -> React` 경계를 유지한다.

## Current Acceptance

- Alphabet이 일일 우선군에 포함되고, 같은 발표가 GOOG / GOOGL 두 카드로 중복 표시되지 않는다.
- provider 실패가 없는 정상 S&P 500 탐색은 5회 이내 완료된다. 실패 종목이 있으면 coverage는 `partial`을 유지하고 재시도 완료 후 `complete`가 된다.
- 일부 provider 실패가 기존 정상 일정을 삭제하지 않는다.
- 현재 / 차기 공개 연도의 FOMC와 공식 휴장 / 조기폐장 일정이 임의의 200행 제한 때문에 누락되지 않는다.
- 미국 거래일과 한국시간 표시일, 장전 / 장후 / 시간 미확인을 구분한다.
- 상단 요약, 캘린더, 선택일 상세, 밀도 그래프가 동일한 필터 결과를 사용한다.
- 첫 화면은 일정 판단을 우선하고 coverage / 수집 진단은 보조 근거로 둔다.
- focused tests, React build, desktop / mobile Browser QA, `git diff --check`가 통과한다.

## 전체 Roadmap

1. 진단: Google 누락 원인, 공식 일정 완전성, UI 약점 확인 — 완료
2. 설계: 혼합 수집 계약과 A안 React 흐름 승인·문서화 — 완료
3. 구현: coverage schema, earnings orchestrator, read model, React A안 적용 — 대기
4. 검증·정리: DB smoke, contract tests, Browser QA, durable docs, commit — 대기

## Historical Scope

2026-05-30과 2026-07-07의 초기 UX / React 전환 범위와 완료 기록은 `DESIGN.md`, `STATUS.md`, `RUNS.md`에 보존한다. 당시의 "DB schema와 collector를 바꾸지 않는다"는 제한은 이번 누락 교정 범위에는 적용하지 않는다.
