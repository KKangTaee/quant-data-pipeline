# Finance Roadmap

Status: Active
Last Verified: 2026-05-29

## Current Work

| Track | Status | Notes |
|---|---|---|
| Phase 10 Walk-forward / OOS / Regime Validation | Active | `.aiworkspace/note/finance/phases/active/phase10-walkforward-oos-regime-validation/`; next task is `walkforward-oos-source-map-v1` |
| Phase 10 Board Open | Implementation complete | `.aiworkspace/note/finance/tasks/active/phase10-board-open/`; Phase 10 official board, task split, immediate next task, storage boundary 정리 |
| Phase 9 Cost / Slippage / Liquidity Realism | Complete | Closeout summary: `.aiworkspace/note/finance/phases/done/phase9-cost-slippage-liquidity-realism.md`; cost / slippage / turnover / liquidity / capacity evidence를 Backtest Realism과 selected-route 판단에 연결 |
| Backtest Realism Gate Policy Refinement V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/backtest-realism-gate-policy-refinement-v1/`; Backtest Realism row-level gaps를 Final Review selected-route gate evidence에 연결 |
| Cost Slippage Sensitivity Audit V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/cost-slippage-sensitivity-audit-v1/`; Backtest Realism Audit `cost_slippage_sensitivity_contract_v1`과 별도 sensitivity row 연결 |
| Liquidity Capacity Evidence V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/liquidity-capacity-evidence-v1/`; provider operability context의 compact capacity metrics와 Backtest Realism Audit `liquidity_capacity_contract_v1` 연결 |
| Net Cost Curve Application V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/net-cost-curve-application-v1/`; gross / net / estimated cost curve proof를 runtime metadata, source snapshot, Backtest Realism Audit row로 연결 |
| Turnover Rebalance Evidence V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/turnover-rebalance-evidence-v1/`; holdings-derived turnover estimate와 cadence-only evidence를 Backtest Realism Audit에서 분리 |
| Cost Model Source Contract Review V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/cost-model-source-contract-review-v1/`; runtime cost application proof를 compact metadata / source snapshot / Backtest Realism Audit contract로 연결 |
| Phase 9 Board Open | Implementation complete | `.aiworkspace/note/finance/tasks/active/phase9-board-open/`; Phase 9 official board, task split, immediate next task 정리 |
| Phase 8 Investability Data Evidence Expansion | Complete | Closeout summary: `.aiworkspace/note/finance/phases/done/phase8-investability-data-evidence-expansion.md`; lifecycle / survivorship / historical membership evidence를 DB-backed로 강화 |
| Lifecycle Audit Scoring V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/lifecycle-audit-scoring-v1/`; Data Coverage Audit lifecycle evidence를 current snapshot / SEC identity / computed partial / actual coverage / delisting actual로 분리해 metrics와 row evidence에 표시 |
| Computed Snapshot Lifecycle V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/computed-snapshot-lifecycle-v1/`; existing current snapshot lifecycle rows를 repeated observation window로 요약하되 partial evidence로 저장하고, Data Coverage Audit은 actual coverage row만 survivorship PASS 후보로 보도록 보수화 |
| SEC CIK Exchange Crosscheck V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/sec-cik-exchange-crosscheck-v1/`; SEC `company_tickers_exchange.json` current CIK / ticker / exchange association을 lifecycle `listing_observed` partial evidence로 적재하는 DB collector / job wrapper 추가 |
| Symbol Directory Snapshot Ingestion V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/symbol-directory-snapshot-ingestion-v1/`; Nasdaq public Symbol Directory current files를 `nyse_symbol_lifecycle` `listing_observed` partial evidence로 적재하는 DB collector / job wrapper 추가 |
| Historical Membership Source Review V1 | Complete | `.aiworkspace/note/finance/tasks/active/historical-membership-source-review-v1/`; Nasdaq Daily List는 강하지만 구독 / 승인형이라 parking lot으로 두고, 다음 구현은 Nasdaq public Symbol Directory current snapshot ingestion으로 결정 |
| Symbol Lifecycle Event Fields V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/symbol-lifecycle-event-fields-v1/`; `nyse_symbol_lifecycle`에 event semantics를 추가하고 current listing row는 `listing_observed`, SEC Form 25 row는 `delisting` event로 저장 |
| SEC Form 25 Ingestion UI V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/sec-form25-ingestion-ui-v1/`; `Workspace > Ingestion`에서 SEC Form 25 delisting evidence collector를 수동 실행하는 UI 연결 추가 |
| SEC Form 25 Delisting Backfill V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/sec-form25-delisting-backfill-v1/`; SEC EDGAR Form 25 filing metadata를 `nyse_symbol_lifecycle` delisting_feed evidence로 적재하는 collector / ingestion job wrapper 추가 |
| Historical Universe Survivorship V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/historical-universe-survivorship-v1/`; `nyse_symbol_lifecycle` schema / loader / Data Coverage Audit 연결을 추가해 historical lifecycle row가 requested period를 덮을 때만 survivorship PASS 처리 |
| Integrated Investability Gate QA V1 | Complete | `.aiworkspace/note/finance/tasks/active/integrated-investability-gate-qa-v1/`; 세 audit과 기존 provider / robustness / paper / final evidence gate의 ready / review / blocker 조합을 service contract로 고정 |
| Data Coverage Gate Policy Link V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/data-coverage-gate-policy-link-v1/`; Data Coverage Audit route를 profile-aware gate policy에 연결해 `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker, `REVIEW`는 review-required로 처리 |
| Data Coverage Hardening V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/data-coverage-hardening-v1/`; DB price window summary, provider freshness, PIT replay / period coverage, universe listing, survivorship evidence를 read-only Data Coverage Audit으로 표시 |
| Backtest Realism Gate Policy Link V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/backtest-realism-gate-policy-link-v1/`; Backtest Realism Audit route를 profile-aware gate policy에 연결해 `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker, `REVIEW`는 review-required로 처리 |
| Backtest Realism Hardening V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/backtest-realism-hardening-v1/`; Practical Validation / Final Review가 기존 result metadata와 compact evidence를 읽어 비용, turnover, liquidity, net performance policy, rebalance timing, tax/account scope, execution boundary를 read-only audit으로 표시 |
| Validation Efficacy Gate Policy Link V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/validation-efficacy-gate-policy-link-v1/`; Validation Efficacy Audit route를 profile-aware gate policy에 연결해 `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker, `REVIEW`는 review-required로 처리 |
| Validation Efficacy Hardening V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/validation-efficacy-hardening-v1/`; Practical Validation / Final Review가 기존 compact evidence를 읽어 runtime replay, period coverage, benchmark parity, provider freshness, robustness, PIT / look-ahead, survivorship / universe, storage boundary gap을 read-only audit으로 표시 |
| Practical Validation V2 P3 Closeout QA | Complete | `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-closeout-qa/`; selected monitoring read models 통합 QA와 저장 경계 확인 완료 |
| Practical Validation V2 P3 Selected Provider Evidence | Implementation complete | `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-selected-provider-evidence/`; Selected Dashboard가 selected component ticker weight로 기존 DB provider / holdings / exposure context를 read-only로 읽고 `NOT_RUN` / stale / partial coverage를 표시 |
| Practical Validation V2 P3 Symbol Freshness | Implementation complete | `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-symbol-freshness/`; Selected Dashboard Performance Recheck 전 ticker / benchmark별 DB price latest date와 stale / missing 상태를 read-only로 표시 |
| Practical Validation V2 P3 Recheck Readiness | Implementation complete | `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-recheck-readiness/`; Selected Dashboard Performance Recheck 실행 전 DB latest market date / replay contract / 기간 기본값을 read-only로 확인 |
| Practical Validation V2 P3 Recheck Comparison | Implementation complete | `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-recheck-comparison/`; 최신 Performance Recheck 결과를 Final Review baseline과 read-only로 비교하고, 미실행 / 오류 / 약화 신호를 pass로 숨기지 않음 |
| Structured Waiver Policy V1 | Complete | `.aiworkspace/note/finance/tasks/active/structured-waiver-policy-v1/`, `.aiworkspace/note/finance/docs/flows/STRUCTURED_WAIVER_POLICY.md`; `BLOCK`은 waiver 불가, future waiver는 일부 `REVIEW_REQUIRED` gap에만 구조화 조건으로 제한 |
| Practical Validation V2 P3 Continuity Check | Implementation complete | `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-continuity-check/`; Final Review selected row가 Selected Dashboard monitoring에 필요한 evidence / component / trigger / timeline 경계를 갖췄는지 read-only로 표시 |
| Investability Decision Foundation | Implementation complete | `.aiworkspace/note/finance/phases/active/investability-decision-foundation/`, closeout summary `.aiworkspace/note/finance/phases/done/investability-decision-foundation.md`; validation gate, storage governance, provenance, look-through, robustness, selected monitoring, decision dossier 완료 |
| Investability Foundation Closeout | Complete | `.aiworkspace/note/finance/tasks/active/investability-decision-foundation-closeout/`; 계획된 구현 track 완료 처리, carry-forward decision을 structured waiver / Practical Validation V2 P2 closeout로 분리 |
| Decision Dossier Report V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/decision-dossier-report-v1/`; Final Review와 Selected Dashboard에서 저장된 최종 판단을 read-only markdown dossier로 표시 / 다운로드 |
| Selected Monitoring Timeline V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/selected-monitoring-timeline-v1/`; Selected Dashboard에 read-only Timeline tab을 추가해 selection / evidence gate / recheck / drift / trigger preview를 자동 저장 없이 시간순으로 표시 |
| Robustness Lab V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/robustness-lab-v1/`; stress / rolling / sensitivity / overfit evidence를 compact board로 묶어 Practical Validation과 Final Review에 표시 |
| Look-through Exposure Board V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/look-through-exposure-board-v1/`; holdings / exposure snapshot을 compact board로 요약해 Practical Validation과 Final Review에 표시 |
| Data Provenance Coverage V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/data-provenance-coverage-v1/`; provider / macro context에 compact provenance / freshness read model과 stale REVIEW policy 추가 |
| Storage Governance Audit V1 | Complete | `.aiworkspace/note/finance/tasks/active/storage-governance-audit-v1/`; JSONL write 지점 전수 감사와 `docs/data/STORAGE_GOVERNANCE.md` 기준선 추가 |
| Validation Gate Hardening V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/validation-gate-hardening-v1/`; Final Review profile-aware gate policy matrix / compact gate snapshot / selected-route policy gate 구현 |
| UI Engine Boundary Foundation | Implementation complete | `.aiworkspace/note/finance/phases/active/ui-engine-boundary-foundation/`; audit, Single Backtest, Compare / Weighted / Saved Replay, Practical Validation handoff, Final Review / Selected Dashboard evidence read model, runtime package boundary 완료 |
| UI Engine Boundary Cleanup | Complete | `.aiworkspace/note/finance/phases/active/ui-engine-boundary-cleanup/`; Task 6~9 완료, `app.services/app.runtime -> app.web` import hard fail 적용 |
| Documentation System Rebuild | Practical closeout | `.aiworkspace/note/finance/tasks/active/doc-system-rebuild/`; legacy root / operations / research / support / phase history 제거 완료 |
| AI Workspace Migration | Practical closeout | `.aiworkspace/note/finance/tasks/active/ai-workspace-migration/`; `.aiworkspace/note/finance`와 `.aiworkspace/plugins` canonical 이동 및 검증 완료 |
| Skill System Rebuild | Complete | `.aiworkspace/note/finance/tasks/active/skill-system-rebuild/`; 4 workflow + 4 domain skill taxonomy, repo-local source, global mirror, plugin manifest, marketplace path 검증 완료 |
| Product Research Skill Stage 1 | Complete | `.aiworkspace/note/finance/tasks/active/product-research-skill-stage1/`; project audit / benchmark research / feature opportunity 스킬 초안과 global mirror 검증 완료 |
| Product Research Output Contract | Complete | `.aiworkspace/note/finance/tasks/active/product-research-output-contract/`; 실제 리서치 산출물 위치를 `.aiworkspace/note/finance/researches/active/`로 확정 |
| Product Research Plugin Stage 5 | Complete | `.aiworkspace/note/finance/tasks/active/product-research-plugin-stage5/`; product research orchestration skill과 bundle bootstrap/check helper를 1차로 plugin workflow에 고정 |
| Product Research Plugin Split | Complete | `.aiworkspace/note/finance/tasks/active/product-research-plugin-split/`; product research skill과 helper를 별도 `quant-finance-product-research` plugin으로 분리 완료 |
| Investability Evidence Packet V1 | Implementation complete | `.aiworkspace/note/finance/tasks/active/investability-evidence-packet-v1/`; Final Review evidence packet / selected-route gate 1차 구현. 후속 gate policy는 `investability-decision-foundation`에서 관리 |
| Backtest Report Migration | Complete | `.aiworkspace/note/finance/reports/backtests/`, legacy phase archive 제거 완료 |
| Practical Validation V2 | P3 closeout complete | `.aiworkspace/note/finance/tasks/active/practical-validation-v2/`; P2 provider / macro / look-through / robustness evidence closeout 완료, P3 selected monitoring slice와 closeout QA 완료 |
| Phase 36 Selected Portfolio Dashboard | Implementation complete before doc rebuild | 기존 phase 문서는 새 구조 정리 후 필요 시 `phases/done/`에 요약만 남긴다 |

## Practical Validation V2 Roadmap

| Step | Goal | Status |
|---|---|---|
| P0 | 최신 runtime 재검증 보강 | Completed before this doc rebuild |
| P1 | Practical Validation V2 기본 진단 구조 | Completed before this doc rebuild |
| P2 | proxy / NOT_RUN 중심 진단을 provider / macro / stress evidence로 정상화 | Completed |
| P3 | Final Review handoff QA, selected monitoring 연결 정리 | Completed; continuity check / recheck comparison / recheck readiness / symbol freshness / selected provider evidence / closeout QA complete |

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

- UI Engine Boundary Cleanup은 완료됐다. 다음 구조 작업은 새 phase/task로 열고, 현재 경계는 boundary lint와 service contract test를 먼저 통과시키는 기준으로 유지한다.
- Practical Validation V2 P3는 selected monitoring 연결과 closeout QA를 완료했다. Validation Efficacy, Backtest Realism, Data Coverage audit 표시 / gate 연결, Integrated Investability Gate QA, Historical Universe Survivorship V1, SEC Form 25 Delisting Backfill / UI, Symbol Lifecycle Event Fields V1을 완료했다.
- Phase 9 is complete. `cost-model-source-contract-review-v1`, `turnover-rebalance-evidence-v1`, `net-cost-curve-application-v1`, `liquidity-capacity-evidence-v1`, `cost-slippage-sensitivity-audit-v1`, `backtest-realism-gate-policy-refinement-v1`, `phase9-integrated-qa-closeout`을 완료했다.
- Phase 10 is active. Next task is `walkforward-oos-source-map-v1`: current Practical Validation / Robustness Lab / replay / result metadata source map을 확인하고, walk-forward / OOS / regime split 구현 경계를 결정한다.
- Structured Waiver Policy V1은 구현 없이 정책만 확정했다. Waiver UI / persistence는 아직 별도 구현 task로 열지 않았다.
