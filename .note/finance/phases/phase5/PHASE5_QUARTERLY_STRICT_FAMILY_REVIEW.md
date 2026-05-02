# Phase 5 Quarterly Strict Family Review

## 목적

- quarterly strict family를 지금 바로 여는 것이 맞는지 먼저 판단한다.

## 현재 판단

- `defer`

## 이유

1. annual strict family가 이제 막
   - baseline
   - compare parity
   - overlay first pass
   까지 열린 상태다
2. quarterly strict family는 annual보다
   - coverage
   - freshness
   - runtime
   - point-in-time 설명 난이도
   가 모두 더 까다롭다
3. first overlay 효과와 운영성을 annual strict family에서 먼저 보는 편이 더 안전하다

## 지금 필요한 최소 조건

quarterly strict family를 public candidate로 보려면 적어도 아래가 먼저 필요하다.

- quarterly statement shadow coverage audit
- freshness spread 재점검
- annual 대비 activation start 비교
- runtime cost 점검
- annual strict family overlay on/off 결과 정리
- selection interpretation / stale preflight가 annual path에서 먼저 안정화

## public 착수 기준

quarterly strict family를 다음 챕터에서 실제 구현 대상으로 올리려면
아래 기준이 충족되는 편이 좋다.

1. annual strict family에서
   - overlay on/off 비교 기준이 고정되어 있을 것
   - stale reason classification이 운영 해석 수준에서 충분히 읽힐 것
2. quarterly strict coverage가
   canonical preset 후보에서 research-only 수준을 넘길 것
3. quarterly runtime이
   annual 대비 과도하게 불안정하지 않을 것
4. activation start가
   annual 대비 지나치게 늦지 않을 것

## 권장 방향

- 다음 순서가 적절하다
  1. annual strict family overlay/compare 안정화
  2. quarterly strict family coverage audit
  3. research-only path 여부 판단
  4. 필요 시 public candidate 검토

## 결론

- quarterly strict family는 좋은 확장 후보지만,
  Phase 5 첫 챕터에서는 review까지 하고 구현은 뒤로 미룬다.
- 현재 상태에서는
  `next chapter candidate`
  로 두는 것이 가장 적절하다.
