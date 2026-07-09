# Plan

## 이걸 하는 이유?

Final Review의 `Step 1 / Candidate Board`가 상단 `후보 현황과 다음 판단`과 같은 후보 수 / 선택 가능 / 보류 / 차단 의미를 반복해, 사용자가 실제로 해야 하는 일인 후보 선택과 투자 검토서 확인으로 바로 이어지기 어렵다.

## Scope

- `Step 1 / Candidate Board` 독립 섹션 제거
- 중복 lane cards 제거
- `Review Queue`, `검토 대상`, 후보 비교 상세를 Decision Desk 아래 후보 선택 패널로 이동
- 아래 섹션 eyebrow를 번호가 아니라 역할 기반 이름으로 정리
- Python service / gate / 저장 / provider fetch / registry write 경계 유지

## Completion Criteria

- Final Review first-read에서 `Step 1 / Candidate Board`가 보이지 않는다.
- 후보 선택에 필요한 `Review Queue`, `검토 대상`, 후보 비교 상세는 유지된다.
- `Final Review 투자 검토서`, `Decision Cockpit`, `Final Decision Action`, `Evidence Appendix`, saved decision review 흐름은 그대로 이어진다.
- focused source contract, compile, diff check, Browser QA를 통과한다.
