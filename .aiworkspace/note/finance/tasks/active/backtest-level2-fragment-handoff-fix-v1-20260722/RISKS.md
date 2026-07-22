# Risks

- 실제 append-only registry를 사용하는 QA는 중복 row를 만들 수 있어 in-memory handler로 대체한다.
- Level1 fragment 전체를 제거하거나 stage session key를 직접 쓰는 확대 수정은 하지 않는다.
- 최종 Browser QA에서 fragment 밖 marker가 갱신되지 않으면 Streamlit event lifecycle을 다시 조사한다.
