# Today Home React Workbench V2 Risks

- latest two observations may not be adjacent calendar days; UI must show exact from/to dates.
- 일부 active lane의 저장 날짜가 다르면 공통 timeline 간격이 불균일할 수 있다. X축은 실제 date spacing을 사용하고 synthetic row를 만들지 않는다.
- total value와 flow-adjusted cumulative return은 서로 다른 단위다. line/axis와 tooltip 보조값을 명확히 구분해야 한다.
- 신규 component build artifact를 canonical `component_static/`에 포함하지 않으면 배포 환경에서 fallback만 보일 수 있다.
- Streamlit component height가 content/responsive 변화 뒤 갱신되지 않으면 clipping이 생길 수 있어 actual Browser QA가 필요하다.

## Closeout

- 위 five risks는 구현과 actual Browser QA로 닫았다.
- 주봉/장중 데이터는 존재하지 않으므로 화면에서 명시적으로 부정하며 합성하지 않는다.
- 배포 시 `component_static/` 누락을 막기 위해 canonical build를 Git에 포함했다.
- 생성된 QA PNG, registry, saved setup, run history는 stage하지 않았다.
