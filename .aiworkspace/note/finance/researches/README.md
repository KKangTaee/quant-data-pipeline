# Finance Research Workspace

Status: Active
Last Verified: 2026-05-14

## Purpose

이 폴더는 `finance` 제품 방향, 벤치마킹, 기능 후보, 전략적 의사결정 근거를 조사하는 작업장이다.

`tasks/active/`가 실행 작업 기록이라면, `researches/active/`는 실제 조사 산출물의 본문을 담는다.

## Structure

```text
.aiworkspace/note/finance/researches/
  active/<research-id>/
    RESEARCH_PLAN.md
    CURRENT_PROJECT_AUDIT.md
    BENCHMARKS.md
    UI_PATTERNS.md
    FEATURE_CANDIDATES.md
    RECOMMENDATION.md
    SOURCES.md
    RISKS.md
  done/<research-id>/
```

## Active Researches

| Research | Focus |
| --- | --- |
| `active/2026-05-ui-platform-research/` | Streamlit UX/UI를 Python quant engine + API + React/Next.js product surface로 분리할지 조사 |
| `active/2026-05-backtest-report-productization/` | Backtest Result / Strategy Report를 제품화하기 위한 report artifact, UI pattern, 기능 후보 조사 |
| `active/2026-05-investable-workflow-gap-analysis/` | 현재 Backtest -> Practical Validation -> Final Review -> Selected Dashboard 흐름의 실전 투자 판단 약점과 상용 제품 대비 개선 방향 조사 |

## Rules

- 조사 중 사실, 추측, source notes, 비교표는 `researches/active/<research-id>/`에 둔다.
- 채택된 장기 방향만 `docs/PRODUCT_DIRECTION.md` 또는 `docs/ROADMAP.md`로 승격한다.
- 승인된 개발 단위만 `phases/active/` 또는 `tasks/active/`로 전환한다.
- 외부 서비스, 가격, 기능, UI는 변할 수 있으므로 `SOURCES.md`에 접근 날짜와 evidence label을 남긴다.
- registry, saved setup, run history, generated artifact를 research 정리 대상으로 섞지 않는다.
