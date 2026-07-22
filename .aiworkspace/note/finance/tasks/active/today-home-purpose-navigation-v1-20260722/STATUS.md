# Status

Status: Complete
Roadmap: 4/4차 완료

## Completed

- B안 정보 구조와 기존 탭 보존 범위 승인.
- 기존 Market Context visual token과 app shell ownership 확인.
- actual DB-backed Economic Cycle, S&P 500, Sentiment, Events, default Portfolio Monitoring payload 확인.
- implementation plan과 TDD 계약 작성.
- `app/services/today.py` pure projection과 partial/unavailable/empty 경계를 구현.
- `app/web/today_page.py`에 Market Context 계열 blue-gray/white B안과 desktop·760px·420px responsive contract를 구현.
- browser root `/`를 Today 기본 page로 두고 `Research / Portfolio / Data / Help` 목적형 navigation으로 재분류.
- 실제 DB `3/5 READY · 5/5 available` partial 상태, default group `디폴트`, 세 owner link와 기존 7개 destination의 렌더링 연속성을 Browser에서 확인.
- 독립 코드 리뷰에서 발견한 render-time default-group 생성 가능성, session-selected group drift, partial 과대 집계, storage failure 오분류를 TDD로 재현하고 전용 read-only default-group path와 상태 정책으로 수정.

## Actual State

- header 기준일 `2026-07-21`, 시장 source `3/5 READY · 5/5 available`, 종합 상태 `PARTIAL`.
- Economic Cycle `회복 / PARTIAL`, S&P 500 `상단 구간 / PARTIAL`, Futures Macro `혼재된 매크로 흐름 / READY`, Sentiment `행동 공포 · 설문 낙관 / READY`, next event `2026-07-29 FOMC`.
- 대표 포트폴리오 `디폴트`, 현재 평가액 약 `$29,781`, 당일 `+6.14%`, 누적 `+107.36%`; 화면은 누적 기여와 주의 항목을 명시적으로 구분한다.

## Boundaries / Follow-up

- Streamlit `default=True` page는 등록된 `url_path="today"` 대신 browser root `/`를 canonical 주소로 사용한다.
- Today portfolio loader는 session state와 `ensure_default_group`을 사용하지 않고 이미 저장된 `is_default` group만 읽는다. default group이 없으면 생성하지 않고 `EMPTY`, 저장소 실패면 `UNAVAILABLE`이다.
- 기존 상세 화면 내부 copy의 legacy `Workspace / Operations` 위치 문자열을 전면 개편하는 일은 승인 범위 밖이며 별도 cleanup 후보다.
- Today 자체의 대표 포트폴리오 선택 UI, live brokerage/account sync, provider 자동 갱신은 후속 승인 범위다.
