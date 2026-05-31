# Decision Dossier Report V1 Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

Final Review는 검증 근거를 기반으로 최종 판단을 남기고, Selected Portfolio Dashboard는 선정 이후 상태를 읽는다.
하지만 사용자가 나중에 "왜 이 후보가 선정 / 보류 / 거절 / 재검토됐는지"를 다시 보려면 packet, gate, component, operator note, monitoring signal을 여러 화면에서 따로 찾아야 한다.

이번 작업은 새 JSONL 저장이나 사용자 메모 기능을 추가하지 않고, 이미 저장된 Final Review row와 선택적으로 현재 Selected Dashboard session signal을 사람이 읽는 dossier / markdown export contract로 묶는 것이다.

## Scope

- Final decision row를 입력으로 받는 Streamlit-free dossier read model 추가.
- Dossier는 summary, components, evidence checks, gate policy, operator decision, optional monitoring timeline, execution boundary를 포함한다.
- Final Review saved record와 Selected Portfolio Dashboard에서 같은 dossier markdown을 표시 / 다운로드한다.
- 새 registry, 자동 report file write, 사용자 memo 저장은 추가하지 않는다.
- Service contract test를 추가한다.

## Non-Goals

- `.aiworkspace/note/finance/reports/backtests/` 자동 파일 생성
- PDF / docx 생성
- broker order, live approval, auto rebalance
- monitoring log 자동 저장
- raw provider / holdings / macro series export

## Verification Plan

- relevant Python compile
- `tests/test_service_contracts.py`
- UI-engine boundary check
- `git diff --check`
- Browser smoke for Final Review / Selected Portfolio Dashboard visible load
