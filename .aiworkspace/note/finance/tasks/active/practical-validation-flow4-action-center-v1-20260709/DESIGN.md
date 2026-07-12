# Design

## User-Facing IA

Flow4는 세 질문에 답한다.

1. `카테고리별 검증 결과`: 무엇이 통과 / 보강 필요 / 차단인가?
2. `데이터 보강 / 수집 실행`: 이 문제 중 현재 데이터 수집으로 해결할 수 있는 것은 무엇이고, 어떤 버튼을 누르면 되는가?
3. `상세 근거 / 원자료`: 검산할 때 어떤 원자료 / raw row를 확인할 수 있는가?

기존 `데이터 보강 대상`과 `Provider 보강 액션`은 내부적으로는 read model 표시와 Python 실행 경계로 분리되어야 하지만, 사용자 화면에서는 하나의 action center로 읽혀야 한다.

## Boundary

- React board는 `data_action_board` props만 렌더링한다.
- Python page는 기존 `run_provider_gap_collection()` 버튼 실행과 session feedback을 계속 소유한다.
- Service read model은 기존 provider gap collection plan과 compact evidence row만 읽는다.
- React / Streamlit UI 모두 provider, FRED, DB를 직접 fetch하지 않는다.
- raw holdings / macro series / provider response는 DB에 있고 UI에는 compact evidence만 남는다.

## Copy Direction

`Provider`는 기술 tag로 유지하되 first-read title에서는 낮춘다.

- Main section: `데이터 보강 / 수집 실행`
- Board title: `데이터 보강 대상`
- Python button area: `수집 실행`
- Button label: `부족한 외부 데이터 일괄 수집 / 보강`
- Help copy:
  - `수집하는 것`: ETF 운용성 / 비용, holdings / exposure, source map 탐색, FRED 매크로
  - `하지 않는 것`: 백테스트 재실행, 검증 판정 변경, Final Review 판단, registry / saved rewrite
  - `실행 후 다음 단계`: Flow 2 재검증을 다시 실행해 보강 결과 반영

## Expander Policy

First-read action center에는 사용자 행동과 직접 연결되는 카드 / 설명 / 버튼만 둔다.

`보강 작업 상세 테이블`, provider gap raw row, source map parser detail은 `상세 근거 / 원자료` 아래 raw detail로 낮춘다.

## Self Review

- Placeholder: none.
- Scope: Flow4 UI / copy / evidence placement only.
- Boundary: no new ingestion path, DB schema, fetch path, gate policy, storage write.
- Ambiguity: `Provider 보강 액션`은 visible standalone title에서 제거하고, technical provider wording은 detailed copy / raw evidence에만 남긴다.
