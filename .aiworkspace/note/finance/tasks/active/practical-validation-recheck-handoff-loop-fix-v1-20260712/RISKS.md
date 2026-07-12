# Risks

- collection 성공을 replay 성공으로 오인하면 stale validation을 다시 저장할 수 있다.
- source별 latest filtering을 eligibility filtering 뒤에 적용하면 최신 blocked row 대신 과거 eligible row가 다시 나타날 수 있다.
- 자동 confirmed key는 명시적 save-and-move action에서만 설정해야 하며 단순 selector 변경에는 적용하면 안 된다.
- registry / saved JSONL audit history는 삭제하거나 재작성하지 않는다.
- 실제 provider 결과에 따라 replay가 blocked로 끝날 수 있다. 이 경우 진행 상태는 `새 결과 저장`이 아니라 `재검증 결과 보강`으로 남고 Final Review 이동을 허용하지 않는다.
- in-app Browser 자동화에서는 custom component navigation intent의 Streamlit rerun을 관측하지 못했다. intent consumer와 저장 방어는 contract test로 검증했지만 실제 브라우저의 end-to-end 클릭 체인은 provider 비실행 조건에서 운영 확인이 남는다.
