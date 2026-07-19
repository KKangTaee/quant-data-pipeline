# Risks

## Active Risks

- Streamlit context surface는 fragment 밖, decision surface는 fragment 안에 있으므로 profile answer와 recheck mode의 rerun scope를 혼동하면 stale read model이 남을 수 있다. intent별 테스트와 actual Browser interaction으로 닫는다.
- 기존 사용자 local registry/run history/saved JSONL과 다수 QA artifact가 dirty 상태다. 이번 commit에는 포함하지 않는다.
- React build asset hash가 바뀐다. source와 build asset을 같은 commit에 포함하고 actual component load를 확인한다.

## Out Of Scope

- validation threshold 계산 방식 변경
- provider 수집/DB schema 변경
- Final Review/Monitoring route 변경
- registry/saved JSONL migration
