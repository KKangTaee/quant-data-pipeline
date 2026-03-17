# Phase 2 Current Chapter TODO

## 목적
이 문서는 현재 진행 중인 PHASE2 작업을
실행 가능한 큰 TODO와 세부 체크 항목으로 관리하기 위한 작업 보드다.

앞으로는 이 문서를 기준으로
- `pending`
- `in_progress`
- `completed`
상태를 갱신하면서 작업을 진행한다.

상위 계획 문서:
- `.note/finance/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`

---

## 현재 챕터 범위

현재 챕터의 목표:

1. 운영 파이프라인 구조를 실사용 기준으로 정리
2. 실행 이력을 운영/분석에 쓸 수 있을 정도로 강화
3. 설정 외부화 착수 전 준비를 끝낸다

---

## 큰 TODO 보드

### A. 운영 파이프라인 정리
상태:
- `completed`

세부 작업:
- `[completed]` Operational Pipelines 섹션 추가
  - routine execution용 상위 버튼 영역을 만들어 manual job과 역할을 분리
- `[completed]` Daily Market Update 추가
  - daily price refresh를 하나의 운영 버튼으로 실행 가능하게 정리
- `[completed]` Weekly Fundamental Refresh 추가
  - fundamentals + factors를 주간 운영 단위로 묶어 실행 가능하게 정리
- `[completed]` Extended Statement Refresh 추가
  - detailed financial statements를 장기 이력 확보용 운영 버튼으로 분리
- `[completed]` Metadata Refresh 추가
  - asset profile 갱신을 별도 운영 단위로 분리
- `[completed]` Extended Statement Refresh에서 `freq`와 `period type` 자동 정렬
  - 의미가 충돌하는 입력 조합이 나오지 않도록 파라미터를 단순화
- `[completed]` 각 파이프라인에 권장 사용 주기 문구 추가
  - daily / weekly / extended / metadata를 언제 눌러야 하는지 화면에 명시
- `[completed]` 각 파이프라인에 권장 symbol source 문구 추가
  - manual, NYSE, filtered universe 중 어떤 source가 기본인지 안내
- `[completed]` 운영 파이프라인과 manual jobs의 역할 차이를 UI에 더 명확히 표시
  - 운영 버튼은 routine use, manual jobs는 예외/세부 제어용이라는 점을 분명히 표시
- `[completed]` 기본값 재검토
  - period, freq, source default가 실제 운영 습관과 맞는지 조정

완료 기준:
- 운영자가 daily / weekly / extended / metadata 목적별 버튼을 바로 구분할 수 있어야 함
- manual job은 예외/세부 제어용이라는 점이 분명해야 함

---

### B. 실행 이력 고도화
상태:
- `completed`

세부 작업:
- `[completed]` `run_metadata` 기본 구조 추가
  - 결과 dict 밖에 실행 컨텍스트를 붙일 수 있는 공통 저장 공간 마련
- `[completed]` symbol source 저장 시작
  - manual / NYSE / filtered source 구분이 이력에 남도록 연결
- `[completed]` symbol count 저장 시작
  - 실행 규모를 나중에 이력만 보고도 판단할 수 있게 저장
- `[completed]` 핵심 input params 저장 시작
  - period, interval, freq 같은 주요 실행 조건을 남기기 시작
- `[completed]` UI history에 symbol source 표시 시작
  - 최근 실행과 영속 이력 테이블에서 source를 바로 볼 수 있게 표시
- `[completed]` `pipeline_type` 저장
  - daily / weekly / extended / metadata / manual 성격을 명시적으로 남김
- `[completed]` `execution_mode` 저장
  - operational pipeline에서 실행했는지 manual job에서 실행했는지 구분
- `[completed]` `notes` 또는 `execution_context` 저장
  - 왜 이 job을 돌렸는지 또는 어떤 맥락의 실행인지 짧게 남길 수 있게 준비
- `[completed]` Persistent Run History 표에 위 필드 반영
  - 저장만 하지 말고 UI에서도 바로 읽을 수 있게 표시
- `[completed]` JSONL 예시 기준으로 이력 스키마 점검
  - 실제 누적된 히스토리를 기준으로 누락/중복 필드가 없는지 확인

완료 기준:
- history 한 줄만 보고도
  - 어떤 job인지
  - operational인지 manual인지
  - 어떤 symbol source인지
  - 어떤 입력으로 돌렸는지
  - 어떤 파이프라인 성격인지
  알 수 있어야 함

---

### C. 설정 외부화 준비
상태:
- `in_progress`

세부 작업:
- `[completed]` 현재 하드코딩 상수 목록 추출
  - 어떤 값들이 코드 안에 박혀 있는지 먼저 inventory 작성
- `[completed]` 외부화 우선순위 분류
  - 꼭 먼저 뺄 값과 나중에 빼도 되는 값을 구분
- `[pending]` 설정 파일 경로 확정
  - 설정 파일을 어디에 둘지 프로젝트 규칙 확정
- `[pending]` 설정 파일 포맷 초안 작성
  - TOML/YAML/JSON 중 어떤 형태로 읽고 관리할지 정리

후보 항목:
- DB 접속 정보
- symbol preset
- 기본 symbol source
- warning threshold
- progress threshold
- 기본 period / freq
- chunk size

완료 기준:
- 다음 단계에서 바로 설정 파일을 도입할 수 있을 정도로 정리되어야 함

---

### D. 백테스트 준비 메모 정리
상태:
- `pending`

세부 작업:
- `[completed]` detailed financial statement tables를 first-class raw ledger로 취급한다는 전제 기록
  - 요약 fundamentals/factors보다 더 긴 과거 이력과 세부 계정 확보용 원장이라는 점 명시
- `[pending]` loader 계층 초안 함수 목록 정의
  - 어떤 loader가 필요하고 함수 이름을 어떻게 잡을지 초안 작성
- `[pending]` price / fundamentals / factors / detailed statements / universe loader 입력 계약 정리
  - symbols, start/end, freq, source 같은 입력 규격을 통일
- `[pending]` point-in-time 주의사항을 loader 설계 항목으로 분리
  - 룩어헤드 방지와 공시 시점 반영을 loader 설계에서 빠뜨리지 않도록 분리

완료 기준:
- loader 구현 전에 필요한 설계 기준이 문서화되어 있어야 함

---

## 현재 추천 다음 작업 순서

1. A-7 운영 파이프라인 권장 사용 주기 문구 추가
2. A-8 권장 symbol source 문구 추가
3. A-9 운영 파이프라인과 manual jobs 역할 차이 명시
4. C-1 하드코딩 상수 목록 추출

---

## 현재 작업 중 항목

현재 `in_progress`:
- `C. 설정 외부화 준비`

바로 다음 체크 대상:
- `C-3 설정 파일 경로 확정`

---

## 현재 진척도

- PHASE2 전체:
  - 약 `46%`

- 현재 챕터:
  - 약 `79%`

판단 근거:
- 운영 파이프라인 정리는 현재 챕터 기준으로 완료
- 실행 이력 고도화는 현재 챕터 기준으로 완료
- 설정 외부화 준비가 시작되었고 inventory가 작성됨
