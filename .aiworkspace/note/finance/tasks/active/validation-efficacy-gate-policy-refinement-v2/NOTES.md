# Validation Efficacy Gate Policy Refinement V2 Notes

Status: Complete
Created: 2026-05-29

## Notes

- 기존 gate policy는 Validation Efficacy route 자체로 selected-route 가능 여부를 판단했지만, row-level temporal evidence가 `Evidence`에 충분히 드러나지 않았다.
- 이번 변경은 row-level detail만 기존 policy group에 합치는 방식이라 UI 저장 흐름이나 registry schema를 바꾸지 않는다.
- Backtest Realism row-level merge와 같은 helper를 재사용했다.
