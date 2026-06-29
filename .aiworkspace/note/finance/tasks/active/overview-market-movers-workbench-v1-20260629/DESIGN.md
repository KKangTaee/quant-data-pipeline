# Design

## 1차 Product Shape

첫 화면은 `스캔 조건 -> command strip -> refresh/support controls -> 상위 변동종목 목록 -> 핵심 차트 / 섹터 요약 -> 보조 진단 -> 선택 종목 조사` 순서로 읽힌다.

Command strip은 진단 패널이 아니라 현재 작업 맥락을 요약하는 얇은 상태 표면이다. `Coverage`, `Period`, `Effective timestamp`, `Freshness`, `Universe`, `Returnable`, `Missing`, `Mode`를 보여 사용자가 어떤 데이터를 보고 있는지 먼저 확인한다.

상위 목록은 Return Table / Volume Table을 같은 위치에서 전환하게 하고, 차트는 Return Rank / Volume Rank / Sector Pulse를 같은 오른쪽 작업 영역에서 전환한다. 전체 높이의 상세 표는 expander에 보존해 기존 기능을 없애지 않는다.

## Empty State

랭킹 row가 없으면 Why It Moved 자리나 오래된 stale panel을 보여주지 않는다. 대신 선택한 coverage / period와 가능한 다음 action을 짧게 보여준다.

- `NASDAQ` + `NO_UNIVERSE`: `Nasdaq 목록 갱신`
- daily no-row: `일중 스냅샷 갱신`
- non-daily no-row: `가격 이력 갱신`

이 문구는 확정 원인 판정이 아니라 현재 read model에서 확인 가능한 상태 안내다.

## Boundary

1차는 Streamlit UI 정보 구조 변경이다. 새 수집, schema, registry/saved JSONL write, provider 직접 호출, 투자 추천, validation/monitoring 의미는 추가하지 않는다.
