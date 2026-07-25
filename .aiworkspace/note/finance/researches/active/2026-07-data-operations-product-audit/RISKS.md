# Risks And Open Decisions

Status: Open
Last Updated: 2026-07-25

## Product Risks

- Data Operations의 primary user가 확정되지 않으면
  단순 operator console과 non-technical product UI 사이에서 다시 혼합될 수 있다.
- 목적 기반 workflow가 너무 많은 job을 자동 연결하면
  provider rate limit과 partial-success 원인이 숨을 수 있다.
- Advanced tools를 지나치게 숨기면 PIT audit와 bounded recovery 접근성이 나빠질 수 있다.
- raw logs를 제품 UI에서 제거할 때 대체 developer access 경로를 함께 정해야 한다.

## Data Risks

- current snapshot을 historical PIT evidence로 오해하지 않도록
  consumer readiness와 validation evidence를 구분해야 한다.
- full universe refresh를 bounded default로 바꿀 때
  silently reduced coverage가 backtest 결과에 영향을 줄 수 있다.
- scheduler를 도입하면 official release timing, US market calendar,
  retry duplication, atomic writer boundary가 필요하다.

## Engineering Risks

- `sections.py`가 `_bind_page_globals()`에 의존해 작은 UI 변경도
  page/session contract에 넓게 영향을 줄 수 있다.
- current tests가 source substring과 기존 diagnostic panel 존재를 contract로 잡고 있어
  intentional removal 시 test redesign이 필요하다.
- durable background execution은 Streamlit session state만으로 해결할 수 없다.
- run history에는 ingestion 외 job도 들어오므로 domain filter 또는 store ownership을 정해야 한다.

## Approval Gates

- Data Operations primary user definition
- raw run/log/failure UI 제거 범위
- routine bounded scope와 full universe sweep 기본값
- contextual action handoff와 자동 multi-step 실행 여부
- scheduler / background worker 도입 여부

## Not A Finding Yet

- 특정 collector backend의 완전 삭제
- 특정 source의 실제 사용 빈도
- scheduler가 manual operation보다 반드시 낫다는 판단
- paid provider나 new database가 필요하다는 판단

이 항목들은 usage evidence 또는 다음 설계 차수 승인 전에는 결론으로 취급하지 않는다.
