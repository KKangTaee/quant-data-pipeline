# Notes

## 2026-07-12 Root Cause

- Final Review recovery handoff 수집 경로는 collection 후 `_clear_practical_validation_replay_state(...)`를 호출하지 않는다.
- 사용자가 collection 뒤 새 validation을 저장하지 않고 Level3로 이동하면 append-only registry의 기존 legacy validation을 다시 연다.
- 조사 시점에 GRS Macro Top3 MA200 source에는 2026-07-11 생성 legacy validation 1개만 저장되어 있었고 새 validation row는 없었다.

