# Backtest Direction Reset Research Plan

Status: Active
Last Updated: 2026-06-12 KST

## Why This Work Exists

이 리서치는 기존 Backtest 3A~5B 흐름을 그대로 이어가지 않고, 구현 전에 Backtest 제품 방향을 다시 정의하기 위한 reset pass다.

핵심 질문은 단순하다. `Backtest Analysis`가 evidence / governance / diagnostics panel을 계속 흡수하는 화면이어야 하는가, 아니면 전략 실행, 비교, 후보 source 생성, replay 가능성 확인에 집중하고 검증 근거는 `Practical Validation`, `Final Review`, `Operations > Portfolio Monitoring`으로 넘겨야 하는가?

이번 결론은 승인된 구현 계획이 아니다. 사용자가 다음 build scope를 승인하기 전까지 이 bundle은 제품 방향 evidence와 선택지로만 읽는다.

## Working Scope

Include:

- 현재 Backtest Analysis / strategy runtime / validation handoff / history replay / saved replay 흐름 audit
- 3A~4B panel/workbench 확장, 4C direction reset, 5A/5B runtime hardening의 유지 / 보류 / 폐기 후보 분류
- Strict Annual, Strict Quarterly Prototype, ETF 전략군, Risk-On Momentum 5D의 maturity model 재정의
- 3~5개 외부 benchmark의 workflow pattern 조사와 dated source 기록
- 1차~n차 잠정 개발 roadmap 제안

Exclude:

- 코드 구현
- 새 Backtest Analysis panel 추가
- registry / saved JSONL / run_history / generated artifact 수정
- `docs/ROADMAP.md`, phase plan, task plan 변경
- provider / FRED direct fetch
- Practical Validation / Final Review / Portfolio Monitoring 동작 변경
- quarterly prototype의 즉시 정식 승격

## Research Questions

| Question | Decision this supports |
| --- | --- |
| 현재 Backtest 제품은 무엇을 해야 하는가? | Backtest Analysis와 downstream validation / review / monitoring 화면의 책임 경계를 다시 잡는다. |
| 지금 브랜치에서 방향이 어긋난 지점은 어디인가? | 기존 3A~5B 중 살릴 것, 보류할 것, 폐기 후보를 분리한다. |
| 전략군별 성숙도 모델은 어떻게 재정의해야 하는가? | 실행 가능, replay 가능, candidate-ready, research/prototype 상태를 분리한다. |
| 외부 benchmark에서 어떤 workflow pattern을 가져올 수 있는가? | run result, diagnostics, history, saved setup, monitoring handoff 분리 방식을 비교한다. |
| 새 개발 roadmap은 어떤 순서여야 하는가? | 지금 바로 할 1차, 다음 2차~3차, 보류 항목을 사용자 승인 대상으로 제시한다. |

## Tentative Research Roadmap

| 차수 | 목적 | 산출물 | 이번 bundle에서의 상태 |
| --- | --- | --- | --- |
| 1차 | 현재 제품 흐름과 branch drift audit | `CURRENT_PROJECT_AUDIT.md` | Complete |
| 2차 | 외부 benchmark와 reusable pattern 추출 | `BENCHMARKS.md`, `UI_PATTERNS.md`, `SOURCES.md` | Complete |
| 3차 | feature opportunity와 reset roadmap 제안 | `FEATURE_CANDIDATES.md`, `RECOMMENDATION.md`, `RISKS.md` | Complete |
| 4차 | 사용자 승인 후 실제 build scope 확정 | future task / phase | Deferred |

## Method

1. Read durable docs and active-state manifests first.
2. Inspect only the Backtest files needed to verify branch state and workflow ownership.
3. Browse current official benchmark sources and record access date plus evidence labels.
4. Separate implemented facts, documented boundaries, marketing claims, and inference.
5. Produce Now / Next / Later / Parking Lot candidates without turning them into an approved roadmap.

## Outputs

| File | Role |
| --- | --- |
| `CURRENT_PROJECT_AUDIT.md` | Current product promise, workflow surface classification, branch drift diagnosis, strategy maturity model. |
| `BENCHMARKS.md` | External benchmark notes and cross-product lessons. |
| `UI_PATTERNS.md` | Product flow and UI/workflow patterns to reuse or avoid. |
| `FEATURE_CANDIDATES.md` | Now / Next / Later / Parking Lot candidates with impact / effort / risk scoring. |
| `RECOMMENDATION.md` | Tentative 1차~n차 roadmap and decision checkpoint. |
| `DEVELOPMENT_SESSION_GUIDE.md` | New-session development guide with per-stage prompts, boundaries, completion criteria, and verification guidance. |
| `SOURCES.md` | Local and web sources with access dates and evidence labels. |
| `RISKS.md` | Evidence gaps, boundary risks, and approval risks. |
