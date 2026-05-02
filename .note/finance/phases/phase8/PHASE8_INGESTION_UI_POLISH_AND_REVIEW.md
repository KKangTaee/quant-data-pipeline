# Phase 8 Ingestion UI Polish And Review

## Summary

이번 정리는 `Ingestion` 화면을 더 덜 복잡하고, 운영 관점에서 더 읽기 쉽게 만드는 데 목적이 있었다.

핵심 변경:

- 상단 `Write Targets` 표 제거
- 각 실행 카드를 expander로 전환
- `Recent Logs` / `Failure CSV Preview` 동작 상태 점검

## Implemented UI Changes

### 1. `Write Targets` 제거

기존 상단 `Write Targets` 표는 삭제했다.

이유:

- 각 실행 카드 안에 이미 `Writes to:` 설명이 존재
- 같은 정보를 화면 상단에서 한 번 더 반복하고 있었음
- 화면을 길게 만들고 핵심 실행 버튼까지 내려가야 했음

따라서 현재는:

- write target은 각 카드 안에서만 설명
- 상단은 실행 중심으로 단순화

### 2. Run Jobs expander화

운영 / 수동 탭 안의 실행 카드들은 이제 expander로 관리한다.

운영 탭:

- `Daily Market Update`
- `Weekly Fundamental Refresh`
- `Extended Statement Refresh`
- `Metadata Refresh`

수동 / 진단 탭:

- `Core Market Data Pipeline`
- `OHLCV Collection`
- `Fundamentals Ingestion`
- `Factor Calculation`
- `Asset Profile Collection`
- `Financial Statement Ingestion`
- `Price Stale Diagnosis`
- `Statement PIT Inspection`

효과:

- 화면이 한 번에 덜 펼쳐짐
- 필요한 카드만 열어서 사용 가능
- run button과 입력값을 job 단위로 집중해서 볼 수 있음

## Review: Recent Logs

### Current behavior

`Recent Logs`는 정상 동작한다.

현재 구현:

- `logs/` 아래 최신 `*.log` 5개 탐색
- 선택한 파일의 마지막 20줄 표시

실제 확인:

- 최신 log 파일이 정상적으로 잡힘
  - `factors_errors_20260329.log`
  - `fundamentals_errors_20260329.log`
  - `financial_statements_errors_20260329.log`
- tail preview도 정상 출력 가능

### Assessment

- **유지 가치 있음**
- 운영자가 최근 실패/에러 흔적을 빠르게 보는 용도로 유용

### Future improvements

- job type filter
- line count selector
- full file download/open
- selected run과 연동된 로그 하이라이트

## Review: Failure CSV Preview

### Current behavior

`Failure CSV Preview`도 기술적으로는 정상 동작한다.

현재 구현:

- `csv/` 아래 `*failures*.csv` 5개 탐색
- 선택한 CSV를 DataFrame으로 미리보기

실제 확인:

- 현재 발견된 파일은 주로 legacy profile failure CSV
  - `nyse_profile_failures_20260206.csv`
  - `nyse_profile_failures_20260204.csv`
- 샘플 파일은 정상적으로 읽힘

### Assessment

- **기능은 동작하지만 현재 운영 가치가 낮음**

이유:

- 최근 주요 ingestion job들이 일관되게 failure CSV를 남기지 않음
- 그래서 패널은 살아 있지만, 최신 운영 문제를 반영하는 artifact가 많지 않음

### Recommendation

현재는 제거보다는 유지가 낫다. 다만 설명이 필요하다.

- 이미 UI caption으로
  - 모든 modern job이 failure CSV를 만들지는 않음
  을 명시

중장기적으로는 둘 중 하나가 맞다.

1. failure CSV emission을 job 전반에 표준화
2. 그렇지 않으면 이 패널을 de-emphasize 또는 교체

## Additional Recommended Features

### 1. Build / Runtime Version Indicator

최근 이슈에서 가장 크게 드러난 문제는:

- 코드가 고쳐졌더라도
- 실행 중인 Streamlit 프로세스가 옛 경로를 타면
- 사용자가 같은 버튼을 눌러도 기대와 다른 결과를 보는 점

추천:

- `Ingestion` 또는 앱 상단에
  - current runtime marker
  - recent reload timestamp
  - optional git commit short SHA
  를 표시

이건 운영 혼선을 크게 줄여줄 가능성이 높다.

### 2. Statement Shadow Rebuild Only Helper

현재 `raw_statement_present_but_shadow_missing` 케이스가 많다.

현 시점엔 `Extended Statement Refresh`를 다시 돌리는 것이 맞지만,
실제로는 raw collection보다 shadow rebuild만 필요한 경우가 많다.

추천:

- `Shadow Rebuild Only`
  - fundamentals shadow rebuild
  - factors shadow rebuild
  만 실행하는 operator helper 검토

### 3. Failure Artifact Standardization

`Failure CSV Preview`를 계속 유지하려면,
주요 job이 failure artifact를 비슷한 형식으로 남겨야 한다.

추천:

- OHLCV
- statement ingestion
- fundamentals
- factors

에 대해 CSV or JSON failure artifact 정책을 통일

### 4. Run Result Deep Link

현재 `Latest Completed Run`과 `Persistent Run History`는 유용하지만,
특정 run의

- 입력값
- step breakdown
- related logs
- related payload

를 더 빠르게 연결해주면 운영성이 좋아진다.

## Recommendation

현재 기준으로는 다음 판단이 가장 적절하다.

- `Write Targets` 제거: 적절
- expander 기반 단순화: 적절
- `Recent Logs`: 유지 가치 높음
- `Failure CSV Preview`: 기술적으로는 정상, 그러나 운영 가치는 현재 제한적

다음 우선순위는:

1. runtime/build indicator
2. shadow rebuild only helper
3. failure artifact standardization

