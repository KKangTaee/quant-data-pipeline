# Portfolio Monitoring React Command Center V1 Roadmap

Status: Design Approved / Detailed Implementation Plan Pending Written Spec Review
Last Updated: 2026-07-19

## 이걸 하는 이유?

Portfolio Monitoring을 Streamlit 진단 패널에서 실제 그룹 구성·성과 추적·근거형 위험 판단이
가능한 React product surface로 전환한다. 구현은 하나의 거대한 변경으로 묶지 않고 계약,
service, React, diagnosis, macro, calibration의 여섯 차수로 분리한다.

## Approved Roadmap

1. Contract And Storage Foundation
2. Monitoring Service Foundation
3. React Portfolio Command Center
4. Strength And Weakness Diagnosis
5. Macro Risk Observation
6. Calibration And Operational History

## Current Gate

- 승인된 written design을 사용자가 검토한다.
- 사용자 승인 뒤 `superpowers:writing-plans`로 파일·테스트·커밋 단위의 상세 구현 계획을 작성한다.
- 상세 구현 계획 승인 전에는 production code, DB schema, saved/registry data를 변경하지 않는다.

## Stop Condition

6차 publication/operational closeout과 Browser QA, durable docs sync까지 완료해야 전체 개편을
완료로 본다. 사용자가 특정 차수에서 중단을 명시하면 해당 차수까지만 닫고 남은 차수를
STATUS/RISKS에 남긴다.
