# Notes

## 2026-07-11 Initial Audit

- 현재 registry 6개 후보의 `세부 audit에서 연결`은 저장된 module audit의 non-PASS row를 최대 3개 연결한 상태다.
- `기간 미포함`은 후보 기간이 2016년 이후라 2000~2009 stress window가 포함되지 않은 결과이며 freshness 문제가 아니다.
- 빈 관측은 Tax / Account 정성 판단, strategy-specific perturbation NOT_RUN, provider row의 criteria 계약 공백으로 나뉜다.
- weighted mix 2개에는 holdings / exposure와 source map 보강 대상이 있으나 단일 후보는 stale-only provider snapshot이라 기존 missing-only collection plan에 잡히지 않는다.
