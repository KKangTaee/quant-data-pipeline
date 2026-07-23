# Risks

- 실제 append-only registry를 사용하는 QA는 중복 row를 만들 수 있어 in-memory handler로 대체한다.
- Level1 fragment 전체를 제거하거나 stage session key를 직접 쓰는 확대 수정은 하지 않는다.
- actual registry append까지 수행하는 QA는 의도적으로 생략했다. 저장 payload 변환과 handler 계약은 기존 테스트가 담당하고, Browser QA는 in-memory handler로 중복 저장 없이 event lifecycle을 검증했다.
- `server.runOnSave=false` 또는 file watcher 비활성 서버는 코드 변경을 자동 반영하지 않으므로 사용 중인 Streamlit process를 재시작해야 한다.
