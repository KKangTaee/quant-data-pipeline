# Design

## Reading Flow

```text
오늘의 시장 맥락
-> 시장 브리프
-> 다음 맥락 체크
-> 참고: 과거 유사 맥락
-> 근거: 자료 기준 / 출처 상태
```

## Section Roles

- `다음 맥락 체크`: 오늘 흐름을 바로 예측하지 않고, 해석을 바꿀 수 있는 다음 관찰 지점만 보여준다.
- `참고: 과거 유사 맥락`: 충분한 표본이 있으면 과거 분포를 참고로 보여주고, 자료 부족이면 muted note로 낮춘다.
- `근거: 자료 기준 / 출처 상태`: 화면이 기대는 source / freshness / caveat를 확인하는 근거 영역이다.

## Data Boundary

기존 `cards`, `source_confidence`, `historical_analog` read model을 재사용한다. 새 fetch / schema / registry write는 없다.
