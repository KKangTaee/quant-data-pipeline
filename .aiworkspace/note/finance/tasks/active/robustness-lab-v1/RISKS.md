# Robustness Lab V1 Risks

Status: Active
Created: 2026-05-28

## Risks

- Board가 기존 stress / sensitivity table과 중복 표시되면 Final Review가 더 복잡해질 수 있다.
- `NOT_RUN`과 follow-up을 PASS처럼 보이게 하면 selected-route gate 의미가 약해질 수 있다.
- Raw run history나 full stress artifact를 저장하면 storage governance 원칙과 충돌한다.

## Mitigation

- Board를 compact summary + detail tabs로 제한한다.
- Status mapping에서 REVIEW / NOT_RUN을 명확히 유지한다.
- 새 JSONL registry나 사용자 memo 저장을 추가하지 않는다.

## Closeout Notes

- Strategy-specific runtime perturbation은 아직 후속 구현이다. Board는 follow-up row로 표시하고 PASS처럼 숨기지 않는다.
- Browser smoke 전에는 Streamlit 화면에서 board가 실제로 표시되는지만 확인하면 된다. 새 저장 action은 추가하지 않았다.
