# Economic Cycle RTDSM History V1

State: active
Last Updated: 2026-08-12

## 이걸 하는 이유?

현재 strict PIT 이력은 독립 전환 사건이 32건뿐이라 다음 국면 목적지 확률을 검증할
수 없다. 공식 RTDSM 장기 빈티지를 반복 가능한 DB 경로로 수집하고, 표본 수와 현행
국면 정합성을 모두 통과하는지 확인해야 예측 모델 개발을 책임 있게 시작할 수 있다.

## Roadmap

1. RTDSM 공식 파일·known-at·저장 계약을 고정한다.
2. XLSX parser, batch UPSERT와 source-filtered loader를 테스트 우선으로 구현한다.
3. 4지표 장기 observed-state와 sample/parity audit를 구현한다.
4. 실제 공식 파일 및 DB 경로로 audit를 재현한다.
5. combined gate가 통과할 때만 별도 destination/imminence model task로 넘긴다.

## Scope

- Philadelphia Fed RTDSM 4개 장기 workbook 수집
- 기존 macro vintage ledger의 provider-native RTDSM row
- research-only long-history state와 sample/parity report
- explicit ingestion job 및 데이터 문서

## Frozen Scope

- 현행 8지표 current observed state와 snapshot
- forecast model/service/UI
- Data Freshness 화면
- 자산별 확인 포인트 계산·payload·디자인

## Stop Condition

공식 파일의 parser→DB→loader 재현과 combined gate 결과를 기록한다. parity 또는 sample
gate가 실패하면 모델 개발을 시작하지 않는다.

