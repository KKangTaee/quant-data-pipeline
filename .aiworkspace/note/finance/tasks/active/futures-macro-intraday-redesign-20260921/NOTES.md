# 확인한 사실과 결정

Date: 2026-09-21

## 기존 코드에서 확인

- `materialize_overview_futures_macro_snapshot()`는 thermometer의 `include_validation=False`와 별개로 pattern outlook 전체 검증을 호출한다.
- `run_overview_futures_daily_ohlcv()`는 routine 1y / 부족 종목 10y 일봉, active session의 2d/5m, finalization 후 materialization을 수행한다.
- `attach_futures_macro_materialization()`의 default도 같은 full materializer다. Overview 버튼만 고치면 다른 ingestion 진입에서 병목이 재발할 수 있다.
- `app/web/today_page.py`와 `app/services/portfolio_monitoring/macro_context.py`가 materialized snapshot을 공유한다. Monitoring은 current family 5D/20D와 별도 horizons를 읽는다.
- 현재 React root는 ShortHorizonDecision / MarketRepricing / FamilyDirection / PatternRibbon / Method / CalculationTrace를 렌더한다. viewport에서 숨긴 미래 type/map/pathway 계약도 큰 root type에 남아 있다.
- 기존 `today_market_session.py`는 timezone·휴장·조기폐장 계산이 있지만 generated_at 이후 schedule을 만든다. 직전 close 조회에는 과거 범위 adapter가 필요하다.
- `load_stored_futures_intraday_rows()`는 정확한 half-open UTC 범위를 읽지만 data-layer 파일에 있다. 재사용하거나 loader 경계로 옮길 때 finalization consumer를 보존한다.
- 원시 수집 universe는 17개이며 `DX-Y.NYB`를 포함한다. 새 달러 대용지표와 DXY를 같은 시계열로 표시하지 않는다.

## 설계 결정

- 전체 5차: cleanup / windows / reading / UI / integration.
- cleanup은 runtime 실행 분리 먼저, 미사용 파일 삭제는 UI 교체 후.
- snapshot의 current/history 결합을 그대로 재사용해 빈 forecast history를 추가하지 않는다. 새 observation key와 호환 reader를 둔다.
- 새 기본 구간은 since-close / last-hour. 과거 5D 전망은 제품 주 경로에서 분리.
- 확률·수익률 전망 연구는 별도 후속 후보. 기존 M2 연구 결함을 이번 관측 개편의 blocker로 만들지 않는다.
- 갱신은 명시적 클릭을 유지한다. '23시간 시장'을 '앱이 자동으로 23시간 수집 중'이라는 약속으로 바꾸지 않는다.

## 이전 자료의 적용 범위

선행 pilot은 한 일봉 조건의 5D target 검증이며 장중 1시간·마감 이후 구간의 예측력을 검증한 것이 아니다. 시안이 좋다는 사용자 응답은 실제 데이터 결과 승인이나 구현 시작 요청이 아니다.

- 2차: DB 입력 조합은 작은 futures_macro_inputs.py로 분리. calendar 연간 collection coverage를 사용하며 Today의 calendar 판단은 바꾸지 않음. 전용 loader는 32일 상한, 실제 read는 16일.
