# Today U.S. Market Session Status V1 Design

Status: User Approved
Last Updated: 2026-07-22

## Confirmed Product Decision

Today에는 프리마켓·애프터마켓을 표시하지 않는다. 미국 주식 정규장을 대표하는 NYSE/Nasdaq 공통 정규 시간 09:30–16:00 ET만 다룬다.

첫 화면에서 사용자는 다음 질문을 바로 끝낼 수 있어야 한다.

1. 지금 미국 정규장이 열려 있는가?
2. 뉴욕과 한국은 각각 몇 시인가?
3. 오늘 개장·마감은 양쪽 시간대로 언제인가?
4. 개장 또는 마감까지 얼마나 남았는가?
5. 오늘이 휴일·주말이거나 조기폐장일인가?

공식 기준 자료:

- NYSE trading hours / holidays: https://www.nyse.com/trade/hours-calendars
- Nasdaq market hours / holidays: https://www.nasdaq.com/market-activity/stock-market-holiday-schedule

## Chosen Approach

기존 DB-backed 공식 시장 일정과 순수 시간 계산을 결합한다.

- 단순 평일 시계만 사용하면 공식 휴일과 13:00 ET 조기폐장을 잘못 표시한다.
- 외부 market-status API를 Today render 경로에서 호출하면 기존 `Ingestion -> DB -> Loader -> UI` 경계를 깨고 첫 화면 장애 요인이 된다.
- 따라서 기존 `market_event_calendar`의 official `MARKET_HOLIDAY` / `EARLY_CLOSE` 근거를 읽고, 상태 계산 자체는 provider 접근 없이 수행한다.

## User Flow And Placement

기존 Today hero 바로 아래, 판단 근거보다 앞에 한 줄 또는 compact two-row strip을 둔다.

```text
미국 정규장 · 장 진행 중
뉴욕 10:42 · 한국 23:42
오늘 09:30–16:00 ET · 22:30–익일 05:00 KST
정규장 마감까지 5시간 18분
```

휴장일에는 `미국 정규장 · 휴장`과 휴일명 또는 `주말`, 다음 거래일 개장 시각과 남은 시간을 보여 준다. 정규장 마감 뒤에는 오늘 일정과 함께 다음 거래일 개장까지 남은 시간을 보여 준다.

색상은 상태를 보조하지만 텍스트가 의미를 소유한다. `장 진행 중`은 positive, `개장 전`은 primary, `정규장 마감`은 neutral, `휴장`은 muted tone을 사용한다. 기존 Today의 시장판단 신호 색상과 장 상태를 혼동시키는 큰 경고 패널은 만들지 않는다.

## Session Semantics

상태는 뉴욕 현지 거래일 기준으로 판정한다.

| 상태 | 조건 | 카운트다운 대상 |
|---|---|---|
| `PRE_OPEN` | 거래일 00:00 ET 이상, 개장 전 | 오늘 09:30 ET |
| `OPEN` | 개장 이상, 마감 전 | 오늘 정규장 마감 |
| `CLOSED` | 거래일 정규장 마감 이후 | 다음 거래일 09:30 ET |
| `HOLIDAY` | 공식 휴장일 | 다음 거래일 09:30 ET |
| `WEEKEND` | 토요일 또는 일요일 | 다음 거래일 09:30 ET |

UI label은 각각 `개장 전`, `장 진행 중`, `정규장 마감`, `휴장`, `휴장`이다. 경계는 `[open, close)`로 정의하여 정확히 09:30 ET부터 OPEN, 정확히 close 시각부터 CLOSED가 된다.

정상 거래일 마감은 16:00 ET, official early-close row가 있는 거래일은 저장된 `release_time_et` 또는 `event_time_label`의 13:00 ET를 사용한다. 알 수 없는 조기폐장 시간을 임의 추정하지 않는다.

## Time And DST Contract

- backend의 계산 기준은 timezone-aware UTC datetime이다.
- 현지 변환은 `zoneinfo.ZoneInfo("America/New_York")`, `zoneinfo.ZoneInfo("Asia/Seoul")`을 사용한다.
- 단순한 고정 `UTC-5` 또는 `한국 +14시간` 계산은 사용하지 않는다.
- 각 거래일의 open/close를 뉴욕 현지 datetime으로 먼저 만들고 UTC ISO timestamp로 직렬화한다.
- KST 표시가 날짜를 넘으면 `익일` 또는 정확한 월·일을 함께 표시한다.

## Component Boundaries

### Python service

`app/services/today.py` 또는 작은 전용 helper가 다음을 소유한다.

- official holiday / early-close row normalization
- 현재 뉴욕 거래일과 향후 거래일 schedule 생성
- UTC open/close boundary, holiday label, calendar quality 직렬화
- deterministic clock injection을 허용하는 pure function

Today의 기존 시장 판단 점수나 source-ready count에는 장 상태를 포함하지 않는다. 장이 열렸다는 사실은 시장 방향 근거가 아니기 때문이다.

### Today page loader

`app/web/today_page.py`는 기존 FOMC `next_event` snapshot과 별도로, 시장 구조 일정만 DB에서 읽어 service에 전달한다. render 중 provider fetch나 ingestion job을 실행하지 않는다. 많은 earnings row 때문에 holiday row가 잘리는 broad event query는 피하고, official holiday/early-close 범위만 좁게 읽는다.

### React

Today component는 payload에 포함된 multi-day schedule과 브라우저 현재 시각으로 active session을 고른다. `setInterval`로 시계와 countdown을 갱신하므로 Streamlit 전체 rerun 없이 상태가 전환된다. timer는 component unmount 시 정리한다.

payload는 최소한 다음 의미를 갖는다.

```text
market_session.timezones
market_session.calendar_quality
market_session.schedule[]
  trade_date
  day_kind
  holiday_label
  open_at_utc
  close_at_utc
  is_early_close
```

schedule은 현재 뉴욕 날짜부터 다음 개장이 안정적으로 포함되는 제한된 horizon만 제공한다. React가 휴일 규칙을 재구현하지 않고 UTC boundary만 소비하게 한다.

## Missing Calendar Handling

- 주말은 달력 자료와 무관하게 확정한다.
- official calendar row가 존재하면 휴장·조기폐장을 확정 표시한다.
- 필요한 연도의 official calendar coverage를 확인할 수 없으면 `일정 확인 필요` 보조 라벨을 붙인다.
- 자료 제한 상태에서 외부 호출로 보완하지 않으며, 확인되지 않은 휴일명을 만들지 않는다.
- schedule 자체를 만들 수 없으면 시계만 유지하고 상태/카운트다운은 `일정 자료 부족`으로 명시한다.

## Error And Boundary Handling

- exact open/close boundary를 자동 테스트한다.
- DST 시작·종료 전후에도 뉴욕 정규 시각은 09:30–16:00으로 유지하고 KST만 올바르게 달라져야 한다.
- 조기폐장일 OPEN countdown은 13:00 ET를 향해야 한다.
- 휴일 또는 주말에는 당일 정규장 시간을 열린 세션처럼 표시하지 않는다.
- 브라우저 탭이 오래 열려 날짜가 바뀌면 포함된 schedule 안에서 다음 상태를 다시 선택한다.
- schedule horizon 밖으로 넘어가면 잘못된 OPEN/CLOSED를 추정하지 않고 `새로고침 필요`를 표시한다.

## Verification Contract

### Automated

- 평일 개장 전 / exact open / 장중 / exact close / 마감 후
- 토요일·일요일과 다음 월요일 개장
- official holiday와 다음 거래일 개장
- official early close의 exact close boundary
- EST 기간과 EDT 기간의 ET/KST 표시
- missing calendar / malformed early-close row fallback
- React phase selection, countdown formatting, date-crossing KST label
- 기존 Today schema, evidence, portfolio, navigation 회귀

### Browser QA

- actual root `/`에서 상태 strip 위치와 실시간 countdown 확인
- desktop과 420px에서 overflow·clipping 확인
- 뉴욕/한국 현재 시각과 ET/KST 개장·마감 label 확인
- console warning/error 확인
- QA screenshot 한 장 생성하되 generated artifact로 커밋하지 않음

## Tradeoffs

- multi-day schedule로 장시간 열린 탭에서도 경계 전환이 가능하지만 payload가 소폭 커진다.
- 공식 일정 저장 상태에 의존하므로 calendar quality를 숨기지 않는다.
- 거래정지나 긴급 휴장 같은 당일 예외는 official row가 수집되기 전까지 반영되지 않을 수 있다. V1은 정규 calendar 상태이며 실시간 exchange halt 서비스가 아니다.
