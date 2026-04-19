# Phase 23 Quarterly Productionization Frame First Work Unit

## 이 문서는 무엇인가

`Phase 23`의 첫 번째 작업 단위 문서다.

이 문서는 quarterly strict family를 바로 고치기 전에,
현재 상태가 어디까지 구현되어 있고 무엇이 아직 prototype인지 먼저 정리한다.

## 쉽게 말하면

quarterly 전략은 이미 UI와 runner가 있다.
하지만 "돌아간다"와 "제품 기능으로 믿고 쓴다"는 다르다.

이번 첫 작업은 quarterly 기능을 제품 기능으로 올리기 전에,
어떤 부분이 이미 충분하고 어떤 부분이 아직 부족한지 지도를 그리는 일이다.

## 현재 코드 기준으로 이미 되는 것

현재 quarterly strict family는 아래 기능을 갖고 있다.

- single strategy에서 quarterly strict family를 선택하고 실행할 수 있다.
- compare form에 quarterly 전략을 넣을 수 있다.
- history rerun / load-into-form 흐름 일부가 연결되어 있다.
- quarterly statement shadow coverage preview를 볼 수 있다.
- `Historical Dynamic PIT Universe` first-pass 흐름을 사용할 수 있다.
- trend filter와 market regime overlay를 일부 사용할 수 있다.
- selection history와 interpretation surface가 존재한다.

## 아직 제품 기능으로 보기 어려운 이유

아직 아래 항목들은 확인 또는 보강이 필요하다.

- UI 이름과 설명에 `Prototype`, `Research-only` 성격이 남아 있다.
- annual strict family에 있는 explicit portfolio handling contract가 quarterly에 같은 수준으로 붙어 있는지 불분명하다.
- rejected slot handling, weighting contract, risk-off contract를 quarterly에서 어떻게 읽어야 하는지 아직 충분히 고정되지 않았다.
- real-money contract, guardrail, promotion surface를 quarterly에 그대로 붙일지, 아직 보류할지 판단이 필요하다.
- compare / history / saved replay에서 quarterly-specific 설정이 빠지지 않는지 실제 QA가 필요하다.
- quarterly factor timing은 annual보다 point-in-time 해석이 더 민감하므로 경고와 설명이 더 중요하다.

## 이번 작업에서 고정할 기준

Phase 23에서 quarterly를 제품화한다는 말은 아래를 뜻한다.

- 사용자가 UI에서 quarterly 전략을 찾고 실행할 수 있다.
- 실행 전 중요한 입력과 제한을 이해할 수 있다.
- 실행 결과를 compare, history, load/replay로 다시 이어갈 수 있다.
- quarterly 결과가 annual 결과와 다르게 계산되는 이유가 설명된다.
- 대표 실행 조합이 최소한 깨지지 않는다는 smoke validation이 남는다.

반대로 아래를 뜻하지는 않는다.

- quarterly 전략을 바로 투자 후보로 추천한다.
- quarterly 결과가 annual보다 좋으면 자동으로 promotion한다.
- 모든 quarterly 조합을 깊게 최적화한다.
- portfolio weight 분석을 다시 확장한다.

## 다음 구현 후보

다음 작업은 아래 순서가 자연스럽다.

1. quarterly single strategy UI의 이름, 설명, warning을 정리한다.
2. annual strict 대비 quarterly에 없는 contract surface를 표로 정리한다.
3. compare / history / saved replay에서 quarterly override가 유지되는지 확인한다.
4. 최소 representative smoke run과 report를 남긴다.

## 한 줄 정리

첫 번째 작업의 결론은 단순하다.
quarterly strict family는 이미 실행 경로가 있지만, Phase 23에서는 그것을 투자 분석이 아니라 재현 가능한 백테스트 제품 기능으로 다듬어야 한다.
