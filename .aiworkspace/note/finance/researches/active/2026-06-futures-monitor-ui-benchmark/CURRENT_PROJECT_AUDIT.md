# Current Project Audit

Status: Draft
Last Updated: 2026-06-23

## Current Surface

화면: `Workspace > Overview > Futures Monitor`

현재 화면은 한글화와 중복 노출 정리는 일부 반영됐지만, 사용자가 보기에는 여전히 Streamlit 기본 입력 컴포넌트와 단순 card grid가 나열된 prototype-like 화면이다.

## Main UX Problems

1. **상단 control bar가 업무 도구처럼 보이지 않는다.**
   - 관찰 그룹, 선물 선택, 시간 범위, 차트 봉, 차트 범위, 데이터 갱신이 같은 위계로 놓여 있다.
   - `데이터 갱신` popover가 화면 위에 큰 floating panel로 떠서 본문 읽기를 막는다.

2. **Macro Context가 시장 브리프라기보다 카드와 텍스트 묶음처럼 보인다.**
   - `근거 강도`, `과거 점검`, `유사 구간`은 유용하지만, 오늘 결론과 관계가 시각적으로 강하지 않다.
   - score chip은 숫자를 보여주지만 사용자가 어떤 방향으로 해석해야 하는지 즉시 알기 어렵다.

3. **최근 1주 흐름이 시각적 흐름이 아니라 반복 카드다.**
   - 각 카드가 같은 무게로 보이며, 가장 중요한 변화 / 지지 근거 / 반대 근거가 분리되지 않는다.
   - “오늘 기준 해석과 1주 흐름이 같은지 다른지”가 보이지 않는다.

4. **차트 영역의 목적이 약하다.**
   - Live Chart는 chart grid를 보여주지만, 상단 macro brief와 어떤 관계인지 약하다.
   - chart section은 chart interaction 중심 화면이라기보다 하단 부록처럼 보인다.

5. **색상과 여백이 의미보다 장식처럼 보인다.**
   - red / teal / grey tone은 상태 의미를 주지만, 사용자가 먼저 볼 path를 강하게 안내하지 못한다.

## User Job To Be Done

사용자는 이 화면에서 다음 질문을 끝내야 한다.

1. 지금 선택한 선물 묶음은 무엇인가?
2. 데이터가 현재 판단에 충분히 최신인가?
3. 오늘 기준 선물/매크로 흐름은 어떤 상태인가?
4. 최근 1주 흐름은 오늘 해석을 지지하는가, 반대하는가?
5. 어떤 선물이 현재 해석에 가장 크게 기여했는가?
6. 더 보고 싶으면 어느 원본 / 차트 / 근거로 내려가면 되는가?

## Design Baseline For Next Iteration

- 화면 첫 1초: `현재 상태 + 갱신 필요 여부 + 가장 큰 시장 압력`을 읽는다.
- 첫 5초: `오늘 해석`, `최근 1주 흐름`, `핵심 근거 2~3개`를 읽는다.
- 이후: chart / evidence / raw data를 사용자가 선택해서 확장한다.

