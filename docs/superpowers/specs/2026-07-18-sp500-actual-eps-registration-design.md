# S&P 500 실제 TTM EPS 등록 설계

## 목적

경제 사이클의 `실제 TTM EPS`가 자료 부족으로 남는 원인은 계산 로직이 아니라
`finance_meta.sp500_index_earnings`에 공식 완료 분기 EPS가 없기 때문이다. S&P 공식
`Index Earnings` XLSX는 공개 페이지에 연결되어 있지만 서버와 브라우저의 직접
접근이 `403 / Access Denied`로 차단되므로 이를 우회해 자동 수집하지 않는다.

사용자가 공식 파일을 내려받아 앱에 등록하면 원본을 검증·정규화·저장하고, 완료된
실제 As-Reported 분기 8개가 확보되는 즉시 경제 사이클이 current/prior TTM과 전년
대비 변화를 계산하도록 한다.

## 선택한 접근

### A. 공식 파일 등록 — 선택

- `Workspace > Ingestion`에서 공식 S&P Index Earnings XLSX와 자료 발표일을 등록한다.
- 앱이 원본 workbook을 읽고 실제/추정, 분기, As-Reported/Operating 구분을 보존한다.
- DB에는 공식 원천 URL과 release vintage를 저장한다.
- 경제 사이클의 `실제 TTM EPS` 명칭을 그대로 유지할 수 있다.

### B. 환경변수·로컬 경로 운영 — 보조 호환

기존 `SP500_INDEX_EARNINGS_*` 경로는 자동화 runner 호환을 위해 유지한다. 다만 일반
사용자의 주 사용 흐름으로 두지 않는다.

### C. Shiller EPS를 실제 EPS로 대체 — 제외

Shiller의 월별 보간 TTM EPS는 S&P 공식 완료 분기 actual과 의미가 다르다. 가치평가
fallback으로는 유지하지만 경제 사이클의 `실제 TTM EPS`에 넣거나 실제 자료처럼
표시하지 않는다.

## 사용자 흐름

1. 사용자가 S&P 500 공식 페이지에서 `Index Earnings` XLSX를 내려받는다.
2. `Workspace > Ingestion > S&P 500 가치평가 자료`에서 파일을 선택한다.
3. 자료 발표일을 입력하고 `실제 EPS 반영`을 실행한다.
4. 앱은 파일 형식, 공식 workbook 표식, EPS basis/status/period를 검증한다.
5. 유효한 행을 release vintage 단위로 idempotent UPSERT한다.
6. 결과는 `반영한 실제 분기`, `가장 최근 완료 분기`, `경제 사이클 판정까지 필요한
   잔여 분기` 중심으로 보여준다. raw job/row 진단을 첫 화면의 주인공으로 만들지 않는다.
7. 경제 사이클을 다시 열면 8개 완료 분기가 있을 때 `실제 TTM EPS`가 자동 활성화된다.

## 아키텍처와 책임

```text
S&P 공식 Index Earnings XLSX
  -> Ingestion file registration
  -> official workbook parser / validator
  -> normalized release-vintage rows
  -> finance_meta.sp500_index_earnings
  -> finance/loaders/sp500_valuation.py
  -> finance/economic_cycle_asset_pathways.py
  -> Overview Economic Cycle
```

- `finance/data/sp500_valuation.py`
  - 공식 workbook sheet/header 탐색과 명시적 actual/as-reported 분기 추출을 담당한다.
  - 기존 normalized workbook 입력도 하위 호환으로 유지한다.
  - 색상이나 셀 위치만으로 actual/estimate를 추론하지 않는다.
- `finance/data/db/schema.py`
  - 기존 vintage unique key를 유지한다. 새 테이블이나 typed EPS 수기 입력은 추가하지
    않는다.
- `finance/loaders/sp500_valuation.py`
  - `period_end <= as_of_date`와 함께 `source_release_date <= as_of_date`를 적용해
    historical read에서 미래 발표치를 읽지 않도록 한다.
  - 같은 분기 여러 vintage 중 해당 기준일에 알려진 최신 release만 선택한다.
- `app/jobs/ingestion_jobs.py`
  - 파일 등록을 기존 canonical importer에 연결하고 사용자용 coverage summary를 만든다.
- `app/web/ingestion/sections.py`
  - 업로드, 발표일, 반영 버튼과 의미 중심 결과를 제공한다.
  - Overview 렌더 경로에서 외부 파일이나 provider를 직접 읽지 않는다.

## 데이터 계약

저장 대상은 다음 조건을 모두 만족하는 행이다.

- 공식 S&P 500 Index Earnings 자료에서 읽은 값
- `period_type = quarterly`
- `earnings_basis = as_reported` 또는 `operating`으로 명시된 값
- `value_status = actual | estimate | mixed`로 명시된 값
- 유효한 `period_end`, `source_release_date`, 양의 EPS

경제 사이클은 이 중 `quarterly + as_reported + actual + eps > 0`만 사용한다. 서로 다른
완료 분기 8개로 최근 4분기 TTM과 이전 4분기 TTM을 만들고 전년 대비 변화율을
계산한다. 추정치, mixed, Operating EPS, Shiller proxy는 이 계산에 섞지 않는다.

## 원천과 파일 처리

- canonical `source`는 `sp_dow_jones_index_earnings`를 유지한다.
- `source_ref`는 로컬 임시 경로가 아니라 공식 Index Earnings URL을 저장한다.
- 업로드 파일은 메모리 또는 작업용 임시 파일로만 처리하고 등록 후 제거한다.
- 파일명만으로 공식 자료라고 신뢰하지 않는다. workbook 내부의 예상 sheet/header 및
  명시적 열을 검증한다.
- 자료 발표일은 사용자가 입력하되 workbook 안에서 확인 가능한 날짜와 충돌하면
  저장을 중단하고 차이를 안내한다.

## 오류 처리

- XLSX가 아니거나 workbook을 열 수 없음: 저장하지 않고 파일 형식을 안내한다.
- 공식 구조를 확인할 수 없음: 정규화 추론을 하지 않고 지원되는 열/시트를 안내한다.
- actual/as-reported 분기가 없음: estimate를 actual로 승격하지 않고 자료 상태를 설명한다.
- 유효 분기가 8개 미만: 저장은 수행하되 `n/8개 확보`로 남긴다.
- 동일 vintage 재등록: unique key UPSERT로 중복을 만들지 않는다.
- DB 실패: 부분 성공으로 표시하지 않고 transaction 단위로 롤백한다.

## 테스트와 완료 조건

### 단위 테스트

- 공식 workbook 형태 fixture에서 actual/as-reported 분기와 estimate를 구분한다.
- normalized workbook 하위 호환을 검증한다.
- 잘못된 sheet/header/date 충돌은 저장 전에 실패한다.
- 같은 vintage 재등록이 idempotent함을 검증한다.
- historical `end_date` 이후 발표된 vintage가 loader 결과에서 제외되는지 검증한다.
- 7개 분기는 `INSUFFICIENT_HISTORY`, 8개 분기는 `READY`가 되는지 검증한다.

### 통합·브라우저 QA

- Ingestion에서 파일 선택 → 발표일 → 반영 흐름이 동작한다.
- 완료 후 경제 사이클의 실제 TTM EPS 경로가 별도 수기 입력 없이 갱신된다.
- 오류·부분 coverage 문구가 actual과 proxy를 혼동시키지 않는다.

### 완료 조건

- 공식 파일의 완료 actual/as-reported 분기 8개가 DB에 저장된다.
- current/prior TTM EPS와 전년 대비 변화가 계산된다.
- point-in-time 기준일 이후 release는 읽지 않는다.
- 관련 focused test, 전체 영향 회귀, Browser QA가 통과한다.
- 데이터 흐름과 테이블 의미 문서가 현재 구현과 일치한다.

## 범위 밖

- S&P의 접근 제한 우회 또는 무인 scraping
- S&P/Capital IQ 유료 계정·API 연동
- 개별 구성 종목 EDGAR 자료로 공식 index EPS 재구성
- Shiller proxy를 공식 실제 EPS로 재분류
- 경제 사이클 모델 확률이나 다른 자산 경로 변경
