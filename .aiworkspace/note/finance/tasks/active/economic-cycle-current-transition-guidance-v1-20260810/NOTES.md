# Notes

- 실제 payload: observed `contraction`, anchor `recovery`, target `expansion`, non-adjacent true.
- route map은 `contraction → recovery`지만 transition panel은 `recovery → expansion`을 보여주는 presentation mismatch가 원인이다.
- persisted state machine은 보존하고 Overview service에서 사용자용 current transition을 파생한다.
