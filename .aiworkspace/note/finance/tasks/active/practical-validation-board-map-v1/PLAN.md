# Practical Validation Board Map V1

Status: Active
Started: 2026-05-30

## 이걸 하는 이유?

Practical Validation 화면에는 `Final Review Gate`, `Input Evidence`, 각종 audit board, Provider board, Robustness Lab이 함께 노출된다.
사용자는 이 화면 블록들이 필수 검증 모듈인지, 조건부 근거 보드인지, 후속 참고인지 빠르게 구분하기 어렵다.

이번 작업은 검증 모듈과 화면 근거 보드를 분리해 표시하고, 현재 후보 특성에 따라 어떤 보드가 적용되는지 명확하게 보여준다.

## Scope

- Practical Validation module planner에 module type, applicability, evidence board mapping 추가
- Streamlit-free board registry 추가
- Practical Validation UI에 Applied Validation Map과 보드별 compact badge 추가
- 단일 component 후보에 적용되지 않는 Risk Contribution / Component Role board는 접힘 상태로 표시
- service contract test와 durable docs 동기화

## Out Of Scope

- 새 검증 수식 추가
- Final Review decision policy 변경
- provider / macro 데이터 수집 로직 변경
- registry JSONL 재작성
