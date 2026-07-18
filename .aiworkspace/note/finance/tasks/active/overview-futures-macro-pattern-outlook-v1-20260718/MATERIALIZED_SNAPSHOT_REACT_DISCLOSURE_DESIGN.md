# Futures Macro Materialized Snapshot And React Disclosure Design

## 이걸 하는 이유?

현재 `Workspace > Overview > Futures Macro` 첫 진입은 저장된 5년 일봉을 읽은 뒤
현재 매크로 snapshot과 5D·20D pattern outlook을 process 안에서 다시 계산한다.
동일 process 안의 재진입은 빠르지만 서버 재시작이나 cache 만료 뒤에는 계산이 반복되어
사용자가 탭을 여는 행위가 수 초짜리 분석 job처럼 동작한다.

또한 React의 `방법론과 품질` disclosure는 닫힌 상태에서 측정된 Streamlit component
iframe 높이를 연 뒤 다시 동기화하지 않아 내용이 iframe 아래에서 잘린다.
그 다음 `원본 데이터 / 계산 추적`은 별도 Streamlit expander라서 같은 화면 안에서
테두리, 여백, 열림 상태와 높이 처리 방식이 서로 다르다.

이번 마무리는 계산식이나 publication gate를 바꾸지 않고,
비싼 계산을 일봉 ingestion 뒤로 이동하고 두 상세 영역을 하나의 React 시각 언어로 통일한다.

## 승인된 사용자 흐름

### 일봉 갱신

1. 사용자가 기존 `일봉 갱신`을 누른다.
2. 기존 core 16개 선물 `5y / 1d` 수집을 실행한다.
3. 수집된 core daily source marker가 저장 snapshot marker와 다를 때만
   현재 매크로와 5D·20D 조건부 전망을 계산한다.
4. 화면에 필요한 compact snapshot을 DB에 UPSERT한다.
5. 갱신 결과와 새 snapshot을 다시 읽어 React 화면을 표시한다.

별도의 `전망 수정`, `전망 재계산` 버튼은 만들지 않는다.
`다시 읽기`는 provider 수집이나 전망 계산을 실행하지 않고 저장 snapshot만 다시 읽는다.

### 평상시 탭 진입

1. 탭은 latest compact snapshot 한 행만 DB에서 읽는다.
2. 저장된 현재 맥락, 5D·20D 전망, 원본 계산 추적을 React payload로 바꾼다.
3. 5년 OHLCV와 pattern replay를 탭 render 중 다시 계산하지 않는다.

snapshot이 없거나 schema / algorithm version이 현재 코드와 다르면
탭 진입 중 fallback 계산을 하지 않는다. React hero와 command 영역에서
`일봉 갱신이 필요합니다`를 보여주고 기존 `일봉 갱신` action을 제공한다.

## 저장 계약

### Table

`finance_meta.futures_macro_snapshot`

- `snapshot_key`: current Overview snapshot의 안정 key
- `source_marker`: core futures latest `1d` candle marker
- `as_of_date`: 화면 자료 기준일
- `schema_version`: persisted payload 구조 version
- `algorithm_version`: pattern outlook 계산 version
- `status`: `READY | LIMITED | ERROR`
- `snapshot_json`: UI가 필요로 하는 compact current-macro + pattern-outlook payload
- `materialized_at`: 실제 계산·저장 시각
- `created_at`, `updated_at`

`snapshot_key`는 unique key이고 동일 source marker의 반복 실행은 idempotent하다.
source marker가 바뀌지 않았고 schema / algorithm version도 같으면 기존 row를 재사용한다.

### Compact payload

저장한다.

- 현재 summary, coverage, warnings, cautions, evidence reading
- 현재 점수 표, 점수 구성 기여, core 16개 일봉 변화의 JSON records
- current pattern, 60D ribbon, evidence, change conditions
- 5D·20D probability, independent episode, validation metric, conditional terminal/range
- method / limitation metadata

저장하지 않는다.

- 5년 전체 OHLCV row
- 전체 historical feature frame
- 전체 forward-coordinate frame
- provider raw response
- Streamlit session state 또는 render-only event state

이 경계는 DB row를 작게 유지하면서 현재 React 화면과 계산 추적을 재구성하기에 충분하다.

## 코드 경계

### Persistence

- `finance/data/db/schema.py`: `futures_macro_snapshot` schema
- `finance/data/futures_macro_snapshot.py`: schema sync, canonical JSON, marker-aware UPSERT / latest load
- `finance/loaders/futures_macro_snapshot.py`: latest compatible compact snapshot read

### Materialization

- `app/services/futures_macro_snapshot.py`: 기존 thermometer와 pattern validation 서비스를 호출하고
  DataFrame을 bounded JSON records로 바꾸는 Streamlit-free materializer
- `app/jobs/ingestion_jobs.py`: 성공 또는 partial-success `1d` ingestion 뒤 materialization을 호출하고
  결과를 job details에 남긴다
- `app/jobs/overview_actions.py`: 기존 `일봉 갱신` facade를 유지한다

일봉 저장은 성공했지만 snapshot 계산·저장이 실패하면 수집 결과를 숨기지 않는다.
job은 `partial_success`와 snapshot error detail을 반환해 사용자가 다시 시도할 수 있게 한다.

### Overview read / React

- `app/web/overview/futures_macro_helpers.py`: render-time 계산 loader를 persisted loader로 교체하고,
  Streamlit `원본 데이터 / 계산 추적` expander는 React available path에서 제거한다
- `FuturesMacroWorkbench.tsx`: compact trace payload type과 disclosure rendering 연결
- `MethodDisclosure.tsx`: controlled toggle 또는 toggle callback으로 iframe height 재측정
- 새 `CalculationTraceDisclosure.tsx`: 자료 기준, 점수, 기여, 16개 선물 변화, 주의점을 React table로 표시
- `style.css`: 공통 disclosure / responsive table / overflow 규칙

React component build가 없을 때의 native fallback은 저장 snapshot만 읽고 기존 최소 안내를 유지한다.
fallback도 render 중 5년 전망 계산을 실행하지 않는다.

## React disclosure 계약

### 방법론과 품질

- 기본은 닫힘 상태다.
- toggle 직후 `Streamlit.setFrameHeight()`를 즉시, 다음 animation frame, 짧은 timeout에서 호출한다.
- 내용이 열린 뒤 다음 Streamlit 블록과 겹치거나 iframe에서 잘리지 않아야 한다.

### 원본 데이터 / 계산 추적

- React workbench의 마지막 disclosure로 `방법론과 품질` 다음에 둔다.
- 자료 기준과 저장 시각을 먼저 보여준다.
- `현재 점수 원본`, `점수 구성 기여`, `선물 일봉 변화`, `해석 주의점`을 내부 section으로 구분한다.
- 큰 화면은 가로 scroll 가능한 표, 좁은 화면은 disclosure 폭 안의 table scroll로 처리한다.
- full OHLCV를 보내거나 브라우저에서 계산하지 않는다.
- React가 정상 렌더되면 같은 내용의 Streamlit expander를 중복 표시하지 않는다.

## 검토한 대안

1. **채택: 영속 compact service snapshot + 단일 React workbench**
   - 첫 진입이 DB 한 행 조회가 되고 서버 재시작 뒤에도 빠르다.
   - 계산과 화면을 분리하고 Streamlit/React disclosure 중복을 없앤다.
2. **기각: process memory cache 유지**
   - 구현은 작지만 재시작, worker 변경, cache 만료 때 긴 첫 진입이 반복된다.
3. **기각: 탭 진입 시 stale-check 후 자동 재계산**
   - 최신성은 높지만 사용자의 원래 문제인 첫 진입 대기를 다시 만든다.
4. **기각: 방법론만 resize하고 raw expander는 Streamlit 유지**
   - 잘림 하나는 고치지만 화면 경계와 사용자 경험이 계속 둘로 나뉜다.

## 오류 및 호환성

- snapshot row 없음: 계산하지 않고 `일봉 갱신 필요` 상태
- incompatible schema / algorithm: 계산하지 않고 `새 snapshot 필요` 상태
- malformed JSON: 오류를 격리하고 갱신 안내, 화면 전체 crash 금지
- ingestion failure: 이전 READY snapshot 보존
- materialization failure: 이전 snapshot 보존, job result에 partial/error 표시
- source marker 동일: 기존 compatible snapshot 재사용
- `PROVISIONAL` / `UNAVAILABLE` publication 상태와 확률 숫자 숨김 계약 유지

## 테스트 계약

### Python RED/GREEN

- schema에 stable unique key, source marker, version, JSON, materialized timestamp가 있다.
- snapshot JSON round-trip이 DataFrame 없이 동일 compact payload를 복원한다.
- 같은 marker/version은 계산 함수를 다시 호출하지 않는다.
- marker 또는 algorithm version 변경은 새 계산과 UPSERT를 실행한다.
- `1d` ingestion만 post-materialization 대상이고 실패는 partial result로 노출한다.
- Overview panel은 persisted loader를 사용하며 thermometer / pattern loader를 render path에서 호출하지 않는다.
- React available path에는 `st.expander("원본 데이터 / 계산 추적")`가 없다.

### React source / build

- 두 disclosure toggle이 frame height sync callback을 호출한다.
- calculation trace payload와 four named sections가 존재한다.
- 5년 full OHLCV payload 또는 client-side 전망 계산이 없다.
- TypeScript / Vite production build가 통과한다.

### Actual Browser QA

- fresh process에서 Futures Macro 첫 진입이 persisted snapshot만 읽는다.
- `방법론과 품질` open 시 모든 metric / caveat / boundary note가 보이고 다음 section과 겹치지 않는다.
- `원본 데이터 / 계산 추적` open 시 네 section이 React 안에서 보인다.
- desktop과 420px에서 document / iframe horizontal overflow와 content clipping이 없다.
- console error가 없다.
- QA screenshot 한 장을 generated artifact로 남기고 commit하지 않는다.

## 범위 밖

- 선물 확률, 유사 episode 선정, 30 / 60 publication gate 변경
- 5년보다 긴 학습 구간 또는 새 provider
- OS scheduler / cron / launchd 등록
- 가격 목표, 매수·매도 신호, 자동 주문
- 전체 OHLCV browser table 또는 raw provider payload 노출

## 완료 조건

- `일봉 갱신` 한 번으로 5년 수집과 compatible compact snapshot 저장이 끝난다.
- server process cold start 뒤 탭 진입이 5년 pattern 계산을 실행하지 않는다.
- snapshot이 없으면 느린 fallback 대신 명확한 갱신 안내가 나온다.
- 방법론과 원본 추적이 같은 React disclosure 패턴으로 보이고 잘리지 않는다.
- focused tests, Vite build, compile / diff check, actual desktop / 420px Browser QA가 통과한다.

