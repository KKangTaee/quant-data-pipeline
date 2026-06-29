# Overview Market Context Brief Flow Redesign V2 Design

## Product Direction

Market Context는 상태 카드 모음이 아니라 시장 브리프 화면이어야 한다.

V2의 화면 흐름은 다음 순서다.

1. `오늘의 시장 브리프`: 현재 저장 자료 기준의 headline, tape, brief rows.
2. `다음 맥락 체크`: 오늘 해석을 바꿀 수 있는 관찰 지점과 확인 위치.
3. `참고: 과거 유사 맥락`: selected as-of / pattern 기준으로만 재계산되는 context-only 통계.
4. `Macro 조건 포함 비교`: broad analog와 추가 macro/futures 조건 적용 후 표본을 나란히 비교.
5. `근거: 자료 기준 / 출처 상태`: 자료 기준과 보강 위치를 보조 근거로 확인.
6. `필요 자료 보강`: 기존 Overview action boundary를 통한 수동 보강.

## UI Rules

- 반복 카드 grid는 metric tile이나 실제 비교가 필요한 곳에만 제한한다.
- reading section은 full-width rule / row / ledger 중심으로 구성한다.
- `다음 맥락 체크`는 guide card가 아니라 observation rail이다.
- `Macro 조건 포함`은 historical analog 안의 nested card처럼 보이지 않게, broad vs conditioned comparison language를 먼저 보여준다.
- 글씨 크기는 compact diagnostic 기준이 아니라 Market Movers / Portfolio Monitoring처럼 읽기 가능한 크기를 우선한다.

## Data Boundary

- 모든 화면 렌더는 기존 DB-backed read model을 사용한다.
- 수집은 기존 `app/jobs/overview_actions.py` facade를 통해서만 실행한다.
- selected as-of는 historical analog 계산에만 적용된다.
- FRED / events / sentiment는 hard condition이 아니라 preview / annotation / deferred 상태로만 표시한다.
