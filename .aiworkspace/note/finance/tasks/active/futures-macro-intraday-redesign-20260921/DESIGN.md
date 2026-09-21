# 선물 매크로 장중 변화 화면 설계

Date: 2026-09-21
Decision: 사용자 시안 선호 확인, 개발 가이드 검토 전 / 구현 미승인

## 이걸 하는 이유?

경기국면은 발표된 경제자료로 경제의 배경과 전환 확인 조건을 설명한다. 해당 탭에도 최신 자산별 확인 포인트가 있으므로, 선물 탭이 현재 가격과 같은 해석만 반복하면 역할이 겹친다. 선물 매크로는 **직전 미국 정규장 마감 이후 / 최근 1시간의 가격 변화**, 다른 자산의 동반 반응, 다음 확인 조건을 제공한다.

긴 거래시간은 장외 시간대에도 변화를 관측할 기회를 준다. 예측 우위는 별도 질문이다. 기존 일봉 조건의 5D 예비 검증 실패는 장중 관측의 효용을 검증한 결과가 아니며, 이를 이유로 관측 기능을 포기하지 않는다.

## 승인 근거와 범위

- 사용자는 2026-09-21 인터랙티브 시안의 방향에 동의하고, 기존 기능 정리부터 시작하는 구체적 개발 가이드를 요청했다.
- 명시적 실행 경계: **“그 내용을 확인한 후 작업 요청할께”**. 이번 산출물은 계획이며 구현·수집·DB 변경은 하지 않는다.
- 시안: `/Users/taeho/.codex/visualizations/2026/09/20/01a0c136-bc3c-73a0-8da0-8a18eda4f205/futures-market-change-preview.html`. 시안 수치와 상태는 전부 가상이다. 이 파일은 generated artifact이며 커밋하지 않는다.
- 기존 근거: [성능 감사](../../../researches/active/2026-09-futures-macro-performance-value-audit/CURRENT_PROJECT_AUDIT.md), [실제 일봉 예비 검증](../../../researches/active/2026-09-futures-macro-performance-value-audit/EMPIRICAL_PILOT_RESULT.md).

## 최종 사용자 흐름

1. 선물 매크로 진입: DB의 관측을 읽는다. 진입만으로 수집·과거 검증을 시작하지 않는다.
2. 기본 비교는 **미국장 마감 이후**. **최근 1시간**으로 바꾸면 같은 화면의 가격·문장·확인 조건이 함께 바뀐다. 두 구간 모두 과거 관측이며 미래 예측 기간이 아니다.
3. 첫 영역: 무엇이 새로 달라졌는지 한 문장, 공통 관측 시각, 경기 배경 한 줄.
4. 두 번째 영역: S&P 500·나스닥·10년 국채·달러 대용지표·금·원유의 같은 구간 가격 변화율.
5. 세 번째 영역: 관측 사실 → 가능한 의미 → 확산/완화 확인 조건. 다우·소형주·구리는 관련 근거로 사용한다.
6. `최신 데이터 반영`은 수집·현재 관측 갱신만 실행한다. `저장 자료 다시 읽기`는 DB/cache만 읽는다. 재클릭은 진행 중인 실행을 중복 시작하지 않는다.
7. 계산 기준·자료 공백은 접힌 근거에 둔다. 원시 run/job/row 표를 새 주요 패널로 만들지 않는다.

시안의 경기국면 화면은 역할 비교용이었다. 실제 경기국면 화면을 시안대로 개편하지 않는다. 선물 화면에서 기존 경기국면의 실제 상태·기준일을 읽고 기존 탭으로 연결하는 범위만 포함한다.

## 유지·분리·제거 결정

| 분류 | 대상 | 결정과 이유 |
|---|---|---|
| 유지 | 선물 OHLCV ingestion, DB, 5분봉, 완료 일봉, session finalization | 새 기능에 필요한 기반. 원시 저장 데이터 삭제 없음 |
| 유지 | 현재 17개 공용 수집 universe | 다른 consumer가 있으므로 전역 축소하지 않음. 화면에 쓰는 subset과 수집 universe를 구별 |
| 유지 | Python 계산 / Streamlit command / React 표시 경계 | 화면에서 provider 직접 조회하지 않음 |
| 유지·보완 | 완료 5분봉 필터, timezone, 지연·누락 판단 | 장중 비교에 재사용. 서로 다른 시각을 같은 시각으로 취급하지 않음 |
| 호환 유지 | 기존 1D/5D/20D current family 계산 및 저장 읽기 | Today와 Portfolio Monitoring이 사용. 새 장중 수익률로 몰래 대체하지 않음 |
| 제품 실행에서 분리 | nested 5D/20D 전망·모델 선택·전체 역사 검증 | 사용자의 현재 관측 클릭에서 실행하지 않음. 수동 연구 호출 및 기존 연구 기록은 보존 |
| 교체 | 시장 재가격화, 단기 요약, 선물군 방향 정렬 | 장중 가격 변화와 규칙 기반 해석으로 재작성. 기존 5D 점수의 단순 라벨 변경 아님 |
| 탭에서 제거 | 최근 60일 체제 리본, 체제 좌표/벡터, 5D/20D 전망 및 score pathway UI 계약 | 장중 변화라는 목적과 다른 정보. 기존 조사 기록은 보존 |
| 접힌 근거로 축소 | raw 점수·전 종목 표·계산 설명 | 선택 구간의 가격, 시각, 누락과 의미 확인에 필요한 항목만 표시 |
| 교체 후 삭제 | 참조가 없어진 탭 전용 React component, Python helper, type/CSS | 공유 참조 검색과 빌드 후 삭제. 파일 수 감소 자체를 성과로 보지 않음 |
| 이번 개편에서 수리하지 않음 | 기존 M2 macro contribution 계약 불일치 | 사용하지 않을 전망 모델의 별도 연구 문제. 새 관측의 선행조건으로 만들지 않음 |

## 데이터·시간 계약

### 대상과 단위

- 가격 기본: `ES=F`, `NQ=F`, `ZN=F`, `GC=F`, `CL=F`.
- 달러 대용지표: `6E=F`, `6J=F`, `6B=F`, `6A=F`, `6C=F`의 같은 구간 수익률에 반대 부호를 적용한 동일 가중 평균. 5개 중 하나라도 없으면 대용지표를 비공개한다. 가용 종목만으로 가중치를 바꾸지 않는다.
- 확산 근거: `YM=F`, `RTY=F`; 원자재 맥락: `HG=F`; 국채 보조: `ZB=F`. 화면 첫 줄에는 늘리지 않는다.
- `DX-Y.NYB`의 DXY, 위 달러 대용지표, 개별 통화 선물은 서로 다른 값이다. 새 화면에서 모두 '달러선물 수익률'로 묶지 않는다.
- 국채선물은 가격 수익률이다. 국채금리 bp 변화나 Fed 정책금리 확률로 변환하지 않는다.
- 수익률은 같은 provider series의 `100 * (end_close / start_close - 1)`. 시작/끝 가격이 0 이하이거나 비유한이면 값과 해석을 보류한다. 조정 없는 연속계약이라는 source 한계를 근거에 명시한다.

### 시간과 결측

1. 내부 시간은 timezone-aware UTC, 사용자 표시 KST, 거래일 판단 America/New_York. 시간대를 숫자 13/14시간으로 고정하지 않는다.
2. 저장된 5분봉의 timestamp가 시작 시각이라는 기존 계약을 확인하고 `bar_end = candle_time_utc + 5분`으로 정규화한다. `bar_end <= evaluated_at`만 읽는다.
3. 필수 관측 집합은 ES·NQ·ZN·5개 통화선물이다. 공통 종료 시각은 필수 집합에서 이용 가능한 완료 봉의 **실제 교집합**으로 선택한다. 단순 min(latest) 후 종목별 forward-fill은 금지한다.
4. 필수 집합의 일부가 없으면 `PARTIAL`이다. 존재하는 ES/NQ/ZN에 공통 시각이 있으면 그 시각의 개별 값은 표시할 수 있지만, 금리·달러·주식 결합 해석은 보류한다. 대체에 사용한 집합·누락 품목을 표시한다. 어떤 기준 집합에도 공통 시각이 없으면 `UNAVAILABLE`이다.
5. GC/CL/YM/RTY/HG/ZB는 선택된 종료 시각과 같은 봉을 사용한다. 없으면 해당 자산만 `—`이며 없는 자산을 포함한 결론을 만들지 않는다.
6. 미국장 마감 이후: 종료 시각 이전의 가장 최근 미국 정규장 실제 마감 시각을 기준으로 한다. 주말·휴장·조기폐장·DST를 저장된 calendar와 `today_market_session.py`의 시간 계산으로 처리한다. 해당 함수가 현재 이후 schedule을 만드는 점을 감안하여 조회 시작일을 앞당겨 과거 15일의 schedule을 구성한다. calendar가 확인되지 않으면 마감 기준 비교만 보류하고 가능한 최근 1시간은 제공한다.
7. 최근 1시간: 공통 종료 시각에서 정확히 60분 전의 완료 봉과 비교한다. 휴장·거래 중단으로 해당 시작 봉이 없으면 다른 시점으로 몰래 이동하지 않는다.
8. 두 endpoint의 같은 시각 가격을 요구한다. 누락된 마감 기준 가격을 일봉 종가·결제가·최근 체결가로 대체하지 않는다.
9. 기존 30분 stale 상한을 초기값으로 유지한다. 거래 중 오래된 관측은 `STALE`; 정상 휴장·정기 중단은 `MARKET_CLOSED`와 마지막 관측 시각으로 구별한다. 상품별 휴장 확인이 불가능하면 휴장으로 추측하지 않고 관측 제한을 표시한다.
10. 가격을 소수 둘째 자리 %로 보여주므로 `0.00%`는 방향 문구도 보합으로 처리한다. 이것은 표시 정밀도 기준이지 경제적으로 유의미한 움직임의 통계적 임계값이 아니다.

### 수집과 cache

- 현재 `2d/5m` 수집만으로 월요일의 금요일 마감 기준을 항상 확보한다고 가정할 수 없다.
- 새 전용 refresh는 먼저 DB에서 두 구간의 endpoint coverage를 확인한다. 기존 자료가 있으면 최근 overlap만 수집한다. 기준점이 없으면 기존 provider의 `5d/5m`, 그래도 부족하면 `1mo/5m`을 **해당 누락 종목에 한 번만** 확대 조회한다. 실패하면 비교 불가로 끝내며 무제한 재시도하지 않는다.
- 완료 일봉은 완료 세션·최종 수집 marker가 바뀔 때 갱신한다. 현행 공용 일봉 수집/확정 기능을 제거하지 않는다. 새 버튼이 매번 10년 bootstrap을 기다리지 않도록 연구용 준비 경로와 분리한다.
- 화면 기간 전환은 provider 호출 없이 Python이 준비한 두 window의 payload 중 하나를 선택한다.
- cache identity에 schema/rule version, 두 endpoint 값·시각, source 수정 marker, 누락 집합, calendar marker를 넣는다. 마지막 날짜만 같다는 이유로 수정 봉을 재사용하지 않는다.
- 앱을 닫아도 수집하는 scheduler, 자동 5분 refresh, 가격 알림은 이번 범위가 아니다. 관측 시각은 데이터가 최신인지 보여주며 계속 움직이는 가짜 live 시계를 두지 않는다.

## 해석 규칙

Python에서 계산한 사실만 조합한다. 임의 생성형 문장이나 단일 종합 점수, '신뢰도 80%'를 추가하지 않는다.

| 관측 | 사용자 표현 | 추가 확인 |
|---|---|---|
| ZN 하락 + 달러 대용지표 상승 | 금리·달러 부담과 들어맞는 조합 | ES/NQ와 YM/RTY 반응 |
| ZN 상승 + 달러 대용지표 하락 | 금리·환율 부담 완화와 들어맞는 조합 | 주가지수 동반 상승 여부 |
| 위 조합과 주식 반응이 반대 | 부담/완화와 주식 반응이 엇갈림 | 가격 조합의 변화 또는 주식 반응의 확산 |
| ES/NQ/YM/RTY 모두 같은 방향 | 관측한 네 지수가 동반 상승/하락 | 다음 관측에도 조합이 유지되는지 |
| 일부 지수만 같은 방향 | 어느 지수에서 관측됐는지 명시 | 보지 못한 지수까지 '시장 전체'로 확장하지 않음 |
| 마감 대비 상승, 최근 1시간 하락 | 상승분 일부 반납 | 마감 기준 대비 위치와 최근 변화 함께 확인 |
| 금/원유/구리 움직임 | 각 가격의 상승/하락 사실 | 가격만으로 경기 개선·공급 충격·인플레이션 확정 금지 |
| 공백·오래된 자료 | 현재 결합 해석 보류 | 자료가 맞춰진 뒤 다시 판단 |

한 window의 가격 부호만으로 '계속 강화', '급변 발생', '추세 전환'을 쓰지 않는다. '최근 1시간 하락'처럼 실제 측정 구간을 명시한다. 확산은 관측 대상 지수 수를 뜻하며 독립적인 확률 증거의 수가 아니다.

## 현재 값과 연구의 저장 경계

- 기존 `futures_macro_snapshot` / `futures_macro_forecast_history` 테이블 및 과거 행은 보존한다.
- 같은 snapshot 테이블의 새 key `overview_futures_macro_observation_v1`에 **현재 관측 전용** 결과를 저장한다. 별도 확률 history 행을 쓰지 않는다.
- 공용 `load_overview_futures_macro_materialized_snapshot()`는 새 observation key를 우선 읽고 기존 key를 호환 fallback으로 읽는다. fallback의 실제 기준일과 provenance를 유지한다. 포맷이 같다는 이유로 오래된 전망을 새로운 현재 관측과 합치지 않는다.
- legacy consumer용 payload는 `macro`, `pattern_outlook.current_pattern`과 metadata를 보존한다. `pattern_outlook.horizons=[]`, `research_status=NOT_COMPUTED`로 명시한다. `NOT_COMPUTED`를 `NO_EDGE` 또는 검증 통과로 표시하지 않는다.
- 기존 full materializer는 연구에서 명시 호출할 때만 남긴다. 공용 collector의 기본 attach도 경량 observation으로 변경하여 Data Operations 경유 갱신에서 무거운 검증이 되살아나지 않게 한다.
- writer는 기존 완료일보다 과거인 결과를 현재값으로 덮어쓰지 않는다. 새 계산 실패 시 마지막 유효 snapshot을 보존하되 실패와 freshness를 숨기지 않는다.

## 신규 모듈·인터페이스 계약

아래 경로와 이름은 개발 제안이다. 기존 함수인 것처럼 취급하지 않는다.

| 파일 | 책임 / 제공 인터페이스 |
|---|---|
| `app/services/futures_macro_observation_snapshot.py` | `build_observation_payload(*, macro: dict, current_pattern: dict, as_of_date: str, materialized_at: str) -> dict`; `materialize_futures_macro_observation_snapshot(*, evaluation_time: Optional[datetime] = None, force: bool = False) -> dict`. 기존 pure current builder만 사용 |
| `app/services/futures_macro_windows.py` | `normalize_closed_bars(rows: Sequence[Mapping], *, evaluation_time: datetime) -> list[dict]`; `build_window_returns(rows: Sequence[Mapping], *, symbols: Sequence[str], start_utc: datetime, end_utc: datetime) -> dict`; `build_futures_macro_window_snapshot(*, rows: Sequence[Mapping], evaluation_time: datetime, calendar: Mapping) -> dict` |
| `app/services/futures_macro_reading.py` | `build_futures_macro_change_reading(window: Mapping, *, companion_window: Optional[Mapping] = None) -> dict`. 해석·근거·반대 관측·다음 확인을 반환 |
| `app/services/overview/futures_macro.py` | `build_futures_macro_intraday_read_model(*, evaluation_time: Optional[datetime] = None) -> dict`. DB loader / calendar / cycle read model / window / reading 결합 |
| `app/jobs/futures_macro_refresh.py` | `run_futures_macro_observation_refresh(*, evaluation_time: Optional[datetime] = None) -> dict`. 범위 제한 수집→확정→관측 저장. 외부 JobResult는 기존 계약 유지 |

한국어 구현 주석/문서는 프로젝트 관례를 따른다. 위 표의 책임은 각각 장중 구간 계산, 해석, 조합, 실행이며 원시 provider fetch는 ingestion에 남긴다.

`normalize_closed_bars` 결과 필드: `provider_symbol`, aware UTC `bar_end_utc`, float `close`, 원본 `collected_at`. 중복 키에 상충 값이 있으면 조용히 임의 선택하지 않고 해당 관측을 제한한다.

`build_window_returns` 결과: `start_utc`, `end_utc`, `returns_pct: dict[str, float | None]`, `missing_symbols: list[str]`, `status: AVAILABLE | PARTIAL | UNAVAILABLE`. finite/positive 가격과 정확한 endpoint를 요구한다.

새 UI schema: `futures_macro_intraday_workbench_v1`.

```text
component: FuturesMacroWorkbench
schema_version: futures_macro_intraday_workbench_v1
generated_at_utc
cycle_background: {state_label, as_of_date, destination}
windows:
  since_close / last_hour:
    start_utc, end_utc
    status: AVAILABLE | PARTIAL | STALE | MARKET_CLOSED | UNAVAILABLE
    prices: [{key, label, return_pct, status, source_symbols}]
    reading: {headline, observation_facts, interpretation, counter_evidence, next_checks}
    evidence: {missing_symbols, source, rule_version, caveats}
research: {status: NOT_VALIDATED, scope: intraday_windows}
command: existing Python-dispatch actions + actual pending result state
action_boundary: python_dispatch_only
```

표시에 사용하지 않는 v7 horizon/map/ribbon/pathway를 새 payload에 넣지 않는다. 새 schema는 observation status와 research status를 분리한다.

## 이번 5단계의 종료 조건과 다음 확장

종료 조건은 사용자가 두 시점의 실제 가격 차이와 해석 범위를 이해하고, 갱신 후 새 관측을 확인하며, 오래된 자료를 현재값으로 오해하지 않는 것이다. 매수·매도 신호 또는 향후 방향 확률을 만드는 것이 종료 조건은 아니다.

접힌 과거 항목에는 '장중 조건 검증 전'과 검증 범위만 표시한다. 기존 일봉 5D 사례 수를 장중 조건에 전용하지 않는다. 장기간 같은 시간대의 과거 자료를 확보하고 episode·target·holdout을 고정하는 연구는 별도 후속 후보다. 현재 2일 수집 범위나 UI 구성만으로 그 연구가 완료됐다고 하지 않는다.
