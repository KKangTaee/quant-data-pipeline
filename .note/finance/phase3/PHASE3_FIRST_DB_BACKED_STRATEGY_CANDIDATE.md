# Phase 3 First DB-Backed Strategy Candidate

## 목적
이 문서는 Phase 3에서
loader와 가장 먼저 연결해볼 전략 후보를 확정하기 위한 문서다.

관련 문서:
- `.note/finance/phase3/PHASE3_FIRST_LOADER_IMPLEMENTATION_ORDER.md`
- `finance/strategy.py`
- `finance/engine.py`

---

## 1. 기본 결론

Phase 3의 첫 DB-backed strategy 후보는
`EqualWeightStrategy`로 고정한다.

---

## 2. 선택 이유

`EqualWeightStrategy`를 첫 후보로 선택한 이유:

1. 입력 요구사항이 가장 단순하다
2. `Date`, `Close` 중심의 가격 데이터만으로 동작 가능하다
3. fundamentals / factors / statements 의존성이 없다
4. 전략 결과 검증이 쉽다
5. loader 계층과 runtime adapter의 첫 성공 경로로 적합하다

---

## 3. 이번 단계에서 제외한 후보

### `GTAA3Strategy`
- 추가 지표 계산이 더 필요함
- `Avg Score`, 이동평균, interval return 등이 필요

### `RiskParityTrendStrategy`
- 변동성 계산과 이동평균 전처리가 더 필요

### `DualMomentumStrategy`
- 12M return과 필터 컬럼 준비가 필요

즉 이 전략들은
첫 runtime 연결 이후 2차 후보로 두는 것이 적절하다.

---

## 4. 첫 검증 목표

`EqualWeightStrategy`로 먼저 확인하려는 것은:

1. DB에서 가격 데이터를 읽을 수 있는가
2. loader 출력이 기존 전략 입력 형식으로 변환 가능한가
3. 전략 결과 DataFrame이 정상 생성되는가

---

## 결론

Phase 3의 첫 DB-backed strategy는
`EqualWeightStrategy`로 시작한다.

이 전략은 가장 단순하고,
loader 계층의 첫 성공 여부를 판단하기에 가장 적합하다.
