# Overview Market Movers React Pilot Plan

## 이걸 하는 이유?

Market Movers 상단 UI는 HTML/CSS로는 잘 보이지만, 실제 실행 버튼은 Streamlit widget으로 따로 렌더링되어 시각적/상호작용 mismatch가 생긴다. 전체 앱을 Next.js로 옮기지 않고, Overview > Market Movers 안에 작은 React custom component island를 도입해 카드, 상태 badge, 버튼, action strip을 같은 디자인 언어 안에서 처리한다.

## 0~5차 범위

0. Contract freeze: React로 넘길 payload와 Python으로 받을 action event contract를 고정한다.
1. Component scaffold: Market Movers 전용 Streamlit custom component wrapper와 frontend scaffold를 추가하고 fallback을 유지한다.
2. Display-only pilot: unified summary를 React component로 렌더링하되 action dispatch는 아직 연결하지 않는다.
3. Action bridge: React event를 Python action plan / existing Overview job wrapper로 연결한다.
4. Summary + refresh action strip integration: 기존 summary와 따로 있던 refresh bar를 React panel로 통합한다.
5. Controls migration decision/application: Coverage / Period / Sector / Top N / ranking controls 중 안전한 범위를 React payload/event로 옮기고 다른 Overview 탭 확장 기준을 정리한다.

## Boundaries

- React는 UI shell / action intent만 담당한다.
- DB read, provider collection, run history, session state dispatch는 기존 Python/Streamlit 경계를 유지한다.
- UI render 중 직접 provider fetch를 만들지 않는다.
- registry / saved JSONL / run history / screenshots는 명시 요청 없이는 stage하지 않는다.

## Completion Criteria

- 각 차수는 RED test, implementation, focused verification, Browser QA 가능 범위, coherent commit을 거친다.
- React component가 없거나 실패하면 기존 Streamlit/HTML path로 fallback한다.
- Market Movers가 성공한 뒤에만 다른 Overview 탭으로 확장한다.
