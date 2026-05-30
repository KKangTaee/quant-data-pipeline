# Notes

- 혼동 지점: 사용자 화면의 board title과 내부 validation module taxonomy가 1:1로 보이지 않는다.
- 방향: module은 검증 의미 / gate owner, board는 화면 근거 묶음으로 분리한다.
- `NOT_APPLICABLE`은 pass가 아니라 현재 후보 특성상 해당 조건부 검증을 실행하지 않는 상태로 표시한다.
- `Leveraged / Inverse Suitability`는 ETF-like 전체가 아니라 실제 leveraged / inverse ticker가 있을 때만 적용한다.
- Provider Coverage / Look-through / Provider Data Gaps는 ETF provider investability module이 적용될 때 보드로 표시한다.
- Risk Contribution / Component Role / Weight는 weighted mix 전용 조건부 보드로 유지한다.
- `latest_replay`는 별도 audit board가 아니라 `3. 최신 데이터 기준 전략 재검증` 섹션의 `전략 재검증 실행`과 `Runtime period coverage`를 의미하므로 blocker table에서 해결 위치를 명시한다.
