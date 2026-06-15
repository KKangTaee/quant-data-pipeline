# Design

## UX Direction

1. 상단 cockpit은 `오늘의 시장 맥락`이라는 이름 아래 짧은 문장으로 먼저 읽힌다.
2. tape / sector pressure / event timeline은 숫자와 시각 단서로 즉시 훑는 영역으로 유지한다.
3. reading-flow는 아래 흐름으로 분리한다.
   - 시장 브리프: 핵심 움직임, 확산/집중, futures/macro 배경.
   - 해석할 때 같이 볼 변수: 이벤트, sentiment, 자료 상태.
   - 과거 유사 맥락 참고: 표본이 충분할 때만 참고 통계.
   - 자료 기준 / 출처 상태: 접힘 가능한 근거 영역.

## Copy Contract

- headline은 가장 중요한 움직임을 한 문장으로 말한다.
- detail은 sector leadership, futures/macro 배경, 확인할 자료 또는 읽기 순서를 1~2문장으로 말한다.
- `현재 맥락:` prefix는 제거한다.

## Visual Contract

- cockpit narrative는 제목형 headline과 본문형 detail을 분리한다.
- reading-flow section은 왼쪽 tone bar와 얇은 separator를 유지하되, 내부 padding과 글자 크기를 조정해 nested card처럼 보이지 않게 한다.
- `시장 브리프`는 가장 크게, `해석 변수`와 보조 근거는 약간 낮은 밀도로 표시한다.

