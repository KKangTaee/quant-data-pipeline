# Risks

Last Updated: 2026-07-25

## Open Risks

- summary를 줄이면서 가격 원인 비확정·해외 상대금리 결측 같은 중요한 경계를 잃지
  않아야 한다.
- 모든 작은 label을 `+1px` 하면 420px 카드에서 줄바꿈이 늘 수 있다.
- 기존 unrelated registry/run-history/generated artifact를 stage하지 않아야 한다.

## Mitigations

- 자산 고유 interpretation에 경로·가격·자료 한계를 명시적으로 분리한다.
- typography를 자산별 section에 한정하고 desktop/420px overflow를 확인한다.
- stage path를 task/spec/code owning files로 제한한다.
