# Overview Market Context Events Data Trust V1 Design

## User Flow

1. 사용자는 Market Context에서 시장 브리프를 읽다가 "확인해야 할 변수"로 최근 주요 발표와 다음 주요 이벤트만 짧게 본다.
2. 이벤트 세부 일정과 source 상태가 필요하면 Events 탭으로 이동한다.
3. 자료 누락/오래됨이 의심되면 Market Context의 작은 자료 주의점만 보고, 상세 수집 상태는 Data Health 탭에서 확인한다.

## Read Model Direction

- `build_market_events_snapshot()`은 event type이 비어 있을 때 CPI/PPI/Employment/GDP/FOMC를 주요 macro event로 우선 취급한다.
- 이벤트 window는 recent 7일 + upcoming 14일을 기본 scan 후보로 보고, UI가 필요한 경우 더 긴 horizon을 명시할 수 있다.
- 반환 row에는 최근/다가오는 구분을 표현할 수 있는 compact field를 추가하되 DB schema는 바꾸지 않는다.
- `build_overview_macro_week_lane()`은 기존 "향후 14일"만 보는 lane에서 "방금 지난 주요 이벤트"와 "다가오는 주요 이벤트"를 분리한 context lane으로 바꾼다.
- Market Context cockpit의 interpretation cue는 Events snapshot을 사용해 "최근 CPI 발표 확인 필요", "다음 FOMC N일 후" 같은 action copy를 만든다.

## Parser Direction

- BLS HTML release schedule parser는 CPI/PPI/Employment label matching을 fixture로 검증한다.
- BLS `.ics` fallback parser는 downloaded calendar text에서 CPI/PPI/Employment를 같은 row contract로 만든다.
- 실제 network collection은 환경에 따라 실패할 수 있으므로 parser-level unit test를 우선 보강하고, 실제 실행 불가 시 `RISKS.md`에 남긴다.

## UI Direction

- Market Context: event cue는 compact row로 남기고 full event table은 Events 탭이 소유한다.
- Data Health: Market Context source-state disclosure에는 사용자 판단에 필요한 자료 주의점만 남긴다. job result, saved rows, failed count, raw status table은 Market Context 첫 화면에 새로 올리지 않는다.
- Events tab: macro week lane은 recent/upcoming section을 보여주고, CPI/FOMC 같은 macro cluster가 earnings에 묻히지 않게 한다.

## Boundary

기존 `Ingestion -> DB -> Loader/Service -> UI` 흐름을 유지한다.
이번 작업은 read model/parser/UI 표현 보강이며 새 provider, schema, registry/saved write, validation gate, monitoring signal, trading action을 만들지 않는다.
