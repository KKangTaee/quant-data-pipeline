# Institutional 13F OpenFIGI Mapping V1 Plan

Status: Design Approved
Started: 2026-07-18

## 이걸 하는 이유?

SEC Form 13F 보유 row는 issuer와 CUSIP/CINS를 제공하지만 거래 ticker를 보장하지 않는다. 현재 제품은 내부 `nyse_asset_profile`의 보수적인 발행사명 일치와 소수 curated seed만 사용하므로 Duquesne 최신 포트폴리오 70개 row 중 5개만 ticker로 연결된다.

보유 비중과 평가액은 정상인데도 대부분의 종목에서 차트, 가격 수집, ticker 기반 sector가 닫혀 있어 실제 탐색 가치가 낮다. 이번 작업은 무료 OpenFIGI v3를 검증된 식별자 보강 원천으로 추가하되, 단일 미국 Equity 후보로 수렴하지 않는 결과는 계속 차단하는 것이 목적이다.

## 전체 Roadmap

### 1차: OpenFIGI v3 안전 변환기

- 목적: CUSIP/CINS를 무료 OpenFIGI v3에 batch 요청하고 응답을 결정적으로 분류한다.
- 예상 파일: `finance/data/institutional_13f_mapping.py`, focused tests.
- 완료 조건: `ID_CUSIP`/`ID_CINS`, US Equity filter, optional free API key, rate-limit/retry, mapped/ambiguous/unmapped/error 분류가 테스트된다.
- 상태: 설계 승인. 구현 대기.

### 2차: 영속화와 안전한 source precedence

- 목적: OpenFIGI 결과와 시도 상태를 idempotent하게 저장하고 legacy 이름 추정 후보가 verified result를 덮지 못하게 한다.
- 예상 파일: `finance/data/db/schema.py`, `finance/data/institutional_13f_mapping.py`, `finance/loaders/institutional_13f.py`.
- 완료 조건: current provider resolution과 attempt evidence가 재실행에 안전하며 loader가 `OpenFIGI mapped/ambiguous gate > legacy exact-name > unresolved` 순서로 읽는다.
- 상태: 설계 승인. 구현 대기.

### 3차: 기존 최신 포트폴리오 backfill과 수집 연결

- 목적: curated manager 최신 holdings부터 무료 batch backfill하고 이후 동일 경로를 반복 실행할 수 있게 한다.
- 예상 파일: `finance/data/institutional_13f.py`, `app/jobs/ingestion_jobs.py`, 관련 ingestion registry/guides 중 필요한 최소 범위.
- 완료 조건: 무료 키 없이도 bounded batch가 동작하고, `OPENFIGI_API_KEY`가 있으면 더 큰 공식 한도를 사용한다. 동일 CUSIP을 중복 호출하지 않는다.
- 상태: 설계 승인. 구현 대기.

### 4차: 실제 DB/UI QA와 문서 closeout

- 목적: Duquesne와 주요 manager의 mapping count/value coverage가 실제로 개선되고 기존 unresolved/ambiguous guardrail이 유지되는지 확인한다.
- 완료 조건: focused/full tests, compile/diff check, actual DB backfill, Institutional Portfolios Browser QA 및 screenshot, durable docs alignment를 완료한다.
- 상태: 설계 승인. 구현 대기.

## 이번 작업에서 하지 않는 일

- 유료 Bloomberg Terminal, CUSIP Global Services, Refinitiv 등 licensed security master 도입.
- 발행사명만으로 ticker를 추측해 자동 승인.
- 복수 후보를 첫 번째 응답으로 자동 선택.
- 가격 데이터 자체를 OpenFIGI에서 수집.
- 추천, 매수/매도 신호, broker/live trading 연동.
- run/job/row 진단 패널을 사용자 첫 화면에 추가.
- legacy mapping row의 파괴적 일괄 삭제.

## Completion Condition

- 무료 OpenFIGI v3가 optional API key 방식으로 연결된다.
- 단일 US Equity ticker/composite FIGI로 수렴한 결과만 canonical mapping으로 사용한다.
- no-match, ambiguous, provider error가 서로 다른 상태로 남는다.
- current curated manager holdings backfill과 재실행이 idempotent하다.
- Duquesne actual UI에서 mapping coverage가 개선되고 잘못된 ticker 차트가 열리지 않는다.
- 전체 roadmap 중 완료 차수와 후속 full-universe 확장 범위가 문서에 남는다.
