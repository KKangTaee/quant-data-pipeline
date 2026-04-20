# Finance Data Architecture

## 목적

이 폴더는 finance 프로젝트의 데이터 흐름, DB 구조, 테이블 의미, 데이터 품질/PIT 주의사항을 관리한다.
`FINANCE_COMPREHENSIVE_ANALYSIS.md`에는 상위 요약만 남기고,
DB와 데이터 의미의 상세 기준은 이 폴더에서 관리한다.

## 읽는 순서

| 상황 | 먼저 볼 문서 |
|---|---|
| 데이터가 어디서 와서 어디로 저장되는지 확인 | `DATA_FLOW_MAP.md` |
| DB와 table 목록을 빠르게 확인 | `DB_SCHEMA_MAP.md` |
| table별 의미와 source / derived / shadow 성격 확인 | `TABLE_SEMANTICS.md` |
| PIT, look-ahead, survivorship, stale data 위험 확인 | `DATA_QUALITY_AND_PIT_NOTES.md` |

## `code_analysis/`와의 차이

- `code_analysis/`는 코드를 어떻게 따라가고 수정할지 보는 개발자 flow 문서다.
- `data_architecture/`는 데이터가 어떤 의미를 갖고 어디에 저장되는지 보는 data / DB 의미 문서다.

예를 들어 새 loader 함수를 고칠 때는 `code_analysis/DATA_DB_PIPELINE_FLOW.md`를 먼저 보고,
그 loader가 읽는 table의 의미를 확인할 때는 이 폴더의 `TABLE_SEMANTICS.md`를 본다.

## 갱신해야 하는 경우

- 새 DB table / column이 추가될 때
- table의 source / derived / shadow / convenience 성격이 바뀔 때
- ingestion source가 바뀔 때
- loader가 source of truth를 바꿀 때
- PIT 기준, filing timing, period_end 의미가 바뀔 때
- provider coverage, stale data, survivorship risk 해석이 바뀔 때

## 갱신하지 않아도 되는 경우

- 단순 UI 문구 변경
- 일회성 backtest 결과
- phase status 변경
- 코드 내부 리팩터링이 table 의미나 데이터 흐름을 바꾸지 않는 경우

## Source Of Truth

schema의 실제 정의는 코드가 기준이다.

- `finance/data/db/schema.py`

이 폴더는 schema SQL을 그대로 복제하는 곳이 아니라,
사람과 agent가 데이터 의미를 빠르게 이해하도록 돕는 해석 지도다.
