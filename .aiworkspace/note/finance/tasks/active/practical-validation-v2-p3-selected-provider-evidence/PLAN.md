# Practical Validation V2 P3 Selected Provider Evidence

Status: Active
Started: 2026-05-28

## 이걸 하는 이유?

Selected Portfolio Dashboard는 선정 이후 성과 재검증과 가격 최신성은 확인하지만, Practical Validation에서 사용한 ETF provider / holdings / exposure 근거가 현재 selected portfolio에도 연결되는지 한 화면에서 확인하지 못한다.

이번 작업은 selected portfolio의 ticker weight를 기존 Final Review / Candidate Registry contract에서 읽고, 이미 DB에 있는 provider snapshot context를 read-only로 표시한다. 데이터 수집, JSONL 저장, 사용자 메모, preset 저장, monitoring log 자동 저장은 만들지 않는다.

## Scope

- Selected Dashboard에 provider evidence preflight 추가
- 기존 `build_provider_context` 서비스 재사용
- provider operability / holdings / exposure / macro display row와 look-through summary 노출
- DB read 실패, provider coverage 누락, stale / NOT_RUN 상태를 pass로 숨기지 않음
- service contract test 추가

## Non-Goals

- provider / macro 신규 수집 실행
- DB schema 변경
- JSONL registry / saved setup 추가
- selected monitoring log 자동 저장
- live approval, broker order, auto rebalance

## Exit Criteria

- Runtime 모델이 Streamlit 없이 import 가능
- Selected Dashboard에서 provider evidence를 read-only card/table로 표시
- 테스트가 DB 없이 injected provider context로 통과
- 문서가 P3 상태와 파일 책임을 반영
