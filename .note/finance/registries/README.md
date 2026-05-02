# Finance Registries

이 폴더는 앱과 운영 helper가 다시 읽어야 하는 append-only JSONL 저장소를 둔다.

## 포함 파일

- `CURRENT_CANDIDATE_REGISTRY.jsonl`: Candidate Review를 통과해 현재 후보로 남긴 row
- `CANDIDATE_REVIEW_NOTES.jsonl`: 후보 초안에 대한 operator review note
- `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`: pre-live / paper tracking / watchlist 운영 상태 기록
- `PORTFOLIO_PROPOSAL_REGISTRY.jsonl`: 여러 후보를 묶은 portfolio proposal draft
- `EXPERIMENT_REGISTRY.jsonl`: 필요 시 실험 후보를 넓게 저장하는 확장 registry

## 사용 기준

registry 파일은 단순 실행 로그가 아니라 다음 UI 단계가 읽는 운영 데이터다. 새 row를 추가할 때는 기존 row를 덮어쓰지 않고 append-only로 남긴다.
