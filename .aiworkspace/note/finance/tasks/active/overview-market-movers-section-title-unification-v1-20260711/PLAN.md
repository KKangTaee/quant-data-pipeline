# Overview Market Movers Section Title Unification V1 Plan

## 이걸 하는 이유?

Market Movers 내부의 `Ranking Board`와 `섹터 / 시장 확산 맥락`이 서로 다른 제목 계층을 사용하고, 섹터 영역은 바깥 divider와 내부 `시장 확산 지도` 제목이 중복되어 큰 섹션 경계가 고정되어 보이지 않는다. 사용자가 화면을 내려 읽을 때 섹터 영역을 하나의 명확한 업무 구간으로 바로 인식하도록 제목 구조를 정리한다.

## 범위

- `섹터 / 시장 확산 맥락`의 React 헤더를 `kicker -> 한글 섹션 제목 -> 설명 -> 상태 badge` 구조로 정리한다.
- 현재 분석 headline은 섹션 제목이 아니라 결과 요약으로 한 단계 낮춘다.
- 외부 중복 divider를 제거하고 HTML fallback도 같은 계층을 유지한다.
- 계산, payload 의미, 섹터 카드, 상세 표, Market Movers 상단, Ranking Board, 선택 종목 조사는 변경하지 않는다.

## 완료 조건

- React와 fallback 모두 `SECTOR BREADTH / 섹터 / 시장 확산 맥락 / 설명 / 상태`를 같은 순서로 렌더링한다.
- `혼재된 참여...` headline은 별도 결과 요약으로 보인다.
- 관련 테스트, React build, Browser QA가 통과한다.
