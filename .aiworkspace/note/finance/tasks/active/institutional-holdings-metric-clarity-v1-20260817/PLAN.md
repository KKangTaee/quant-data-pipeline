# Institutional Holdings Metric Clarity V1 Plan

## 이걸 하는 이유?

기관 보유 화면에서 가격 기여, 인기 순위의 보고가액, 13F 해석 한계를 각각 오해 없이 읽을 수 있는 Python 의미 계약으로 고정한다.

## Scope

- 가격 proxy의 양(+) 기여와 음(-) 기여 목록을 분리한다.
- 인기 순위의 보고가액 label과 설명 문구를 명확히 한다.
- workbench payload에 한국어 13F 주의사항 read model을 제공한다.

## Roadmap

1. 의미 계약 고정 — contribution sign, `%p`, reported-value and disclosure payload
2. 화면 표현 개선 — contribution metrics, popularity labels, Korean disclosure
3. 실제 화면 검증과 문서 정렬 — desktop/mobile QA, regressions, closeout

## Stop Condition

지정된 service/React contract tests와 desktop/390px actual Browser QA가 통과하고,
계산/DB/schema/registry/trading 경계를 바꾸지 않는다.

## References

- Approved design: `docs/superpowers/specs/2026-08-17-institutional-holdings-metric-clarity-design.md`
- Implementation plan: `docs/superpowers/plans/2026-08-17-institutional-holdings-metric-clarity.md`
