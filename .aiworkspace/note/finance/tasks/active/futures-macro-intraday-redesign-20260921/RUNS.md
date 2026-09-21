# 계획 작성 확인 기록

Date: 2026-09-21

- 읽은 entry: INDEX / PRODUCT_DIRECTION / ROADMAP / PROJECT_MAP, 기존 성능·가치 research와 시안.
- 분류: 시안 동의 후 구현 전 개발 계획 작성. finance-task-intake / writing-plans 적용.
- read-only 코드 확인: snapshot/full outlook 호출, ingestion attach, daily/intraday refresh와 finalization, 공용 Today/Monitoring reader, React root·package scripts, 시장 calendar와 DB loader.
- repository 상태: 실제 branch `master`, 기존 user-generated untracked PNG 4개 보존.
- 검색 중 존재하지 않는 `scripts/` 경로에 대한 rg 경고가 있었으며 해당 경로에 의존하는 계획은 만들지 않았다.
- 문서 확인: task 6개와 recommendation의 local link, 미완성 placeholder, normalized status, 정확히 5개 개발 단계 검사 PASS. 인터페이스와 UI/연구 schema 경계를 자기 검토했다.
- `git diff --check` PASS. staging 이후 신규 문서를 포함한 `git diff --cached --check`도 커밋 전에 확인한다.
- 앱 테스트/빌드/실제 수집/DB 변경/Browser QA는 실행하지 않음. 변경은 계획 문서뿐이다.

## 1차 구현

- 새 관측 테스트 RED 5 failures → 관련 GREEN 122 passed / 2 subtests. 외부 edgartools 경고 3개는 기존 baseline과 동일.
- 실제 저장자료 observation 계산 0.493초, 2026-09-18 기준. write_fn capture로 운영 snapshot 미변경.
- 실제 MySQL monotonic UPSERT: 과거 날짜·같은 날짜의 이전 계산 결과 덮어쓰기 방지 PASS. 고유 test key는 transaction rollback으로 제거. forecast history 변경 없음.

## 2차
- 신규 경계 테스트 RED 19개 → 구현 후 GREEN. calendar 누락 시 가격 backfill을 하지 않는 RED 추가 후 수정.
- windows/refresh/intraday/session/finalization/shared refresh: 73 passed (기존 edgar 경고 3개).
- 실제 DB read 0.046초, 공식 calendar CONFIRMED. 저장 관측 2026-09-21 00:00 UTC는 STALE로 판정.

## 3차
- 해석/read model RED 8개 → GREEN. windows 포함 26 passed.
- 부담/완화와 주가 엇갈림, 중립 표시, stale/partial 보류, 같은 cutoff 상승분 반납, 수정값/누락/rule 변경 identity 확인.

## 4차
- UI action RED 2개 → GREEN. 재전송 nonce 억제, 오류 후 unlock, reload는 수집 미실행, fallback AppTest 기간 전환 포함 신규 32 passed.
- 유지되는 service futures 계약 35 passed. 원본 master에서도 실패하는 기존 thermometer 테스트 3개는 동일 재현하여 범위 밖 baseline으로 분류. 구 v3/v7 화면 전용 계약 29개/구 short-horizon 화면 테스트는 새 관측 계약으로 교체. 공유 일별 session 통합 테스트는 보존.
- React 18 type 의존성을 devDependencies에 추가, tsc --noEmit 및 Vite production build 통과. 제품 component_static 산출물 갱신.
- Browser: 두 기간 전환 시 시각·가격 함께 변경. 실제 refresh 동안 두 버튼 disabled, 실제 ack 후 unlock. 420px frame 377px = scroll 377px, 900/1400px 추가 확인.
- 실제 refresh JobResult: success 6.846초, 2d/5m 수집 6.592초 1회, observation 재사용 0.123초. baseline 70.567초는 무거운 계산 포함 이전 관측이며 동일 네트워크/입력의 엄밀한 benchmark는 아님.
- 콘솔의 overview/_stcore 경로 404 두 건은 Streamlit 초기 경로 탐색이며 앱 정상 연결됨. 새 컴포넌트 JS 오류 없음.

## 5차 최종 검증

- 신규 오류 경계 RED 3개 → GREEN: 손상된 observation JSON은 구 key의 실제 날짜로 fallback; materializer unavailable은 전체 성공 표시 금지; DB 읽기 실패 시 마지막 관측/시각 유지·결합 해석 보류.
- 독립 전체 branch 리뷰: P2 두 건. 토요일의 오래된 complete endpoint는 missing=[]여서 수집이 전혀 실행되지 않는 경우, 보조 자산 GC의 마감 endpoint 누락이 CORE-only missing에서 사라지는 경우를 순수 fixture로 재현했다. RED 2개 후 recent needs_recent guard와 별도 backfill_symbols로 수정. 가격 자료 전체의 보강 목록과 결합 해석의 핵심 누락을 분리했다.
- 최종 focused regression: **194 passed, 2 subtests passed**, 기존 edgar deprecation warning 3개. 유지 service-contract futures subset **35 passed**.
- 원본 master 재현: 기존 `test_macro_thermometer_detects_rate_pressure_scenario`, `test_macro_thermometer_inverts_rates_and_fx_pressure`, `test_macro_thermometer_snapshot_exposes_current_evidence_counts` 3개가 동일 실패. 새 장중 경로의 회귀와 분리하며 전체 저장소 테스트 전부 통과로 주장하지 않는다.
- 동일 DB 자료 current 강제 read/compute/write 3회: **0.4470 / 0.4388 / 0.4365초**. 표시 read model 3회 **0.1319 / 0.0466 / 0.0521초**. forecast_history count **23→23**으로 증가 없음.
- 수집 포함 actual JobResult: **6.846초**, recent 2d/5m 요청 1회 **6.592초**, current 재사용 **0.123초**. 두 구간 AVAILABLE, 완료 일별 기준일 2026-09-18, 진행 중 2026-09-21은 settlement cutoff 전이라 finalization not_due. 옛 70.567초와 네트워크·입력 상태가 다르므로 엄밀한 배율 개선으로 표현하지 않는다.
- Browser QA: 실제 버튼→disabled→결과 ack→unlock; period 변경으로 시각/가격 변경; 저장 자료 다시 읽기; 경기국면 원래 route 이동; stale/available 실제 자료. PARTIAL/UNAVAILABLE/휴장/실패/중복은 deterministic 테스트. fallback AppTest 동일 구간/실패시 마지막 관측 확인.
- viewport 420/900/1400 검산, frame 377/729/1229에서 각각 scrollWidth와 일치. 최종 screenshot: `/Users/taeho/Project/quant-data-pipeline/.playwright-mcp/futures-macro-final-qa.png` (generated, 미커밋).
- `tsc --noEmit`, Vite production build, `git diff --check` 통과. 제거된 component import는 production에서 없음. 제품 배포에 필요한 tracked component_static만 갱신했고 registry/saved/run history/user PNG는 변경하지 않음.
- canonical docs: PRODUCT_DIRECTION/PROJECT_MAP/ROADMAP/data 흐름·schema 의미 갱신. INDEX 탐색 구조와 별도 runbook 절차는 변하지 않아 변경 없음. 로컬 master는 시작 SHA 그대로이며 충돌 없는 fast-forward 가능 확인.
