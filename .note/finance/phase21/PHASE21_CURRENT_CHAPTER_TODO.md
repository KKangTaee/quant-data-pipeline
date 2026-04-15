# Phase 21 Current Chapter TODO

## 상태
- `practical closeout / manual_validation_pending`

## 1. Research Automation

- `completed` phase bundle automation 첫 번째 작업 단위
  - `bootstrap_finance_phase_bundle.py` 추가
  - phase plan / TODO / completion / next-phase / checklist 문서 묶음을 한 번에 생성 가능

## 2. Experiment Persistence

- `completed` current candidate registry 두 번째 작업 단위
  - `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl` seed 생성
  - `manage_current_candidate_registry.py` 추가
  - `list / show / append / validate` command 제공

## 3. Workflow Integration

- `completed` hygiene script registry integration
  - candidate-facing 문서가 바뀔 때 registry도 같이 점검하도록 보강
- `completed` plugin / skill / reference 문서 sync
- `completed` registry guide 문서 생성

## 4. Validation

- `completed` `py_compile`
- `completed` `.venv` import smoke
- `completed` script smoke validation
  - phase bundle bootstrap actual run
  - current candidate registry seed / list / validate
- `pending` manual workflow validation checklist

## 5. Documentation Sync

- `completed` phase21 kickoff plan 문서 생성
- `completed` phase21 current chapter TODO 문서 생성
- `completed` first work-unit / second work-unit 문서 생성
- `completed` completion / next-phase / checklist 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` plugin review / skill reference sync
- `completed` phase20 완료 상태를 반영한 phase21 QA 문맥 정리
  - phase21 checklist는 script / registry 중심이라 phase20 UI rename의 직접 영향이 작다는 점을 명시
  - next-phase handoff는 phase20 완료 상태를 반영해 phase22 deep validation 준비 쪽으로 다시 정리
