# Finance Roadmap

Status: Active
Last Verified: 2026-05-19

## Current Work

| Track | Status | Notes |
|---|---|---|
| UI Engine Boundary Foundation | Active | `.aiworkspace/note/finance/phases/active/ui-engine-boundary-foundation/`; audit과 Single Backtest service extraction 완료. Compare service boundary는 manual compare execution service slice 진행 중 |
| Documentation System Rebuild | Practical closeout | `.aiworkspace/note/finance/tasks/active/doc-system-rebuild/`; legacy root / operations / research / support / phase history 제거 완료 |
| AI Workspace Migration | Practical closeout | `.aiworkspace/note/finance/tasks/active/ai-workspace-migration/`; `.aiworkspace/note/finance`와 `.aiworkspace/plugins` canonical 이동 및 검증 완료 |
| Skill System Rebuild | Complete | `.aiworkspace/note/finance/tasks/active/skill-system-rebuild/`; 4 workflow + 4 domain skill taxonomy, repo-local source, global mirror, plugin manifest, marketplace path 검증 완료 |
| Product Research Skill Stage 1 | Complete | `.aiworkspace/note/finance/tasks/active/product-research-skill-stage1/`; project audit / benchmark research / feature opportunity 스킬 초안과 global mirror 검증 완료 |
| Product Research Output Contract | Complete | `.aiworkspace/note/finance/tasks/active/product-research-output-contract/`; 실제 리서치 산출물 위치를 `.aiworkspace/note/finance/researches/active/`로 확정 |
| Product Research Plugin Stage 5 | Complete | `.aiworkspace/note/finance/tasks/active/product-research-plugin-stage5/`; product research orchestration skill과 bundle bootstrap/check helper를 1차로 plugin workflow에 고정 |
| Product Research Plugin Split | Complete | `.aiworkspace/note/finance/tasks/active/product-research-plugin-split/`; product research skill과 helper를 별도 `quant-finance-product-research` plugin으로 분리 완료 |
| Backtest Report Migration | Complete | `.aiworkspace/note/finance/reports/backtests/`, legacy phase archive 제거 완료 |
| Practical Validation V2 | Active | `.aiworkspace/note/finance/tasks/active/practical-validation-v2/` |
| Phase 36 Selected Portfolio Dashboard | Implementation complete before doc rebuild | 기존 phase 문서는 새 구조 정리 후 필요 시 `phases/done/`에 요약만 남긴다 |

## Practical Validation V2 Roadmap

| Step | Goal | Status |
|---|---|---|
| P0 | 최신 runtime 재검증 보강 | Completed before this doc rebuild |
| P1 | Practical Validation V2 기본 진단 구조 | Completed before this doc rebuild |
| P2 | proxy / NOT_RUN 중심 진단을 provider / macro / stress evidence로 정상화 | In practical closeout |
| P3 | QA, Final Review handoff, selected monitoring 연결 정리 | Planned |

## P2 Scope Reminder

P2의 핵심은 provider connector 자체가 아니라,
12개 Practical Validation 진단 중 미완성 진단을 정상 검증 가능한 상태로 만드는 것이다.

P2에서 정상화하는 주요 진단:

| No | Diagnostic |
|---:|---|
| 2 | Asset Allocation Fit |
| 3 | Concentration / Overlap / Exposure |
| 5 | Regime / Macro Suitability |
| 6 | Sentiment / Risk-On-Off Overlay |
| 7 | Stress / Scenario Diagnostics |
| 9 | Leveraged / Inverse ETF Suitability |
| 10 | Operability / Cost / Liquidity |
| 11 | Robustness / Sensitivity / Overfit |

## Phase / Task Model

앞으로 큰 작업은 두 층으로 관리한다.

| Layer | Location | Meaning |
|---|---|---|
| Phase | `.aiworkspace/note/finance/phases/active/<phase>/` | 여러 task를 묶는 상위 방향, 설계, 통합 단위 |
| Task | `.aiworkspace/note/finance/tasks/active/<task>/` | 실제 구현, 문서 정리, 조사, QA를 수행하는 실행 단위 |

현재 Practical Validation V2는 phase가 아니라 별도 active task로 관리한다.

## Product Research Model

제품 방향 리서치는 실행 task와 분리해 관리한다.

| Layer | Location | Meaning |
|---|---|---|
| Research | `.aiworkspace/note/finance/researches/active/<research-id>/` | 현재 제품 분석, 외부 벤치마킹, 기능 후보, 추천안 산출물 |
| Task | `.aiworkspace/note/finance/tasks/active/<task>/` | 리서치 workflow / skill 자체를 만들거나 수정하는 실행 작업 |
| Docs | `.aiworkspace/note/finance/docs/` | 사용자 승인 후 장기 방향으로 승격된 지식 |

반복 product research run은 `quant-finance-product-research` plugin의 `finance-product-research-workflow`가 전체 순서를 조정한다.
새 research bundle은 `.aiworkspace/plugins/quant-finance-product-research/scripts/bootstrap_product_research_bundle.py`로 만들 수 있고, 산출물 구조는 `check_product_research_bundle.py`로 검증한다.

## Next Decisions

- UI Engine Boundary Foundation은 `compare-service-boundary`에서 다음 slice로 strategy runner catalog를 `app/services` 쪽으로 옮길지 결정한다. 단, `backtest_common.py`의 Streamlit-adjacent preset 의존성을 먼저 피해야 한다.
- Practical Validation V2는 P2 QA 여부를 확인한 뒤 P3로 넘어갈지, P2를 closeout할지 결정한다.
