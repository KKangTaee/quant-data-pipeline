# Backtest Analysis Commercial UX Research Plan

Status: Active
Last Updated: 2026-06-29 KST

## Why This Work Exists

사용자는 Backtest 영역이 에이전트 / 세션 주도 개발 과정에서 기능과 가이드가 과도하게 붙고, 실제 사용 흐름은 복잡해졌다고 판단했다.
이번 research는 `Backtest > Backtest Analysis`를 먼저 해부한 뒤, 불필요한 안내 / 참고 패널 / 과잉 검증을 줄이고 상용 제품형 workflow로 다시 설계하기 위한 개발 가이드라인을 만든다.

핵심 해석:

- 개선은 가이드를 추가하는 일이 아니다.
- Backtest Analysis는 후보 source를 만드는 화면이다.
- 기본 흐름은 `Backtest Analysis -> Practical Validation -> Final Review`를 유지한다.
- Reference help, 사용 안내, 전략 개발 참고 패널은 기본 작업을 방해하면 제거 / 이동 후보로 본다.
- Latest Backtest Run의 검증은 필요하지만, 다음 단계 이동을 과하게 막거나 같은 설명을 반복하면 재설계 대상이다.

## Research Questions

| Question | Decision Supported |
|---|---|
| 현재 Backtest Analysis에는 어떤 기능이 있고 어떤 파일이 소유하는가? | 제거 / 유지 / 이동 범위 결정 |
| 각 전략은 실제로 어떤 방식으로 실행되는가? | 전략별 maturity와 UI label 재정렬 |
| Latest Backtest Run의 readiness / Data Trust / handoff 판단은 과한가? | hard blocker와 review signal 분리 |
| 외부 백테스트 / 증권 분석 제품은 어떤 UI 흐름을 쓰는가? | compact commercial UX pattern 추출 |
| 1차 구현은 무엇부터 해야 하는가? | 새 구현 세션 요청문 작성 |

## Scope

Include:

- Backtest page top guidance / workflow header
- Backtest Analysis default screen
- Single Strategy / Portfolio Mix Builder entry shape
- Reference help and strategy development reference panels
- Latest Backtest Run summary, Data Trust, Candidate Readiness, Practical Validation handoff
- current strategy family / runtime ownership map
- external benchmark pattern synthesis
- staged development guideline

Exclude:

- direct code implementation in this session
- registry / saved JSONL rewrite
- run_history / generated artifact cleanup
- Practical Validation / Final Review / Monitoring behavior change without separate approval
- live approval, broker order, account sync, auto rebalance
- copying Overview Market Context / Futures Macro design literally

## Session Roadmap

| 차수 | 목적 | 산출물 | 하지 않을 일 |
|---|---|---|---|
| 1차 | 현재 Backtest Analysis audit | `CURRENT_PROJECT_AUDIT.md` | 코드 변경 |
| 2차 | 외부 benchmark와 UI pattern 추출 | `BENCHMARKS.md`, `UI_PATTERNS.md`, `SOURCES.md` | 기능 복사 / live trading 제안 |
| 3차 | feature 후보와 우선순위 정리 | `FEATURE_CANDIDATES.md` | roadmap 확정 |
| 4차 | 단계별 개발 가이드와 다음 구현 세션 handoff | `RECOMMENDATION.md`, `DEVELOPMENT_GUIDELINES.md` | 구현 완료처럼 말하기 |
