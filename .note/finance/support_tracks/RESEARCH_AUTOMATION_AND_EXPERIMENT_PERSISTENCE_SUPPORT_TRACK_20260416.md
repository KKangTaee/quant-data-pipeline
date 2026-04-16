# Research Automation And Experiment Persistence Support Track

## 이 문서는 무엇인가
- 기존에 `Phase 21`로 다뤘던 automation / plugin / registry 작업을,
  **main finance phase가 아닌 support track**으로 다시 분류한 정리 문서다.

## 왜 support track으로 빼는가
- 이 작업은 `finance` 프로젝트의 전략 / 백테스트 / 운용 surface를 직접 넓히는 일이라기보다,
  현재 데스크탑의 Codex / plugin / script 환경을 더 잘 쓰기 위한 보조 작업에 가까웠다.
- 즉:
  - current candidate registry
  - phase bundle bootstrap
  - hygiene / plugin / skill 연결
  은 유용했지만,
  `Phase 21`이라는 main project phase로 세는 것은 과하다고 판단했다.

## 무엇을 남겨두는가
- 아래 산출물은 여전히 repo 안에서 usable한 support tooling으로 유지한다.
  - `plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py`
  - `plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py`
  - `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`
  - repo-local hygiene / plugin / skill sync

## 이 문서를 보는 방법
- 앞으로 roadmap에서 이 작업은
  **main phase sequence 밖의 support tooling track**
  으로 읽는다.
- 따라서 이 support track은:
  - main phase 번호를 차지하지 않고
  - 필요할 때 병행 관리하거나 개선할 수 있는 보조 작업으로 다룬다.

## 관련 보존 문서
- [support plan](/Users/taeho/Project/quant-data-pipeline/.note/finance/support_tracks/RESEARCH_AUTOMATION_AND_EXPERIMENT_PERSISTENCE_SUPPORT_PLAN_20260416.md)
- [first work unit](/Users/taeho/Project/quant-data-pipeline/.note/finance/support_tracks/RESEARCH_AUTOMATION_PHASE_BUNDLE_AUTOMATION_FIRST_WORK_UNIT_20260416.md)
- [second work unit](/Users/taeho/Project/quant-data-pipeline/.note/finance/support_tracks/RESEARCH_AUTOMATION_CURRENT_CANDIDATE_REGISTRY_AND_WORKFLOW_AUTOMATION_SECOND_WORK_UNIT_20260416.md)

## 한 줄 정리
- 이 automation 묶음은 버리는 것이 아니라,
  **main phase가 아니라 support track으로 재분류해서 유지하는 것**이 맞다.
