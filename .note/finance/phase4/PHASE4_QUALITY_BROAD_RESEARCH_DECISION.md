# Phase 4 Quality Broad Research Decision

## 목적
이 문서는 첫 factor / fundamental 전략인
`Quality Snapshot Strategy`의 기본 snapshot mode를
`broad_research`로 결정한 이유를 기록한다.

## 결정
- first public mode: `broad_research`

## 이유
1. 현재 `nyse_factors`를 바로 활용할 수 있다
2. UI와 runtime 연결을 가장 빠르게 열 수 있다
3. strict PIT 논의와 구현을 먼저 끝낼 때까지 전략 전체를 막아둘 필요는 없다

## 주의사항
- 이 전략은 first-pass 기준으로 strict PIT 전략이 아니다
- product-facing 문구에서도 `research-oriented quality snapshot strategy`로 설명하는 것이 맞다
- 이후 stricter mode가 준비되면 별도 모드 또는 후속 전략으로 열 수 있다

## 결론
- broad_research를 first public mode로 사용한다
- strict PIT 강화는 후속 작업으로 남긴다
