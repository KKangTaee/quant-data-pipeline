# Risks

- collection 성공을 replay 성공으로 오인하면 stale validation을 다시 저장할 수 있다.
- source별 latest filtering을 eligibility filtering 뒤에 적용하면 최신 blocked row 대신 과거 eligible row가 다시 나타날 수 있다.
- 자동 confirmed key는 명시적 save-and-move action에서만 설정해야 하며 단순 selector 변경에는 적용하면 안 된다.
- registry / saved JSONL audit history는 삭제하거나 재작성하지 않는다.

