# Risks

## Closed Risks

- context/decision rerun scope는 intent test와 actual Browser interaction으로 닫았다. profile answer는 replay를 보존하고 decision만 무효화하며, recheck mode는 replay/result를 함께 무효화한다.
- React source와 production build asset을 같은 변경 단위로 검증했고 actual component load와 console error 0을 확인했다.
- 기존 사용자 local registry/run history/saved JSONL과 다수 QA artifact는 이번 commit에서 제외한다.

## Out Of Scope

- validation threshold 계산 방식 변경
- provider 수집/DB schema 변경
- Final Review/Monitoring route 변경
- registry/saved JSONL migration
