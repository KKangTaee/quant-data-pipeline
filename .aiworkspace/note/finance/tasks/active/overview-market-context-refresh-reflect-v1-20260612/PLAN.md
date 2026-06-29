# Overview Market Context Refresh Reflect V1 Plan

## 이걸 하는 이유?

1차에서 `Overview > Market Context`는 시장 브리프 중심 흐름으로 정리되었지만, 하단 `보조 갱신` 실행 후 상단 브리프가 새 snapshot을 다시 읽었는지 사용자가 확인하기 어렵다.
이번 2차는 job log를 키우는 작업이 아니라, 갱신 후 브리프가 최신 read model을 다시 읽고 그 반영 여부를 작게 알려주는 실사용 흐름 보정이다.

## 전체 흐름

- 1차 완료: Market Context를 카드형 guide가 아니라 시장 브리프 흐름으로 재구성했다. 커밋: `b7ffb8c7`.
- 2차 진행: 갱신 완료 후 Market Context cache를 지우고 rerun하여 상단 cockpit/brief가 새 snapshot 기준으로 다시 그려지게 한다.
- 3차 후속: CPI/Event coverage 보강, Macro Calendar 수집/ICS fallback 검증, Data Health 노출 범위 재검토를 별도 작업으로 다룬다.
- 별도 제품 후보: 과거 유사국면 / 향후 예측 기능은 이번 task에서 구현하지 않는다.

## Scope

- `app/web/overview_dashboard.py`의 Market Context refresh cache clear / rerun / 보조 상태 표시를 수정한다.
- 필요하면 `app/web/overview_dashboard_helpers.py`의 cached read path를 확인하되, DB schema와 provider 수집 정책은 바꾸지 않는다.
- regression test는 기존 `tests/test_service_contracts.py`의 Overview contract 영역에 추가한다.
- Browser QA는 `http://localhost:8525`에서 Overview > Market Context를 확인하고 screenshot 1장을 남긴다.

## Stop Condition

- 갱신 버튼 실행 후 success / partial success는 관련 cache clear 뒤 `st.rerun()`으로 상단 cockpit을 다시 그린다.
- 실패는 갱신 반영처럼 과장하지 않고 작은 안내로 표시한다.
- job 결과 table은 기존 expander 보조 정보로 유지한다.
- compile, diff check, focused tests, Streamlit run, Browser QA 결과를 `RUNS.md`와 최종 응답에 남긴다.
