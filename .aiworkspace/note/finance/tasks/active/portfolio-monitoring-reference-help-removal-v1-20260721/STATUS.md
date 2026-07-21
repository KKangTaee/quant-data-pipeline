# Portfolio Monitoring Reference Help Removal V1 Status

Status: Complete (`2/2차`)

- 1차: Portfolio Monitoring의 contextual renderer 호출·중복 import·전용 catalog row를 TDD로 제거했다.
- 자동 계약은 `get_reference_contextual_help("portfolio_monitoring") is None`과 canonical Reference 3개 item·owner destination 보존을 함께 검증한다.
- 2차: Python 29+142, React 15+31, 양쪽 typecheck/build와 target py_compile을 통과했다.
- actual desktop/420px에서 help panel 미노출, Command Center 노출, horizontal overflow 0, console error 0을 확인했다.
- `/reference?item=journey.monitoring`, `concept.monitoring_scenario`, `playbook.monitoring_scenario_stale` 상세와 Portfolio Monitoring destination을 확인했다.
- durable docs와 root handoff log를 current 6-surface contextual-help 계약으로 정렬했다.
- 범위 밖의 다른 contextual-help surface와 Portfolio Monitoring 데이터·command·DB 계약은 변경하지 않았다.
