# 선물 매크로 장중 변화 개편 개발 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task after the user requests execution. Steps use checkbox (`- [ ]`) syntax for tracking. 이 문서 작성 요청은 구현 승인이 아니다.

**Goal:** 선물 매크로를 ‘미국장 마감 이후 / 최근 1시간의 변화 → 교차자산 반응 → 다음 확인 조건’으로 개편하고 현재 관측 갱신에서 무거운 전망 검증을 제거한다.

**Architecture:** 기존 ingestion·DB·완료 일봉과 공용 current observation을 재사용한다. 장중 구간 수익률과 설명 규칙은 Python 서비스로 분리하고, 두 구간의 read model을 Streamlit을 통해 React에 전달한다. 기존 예측 모델은 명시적 연구 경로로 분리한다.

**Tech Stack:** 기존 Python / pandas / MySQL / Streamlit / React / TypeScript / Vite. 새 시세 공급사·자동 scheduler·백그라운드 queue는 추가하지 않는다.

**Spec:** [DESIGN.md](./DESIGN.md). 사용자 시안 승인 취지와 실제 코드 의존성을 함께 반영한 설계 제안.

Date: 2026-09-21
Execution: **개발 0/5단계. 가이드 검토 후 사용자 작업 요청 대기.**

## 이걸 하는 이유?

경기국면에도 자산별 확인 포인트가 있으므로 선물 탭의 차별점은 장중의 새로운 변화여야 한다. 기존 수집과 데이터 품질 처리를 살리는 편이 새로 만드는 것보다 변경 범위가 작다. 특히 앞선 측정에서 70.6초 갱신 중 57.8초가 snapshot materialization이었고, 별도 읽기 전용 재현에서 숨겨진 5D/20D 검증이 약 60.3초였다. 화면 카드 수를 줄이거나 파일을 삭제하는 것만으로 해결되지 않는 병목이다.

## 개발은 총 5단계

| 차수 | 목적·결과 | 수정 범위 | 완료 조건 / 다음 연결 |
|---|---|---|---|
| **1차 · 기존 계산 정리** | 갱신에서 무거운 전망 검증을 분리하고 재사용 기반 보존 | snapshot, ingestion attach, refresh, 공용 reader | 현재 관측 parity / 전망 실행 0회 / Today·Monitoring 회귀 없음 → 새 계산의 기반 |
| **2차 · 장중 비교 데이터** | 마감 이후·최근 1시간의 실제 수익률과 공통 관측 시각 제공 | windows service, DB loader, calendar adapter, refresh job | 주말·DST·조기폐장·누락에도 정확한 기준점, 부분 자료를 현재 전체로 표시하지 않음 → 해석의 입력 |
| **3차 · 해석과 다음 확인** | 관측·가능한 의미·반대 근거·다음 관측을 일관되게 연결 | reading service, overview read model | 정해진 사실에서 재현되는 문장, 양쪽 window 전환 시 의미 일치 → 화면의 내용 |
| **4차 · 시안 화면 적용·전용 코드 정리** | 세 영역과 두 기간 선택으로 실제 탭 교체 | Python UI adapter, React component/types/styles, fallback | 실제 DB 값·날짜와 시안 흐름 연결, 불필요한 리본·중복 요약 제거 → 사용자 흐름 완성 |
| **5차 · 통합 검증·속도 확인** | 실제 갱신과 다른 화면까지 검증해 개편 종료 | 관련 회귀, Browser QA, 성능 기록, 문서 | 수집→표시 및 오류·휴장·좁은 화면 검증, 성능 전후 비교, 공유 소비자 정상 → 실사용 개편 완료 |

1차만 끝내고 전체 개선 완료로 부르지 않는다. 1차에서는 기존 화면이 유지될 수 있고, 4차부터 새 흐름을 실제 탭에서 볼 수 있다. 5차까지가 이번 개편의 범위다. 장중 역사 기반 예측 확률은 별도 후속 연구이며 자동으로 6차를 시작하지 않는다.

## 먼저 정리할 것

| 처리 | 구체 대상 |
|---|---|
| **남김** | 17개 공용 수집 universe, DB 원본, 완료 5분봉·일봉, session finalization, 공용 current family 계산, cache·source 시각·명시적 refresh |
| **갱신 경로에서 뺌** | nested 5D/20D 검증, 모델 선택, 전체 역사 재생, forecast history 생성 |
| **새 흐름으로 교체** | 재가격화 해석, 1D/5D/20D 중심 요약, 방향 정렬, 복잡한 근거 표시 |
| **탭에서 제거** | 최근 체제 리본, 체제 좌표·벡터, 오래된 outlook/pathway 계약과 중복 요약 |
| **참조 확인 후 삭제** | 탭 전용 미사용 component/helper/type/CSS. Today·Monitoring·수집 코드에서 쓰는 기능은 보존 |
| **보존만 함** | 기존 연구 코드·예측 검증 기록·DB history. 새 관측을 위해 M2 연구 모델부터 수리하지 않음 |

권고 순서는 **호출 분리 → 새 결과 검증 → 화면 교체 → 남은 전용 코드 삭제**다. 코드 대량 삭제를 먼저 하면 공용 의존성 복구 비용이 커질 수 있다.

## Global Constraints

- 사용자 승인 범위는 개발 가이드까지다. 후속 작업 요청 전 구현·수집·DB 변경 금지.
- `Ingestion -> DB -> Loader / Service -> Runtime -> UI`. UI는 provider를 직접 호출하지 않는다.
- 시간 내부값은 aware UTC; 거래일 America/New_York; 표시 KST. 완료 5분봉만 사용한다.
- 기간은 `since_close` / `last_hour`. 기간 전환은 provider·연구 계산을 호출하지 않는다.
- 달러 대용지표는 EUR/JPY/GBP/AUD/CAD 선물 역방향 동일 가중 평균. 구성원 누락 시 재가중 금지.
- 장중 stale 초기 상한은 기존 30분. 정상 휴장과 데이터 갱신 지연을 구별한다.
- 새 UI는 `futures_macro_intraday_workbench_v1`. 장중 상태와 연구 검증 상태를 분리한다.
- 현재 관측과 예측 연구의 저장 key·기준일·실행 경로를 분리한다. 기존 데이터/history/registries/saved 삭제 금지.
- Today·Portfolio Monitoring의 일별 current family 의미와 날짜를 보존한다.
- 시안 수치는 가상이다. 실제 화면에 hardcode하지 않는다.
- 신규 작업/run 진단 대시보드는 만들지 않는다. source/시각/누락은 해석에 필요한 보조 근거다.
- 매매 신호·정확한 다음 방향·금리인하 확률·장중 적중률은 이번 개편의 공개 결과가 아니다.
- 리팩터링은 이 탭의 필요한 경계로 제한한다. 경기국면·물가정책의 계산 변경은 포함하지 않는다.

## Review Focus

| 입력/실패 조건 | 기대 동작 | 테스트 소유 |
|---|---|---|
| 월요일·연휴·DST·조기폐장 | 실제 직전 정규장 마감과 정확한 UTC 기준점, calendar 불확실 시 마감 window만 보류 | 2차 windows/calendar |
| 통화 1개 결측·미완료 봉·지연·서로 다른 timestamp | 달러 재가중/forward-fill 금지, 부분 관측 공개 범위 제한 | 2차 windows, 3차 reading |
| 현재 관측 저장 실패·과거 기준일 결과의 늦은 저장 | 기존 좋은 결과 보존, 새 값인 것처럼 표시하지 않음 | 1차 snapshot, 5차 통합 |
| 거래 중단·음수/0/NaN 가격·연속계약 교체 | 수익률 계산 제한과 source 한계 표시, 큰 경제 충격으로 자동 해석하지 않음 | 2차 returns, 3차 reading |
| 새 관측/구형 snapshot, UI 재클릭, unrelated 종목 누락 | Today/Monitoring 호환, 중복 갱신 방지, 없는 근거를 포함한 결론 금지 | 1차 consumer, 4차 UI, 5차 통합 |

---

## 1차 · 기존 계산 정리

**Files**

- Create: `app/services/futures_macro_observation_snapshot.py`
- Modify: `app/services/futures_macro_snapshot.py`, `app/jobs/ingestion_jobs.py`, `app/jobs/overview_actions.py`, `finance/data/futures_macro_snapshot.py`
- Reuse: `app/services/futures_macro_pattern.py`, `futures_macro_daily_loader.py`, `futures_macro_thermometer.py`, `futures_macro_sessions.py`
- Test: `tests/test_futures_macro_observation_snapshot.py` (신규), `tests/test_futures_macro_snapshot.py`, `tests/test_overview_futures_macro_refresh.py`, `tests/test_ingestion_jobs.py`, `tests/test_today_home.py`, `tests/test_portfolio_monitoring_macro_context.py`

**Interfaces**

- Consumes: 완료 일봉과 기존 `build_pattern_feature_frame`, `build_current_pattern_snapshot`, thermometer의 current 계산.
- Produces: DESIGN의 observation materializer와 새 snapshot key; 기존 공용 load 함수의 반환 `macro`, `pattern_outlook.current_pattern`, `metadata` 유지.
- Production attach는 경량 materializer를 호출한다. 기존 full materializer는 명시 호출 연구 API로 남긴다.

- [ ] 공유 참조와 현재 마지막 유효 payload를 고정 fixture로 남긴다. Today/Monitoring이 읽는 family 값·기준일을 비교한다.
- [ ] current 계산만 실행하는 테스트를 먼저 추가한다. full outlook builder를 호출하면 실패하는 sentinel을 세워 단순 '화면에서 안 보임'과 실제 '계산 안 함'을 구별한다.
- [ ] observation payload와 저장 함수를 구현한다. 아래 반환 의미를 고정한다.

```python
def build_observation_payload(*, macro, current_pattern, as_of_date, materialized_at):
    return {
        "macro": macro,
        "pattern_outlook": {
            "status": current_pattern.get("status", "UNAVAILABLE"),
            "current_pattern": current_pattern,
            "horizons": [],
            "research_status": "NOT_COMPUTED",
        },
        "as_of_date": as_of_date,
        "materialized_at": materialized_at,
    }
```

- [ ] 새 key에 현재 관측만 저장하고 forecast history를 쓰지 않는다. 동시/늦은 결과에서 완료 기준일이 후퇴하지 않는 transactional writer 테스트를 추가한다. read는 새 key 우선, 기존 key fallback이며 각각의 날짜를 보존한다.
- [ ] Overview refresh와 `attach_futures_macro_materialization` 기본 호출을 경량 경로로 바꾼다. 코드의 `include_validation=False` 하나만 바꾸는 수정으로 끝내지 않는다.
- [ ] 회귀 및 snapshot 계산 시간을 확인하고 `선물 매크로 현재 관측과 전망 연구 실행 분리` 단위로 커밋한다.

현재 관측 보존 계약의 최소 테스트 예시:

```python
from app.services.futures_macro_observation_snapshot import build_observation_payload

current_fixture = {
    "as_of_date": "2026-09-18",
    "status": "OK",
    "families": {"rate_pressure": {"five_day": 0.8, "twenty_day": 0.4}},
}
payload = build_observation_payload(
    macro={"status": "OK"},
    current_pattern=current_fixture,
    as_of_date=current_fixture["as_of_date"],
    materialized_at="2026-09-21 07:00:00",
)
assert payload["pattern_outlook"]["horizons"] == []
assert payload["pattern_outlook"]["research_status"] == "NOT_COMPUTED"
assert payload["pattern_outlook"]["current_pattern"]["families"] == current_fixture["families"]
assert payload["as_of_date"] == current_fixture["as_of_date"]
```

핵심 검증은 값의 parity에 더해 full outlook sentinel 호출 0회, forecast history writer 호출 0회, current writer 실패 시 기존 row 보존이다. 실패 테스트를 먼저 실행한 뒤 변경 후 같은 테스트를 재실행한다.

**완료:** 기존 소비자 정상, current 기준일 전진 정상, nested 검증은 갱신 경로에서 호출되지 않음. 이 단계의 성능 개선은 실제로 측정하며 60초 전체가 반드시 사라진다고 미리 보장하지 않는다.

## 2차 · 장중 비교 데이터

**Files**

- Create: `app/services/futures_macro_windows.py`, `app/jobs/futures_macro_refresh.py`
- Modify: `finance/loaders/futures.py`, `app/jobs/overview_actions.py`; 필요한 경우 `finance/data/futures_market.py`의 bounded collection 인자
- Reuse: `app/services/today_market_session.py`, `app/services/futures_macro_sessions.py`, `app/jobs/futures_macro_daily_finalization.py`, `finance/data/futures_session_finalization.py`
- Test: `tests/test_futures_macro_windows.py`, `tests/test_futures_macro_observation_refresh.py` (신규), 기존 intraday/session/finalization 테스트

**Interfaces**

- Consumes: DB의 raw `provider_symbol/candle_time_utc/close/collected_at`, 저장 calendar, evaluation time.
- Produces: DESIGN에 정의한 normalized bars, two-window snapshot, bounded refresh `JobResult`.

- [ ] 정확한 endpoint·미완료 봉 배제·공통 timestamp·missing 통화·0/음수/NaN을 재현하는 테스트를 작성하고 실패를 확인한다.
- [ ] DB loader를 시간 범위와 필요한 columns로 제한한다. 기존 문자열 날짜 범위 loader를 쓸 때 하루 단위 truncation으로 장중 endpoint가 사라지지 않도록 전용 aware-UTC 범위를 제공한다.
- [ ] 완료 봉 정규화, calendar 기준점, 같은 endpoint의 수익률과 달러 대용지표를 구현한다. 핵심 수식은 다음과 같고 표시 반올림 전에 계산한다.

```python
from math import isfinite

def price_return_pct(start_close, end_close):
    if not all(isfinite(v) and v > 0 for v in (start_close, end_close)):
        return None
    return 100.0 * (end_close / start_close - 1.0)

def dollar_proxy_pct(currency_returns):
    if len(currency_returns) != 5 or any(v is None for v in currency_returns):
        return None
    return -sum(currency_returns) / 5.0
```

실제 구현에서는 인입 변환 실패도 결측으로 처리한다. quote별 정확한 source symbol 집합 검증은 위 평균 계산 전 window builder가 소유한다.

```python
from datetime import datetime, timezone
import pytest
from app.services.futures_macro_windows import build_window_returns

def test_missing_endpoint_is_not_forward_filled():
    start = datetime(2026, 9, 21, 5, 0, tzinfo=timezone.utc)
    end = datetime(2026, 9, 21, 6, 0, tzinfo=timezone.utc)
    rows = [{"provider_symbol": "ES=F", "bar_end_utc": start, "close": 100.0}]
    result = build_window_returns(rows, symbols=["ES=F"], start_utc=start, end_utc=end)
    assert result["returns_pct"]["ES=F"] is None
    assert result["missing_symbols"] == ["ES=F"]

def test_return_uses_the_two_exact_endpoints():
    start = datetime(2026, 9, 21, 5, 0, tzinfo=timezone.utc)
    end = datetime(2026, 9, 21, 6, 0, tzinfo=timezone.utc)
    rows = [
        {"provider_symbol": "ES=F", "bar_end_utc": start, "close": 100.0},
        {"provider_symbol": "ES=F", "bar_end_utc": end, "close": 100.25},
    ]
    result = build_window_returns(rows, symbols=["ES=F"], start_utc=start, end_utc=end)
    assert result["returns_pct"]["ES=F"] == pytest.approx(0.25)
```

- [ ] 전용 refresh를 기존 일별 처리와 분리하고, DB coverage→필요한 5분봉 추가→필요한 일봉 확정→경량 관측 저장으로 연결한다. 기존 17종목 공용 설정은 축소하지 않는다.
- [ ] 주말에 2일 자료가 부족한 경우를 재현하고 5d→누락 종목만 1mo의 제한된 보충을 검증한다. 최근 1시간 비교는 가능하지만 마감 window만 불가하면 두 구간을 일괄 실패 처리하지 않는다.
- [ ] DST/휴일/13:00 조기폐장 및 16:00 정상 마감 fixture, 정상 휴장과 stale 구분을 검증하고 `선물 장중 비교 구간과 현재 데이터 갱신 구현` 단위로 커밋한다.

**완료:** 두 구간 모두 실제 가격·시작·종료를 설명할 수 있음. 공급사 데이터 공백은 값을 발명하지 않고 제한 상태로 표시 가능. 주말/휴장 처리 완료 전 평일 happy path만으로 완료하지 않는다.

## 3차 · 해석과 다음 확인

**Files**

- Create: `app/services/futures_macro_reading.py`, `app/services/overview/futures_macro.py`
- Test: `tests/test_futures_macro_reading.py`, `tests/test_overview_futures_macro_intraday.py` (신규)
- Reuse: `app/services/overview/economic_cycle.py`의 실제 current read model

**Interfaces**

- Consumes: 2차 두 window의 값·coverage·status, 실제 경기 배경.
- Produces: `build_futures_macro_change_reading`과 `build_futures_macro_intraday_read_model`, DESIGN의 UI schema.

- [ ] 부담 조합/완화 조합/엇갈림/상승분 반납/일부 지수만 하락/자료 공백을 고정 input으로 만든다.
- [ ] 표의 rule마다 관측 fact와 문구의 일치를 테스트한 뒤 Python에서 rules와 Korean copy를 구현한다. 값의 표시 방향과 문장 방향이 엇갈리지 않게 한다.
- [ ] window마다 `headline`, `observation_facts`, `interpretation`, `counter_evidence`, `next_checks`를 만든다. 부재한 YM/RTY를 포함해 '주식시장 전체'라고 쓰지 않는다.
- [ ] `cycle_background`는 현재 경기국면의 state/date만 읽는다. 월간 판단을 장중 가격으로 수정하지 않는다. 다른 탭의 전체 모델을 재계산하지 않는다.
- [ ] 두 window와 실제 calendar/source marker를 포함한 cache identity를 적용하고 수정 봉·버전 변경·누락 변경에 invalidation을 검증한다.
- [ ] `선물 장중 관측의 해석과 확인 조건 연결` 단위로 커밋한다.

대표 rule fixture의 완전한 의도:

```python
from app.services.futures_macro_reading import build_futures_macro_change_reading

window = {
    "status": "AVAILABLE",
    "returns_pct": {"ES=F": 0.18, "NQ=F": 0.42, "ZN=F": -0.26},
    "dollar_proxy_pct": 0.31,
    "missing_symbols": [],
}
reading = build_futures_macro_change_reading(window)
assert "하락 확률" not in reading["headline"]
assert "국채" in " ".join(reading["observation_facts"])
assert "상승" in " ".join(reading["counter_evidence"])
assert len(reading["next_checks"]) == 2
```

위 window는 reading 전용 값이며 UI의 prices 배열은 overview read model에서 변환한다. 실제 문구는 DESIGN 규칙표에 따른다. 누락 window fixture에서는 금리·달러 결합 문장이 생성되지 않는지 별도로 고정한다.

**완료:** 사용자가 관측 사실과 해석을 구별하고, 같은 입력에는 같은 문장이 나오며, 반대 근거와 다음 확인 조건이 함께 제공됨. 문장 생성이 연구상의 예측 gate를 대신하지 않음.

## 4차 · 시안 화면 적용과 전용 코드 정리

**Files**

- Modify: `app/web/overview/futures_macro_helpers.py`, `futures_macro_react_component.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`, `contracts.ts`, `presentation.ts`, `style.css`
- Create: 같은 `src/`의 `IntradayChangeSummary.tsx`, `AssetChangeStrip.tsx`, `ObservationReading.tsx`
- Remove after reference check: `PatternRibbonSection.tsx`, `PatternMapSection.tsx`, `PatternHorizonSection.tsx`, `AssetPathwaysSection.tsx`, `CurrentEvidencePanel.tsx`; 교체 완료된 `MarketRepricingSection.tsx`, `FamilyDirectionSection.tsx`, `ShortHorizonDecisionSection.tsx` 및 전용 type/CSS
- Adapt/reuse: `MacroContextSection.tsx`, `MethodDisclosure.tsx`, `CalculationTraceDisclosure.tsx`에서 필요한 controls·근거만. 재사용보다 교체가 간단하면 작은 새 component로 통합
- Test: `tests/test_overview_futures_macro_intraday.py`, `tests/test_overview_futures_macro_short_horizon.py`, `tests/test_futures_macro_v2_integration.py`의 살아 있는 계약을 새 schema에 맞춰 갱신

**Interfaces**

- Consumes: 3차 `futures_macro_intraday_workbench_v1`. 기간 변경은 전달받은 두 window 사이의 local selection.
- Produces: 원래 route/key를 유지한 실제 선물 탭, Python dispatch refresh action, 같은 의미의 Streamlit fallback.

- [ ] schema 계약과 결과 기준일 테스트를 먼저 추가하고 구 v7의 제거된 UI 요소를 요구하는 assertion은 의미 단위로 교체한다.
- [ ] 세 영역, 두 기간 선택, 경기 배경/기존 탭 링크를 구현한다. 시안에서 비교용으로 만든 경기국면 화면을 제품에 복사하지 않는다.
- [ ] 새 selector의 한 동작으로 제목·가격·근거·시각·next_checks 전체가 같은 window를 참조하도록 한다.

```tsx
const [period, setPeriod] = useState<"since_close" | "last_hour">("since_close");
const window = payload.windows[period];
// Summary, price strip, reading and timestamp all consume this same window.
```

- [ ] 진행 중 refresh action은 실제 결과 nonce까지 잠근다. 기존 900ms timer만으로 pending을 해제하지 않는다. 오류 시 이전 유효 관측의 기준일을 보존하고 오류 메시지와 갱신 가능 동작을 제공한다.
- [ ] 정상·partial·stale·휴장·무자료·React unavailable fallback을 모두 연결한다. 과거 항목은 검증 전으로 접어 두며 fictitious n/N을 넣지 않는다.
- [ ] 생산 코드의 import/type/CSS 참조를 검색한 뒤 탭 전용 구파일만 삭제한다. 공용 family 계산·DB history·연구 모델은 삭제하지 않는다.
- [ ] TypeScript 확인·production build 후 desktop/900px/420px Browser QA, 스크린샷을 남기고 `선물 매크로를 장중 변화 중심 화면으로 개편` 단위로 커밋한다.

**완료:** 사용자가 마감 이후 전체 변화와 최근 1시간 반응을 구별하고, 근거와 다음 확인을 한 화면에서 읽음. 진단 표만 예쁘게 바꾸거나 카드만 줄이는 작업으로 완료 처리하지 않는다.

## 5차 · 통합 검증과 속도 확인

**Files**

- Test: 앞선 신규 테스트, 기존 refresh/snapshot/intraday/session/finalization, `test_today_home.py`, `test_portfolio_monitoring_macro_context.py`, `test_ingestion_jobs.py`
- Documentation: 이 task 6개 문서, 실제 바뀐 경계를 소유하는 `docs/PROJECT_MAP.md`와 해당 flows/data/runbooks; `PRODUCT_DIRECTION.md`/`ROADMAP.md`는 구현 완료된 역할/baseline을 필요한 만큼만 반영

**Interfaces**

- Consumes: 1~4차 통합 제품, DB-backed current source, 고정 시간 fixture, 실제 refresh 결과.
- Produces: 단계별 시간 측정, 오류/holiday/browser evidence, 최종 잔여 한계와 완료 기록.

- [ ] 수집 없이 진입·기간 전환·저장 자료 다시 읽기가 동작하는지 확인한다. refresh에서만 provider를 호출하고 연구 builder는 호출되지 않아야 한다.
- [ ] actual DB/실제 갱신 1회와 동일 저장 데이터 기반 반복 3회로 provider·DB·현재 계산·render 시간을 구분해 기록한다. 옛 70.6초 단일 측정과 환경이 다르면 직접 속도비로 과장하지 않는다.
- [ ] **성능 목표:** 저장 자료 재표시·기간 전환은 불필요한 네트워크 대기 없음, 로컬 DB 읽기+현재 계산+저장 목표 5초 이내. 실제 수집 포함 총시간은 별도 측정하며 외부 응답 시간을 숨기지 않는다. 목표 미달이면 가장 큰 내부 구간을 개선하고 다시 확인한다.
- [ ] 정상/부분성공/공급사실패/마감 기준점 부족/휴장/중복클릭을 actual 또는 deterministic fixture로 검증한다. 실제 휴일을 기다려야 하는 항목은 calendar fixture와 실제 DB coverage를 구별해 기록한다.
- [ ] Today·Portfolio Monitoring의 current family와 날짜가 보존됐는지 확인한다. standalone full research는 명시 호출에서만 접근 가능하며 새 화면이 의존하지 않아야 한다.
- [ ] 최종 Browser QA 스크린샷 1장 이상, 변경 파일별 필요한 문서, commit, STATUS 5/5를 정렬한다. 검증 실패와 관측 제한을 pass로 기록하지 않는다.

관련 검증 명령(새 테스트는 생성한 뒤 실행):

```bash
.venv/bin/python -m pytest tests/test_futures_macro_observation_snapshot.py tests/test_futures_macro_snapshot.py tests/test_overview_futures_macro_refresh.py tests/test_ingestion_jobs.py tests/test_today_home.py tests/test_portfolio_monitoring_macro_context.py -q
.venv/bin/python -m pytest tests/test_futures_macro_windows.py tests/test_futures_macro_observation_refresh.py tests/test_futures_macro_reading.py tests/test_overview_futures_macro_intraday.py tests/test_futures_macro_intraday.py tests/test_futures_macro_sessions.py tests/test_futures_session_finalization.py -q
.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py tests/test_futures_macro_v2_integration.py -q
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
git diff --check
```

`package.json`에 현재 test/typecheck script는 없다. 존재하지 않는 `npm test`를 검증 완료로 기록하지 않는다. TypeScript 확인은 해당 component 디렉터리에서 설치된 `node_modules/.bin/tsc --noEmit`으로 수행한다. 환경 Node/Python 경로가 없으면 먼저 이용 가능한 runtime을 확인한다.

## 별도 후속 후보: 장중 과거 사례와 전망

이번 5단계는 현재 관측 도구의 완성이다. 이후 사용자가 요청하면 장기 장중 history coverage, 당시 사용 가능 가격, 세션·시간대별 baseline, 비중복 episode, 향후 1시간/정규장 마감 target과 chronological holdout을 먼저 설계한다. 데이터를 보고 유리한 조건을 반복 선택하지 않는다. 검증된 범위만 n/N과 평소 대비 차이 또는 조건부 전망으로 공개한다.

## 실행 handoff

- 현재 완료: 개발 가이드와 설계 작성·참조 확인.
- 개발 진행: **0/5단계**. 다음은 사용자 검토 후 1차 시작.
- 실행 시 원본 workspace 상태와 branch를 다시 확인한다. 계획 작성 시 실제 branch는 `master`였고 user PNG 4개가 untracked였다. 임의 정리하지 않는다. 구현용 격리가 필요하면 `codex/` branch의 worktree를 사용한다.
- 기본 실행은 단계별 순차 진행이며, 사용자 요청 없이 별도 task 생성·병렬 agent 위임을 가정하지 않는다.
- 불확실한 source 특성 때문에 목표가 바뀌면 변경점과 영향을 먼저 설명한다. 결측을 임의 보정하거나 범위를 몰래 확장하지 않는다.
