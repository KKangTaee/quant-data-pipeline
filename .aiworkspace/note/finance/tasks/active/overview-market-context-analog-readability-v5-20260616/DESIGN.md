# Design

## Reading Flow

1. `참고: 과거 유사 맥락` 제목과 현재 상태를 유지한다.
2. 표 전에 정의 문장을 둔다.
   - 현재 리더십 섹터를 ETF proxy로 보고, proxy ETF가 SPY 대비 5D 기준 강했던 과거 구간을 찾는다는 점을 명시한다.
   - 이후 5D / 20D / 60D의 주요 자산 분포를 요약한 참고 통계라고 설명한다.
3. `먼저 읽을 결론` 문장과 핵심 수치 strip을 표보다 먼저 둔다.
   - 유사 사례 수
   - proxy ETF 20D 중간값
   - 상승 비율
   - 최악 경로
4. 표는 `핵심 자산 요약`과 `보조 자산 참고`로 나눈다.
   - 핵심: proxy ETF, SPY, QQQ
   - 보조: TLT, GLD, IWM, HYG, LQD 등 나머지 비교 자산

## Boundaries

- 기존 historical analog read model의 rows를 그대로 사용한다.
- UI는 과거 통계를 미래 움직임 보장으로 표현하지 않는다.
- 자료 부족 상태와 OHLCV repair action은 V4 흐름을 유지한다.
