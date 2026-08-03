# Inflation Policy Functional Recovery Status

State: active
Roadmap: 2/5 recovery stages complete
Last Updated: 2026-08-03

## Current

- 사용자 재현 6개 증상과 actual DB 상태를 기준으로 기존 완료 기록을 재감사했다.
- 기존 집중 baseline은 Python 190건, React 11건 통과했지만 actual reverse click과
  production materialization contract를 포함하지 않았음을 확인했다.
- 승인된 복구 설계와 5차 roadmap을 기록했다.
- reverse command result를 payload 저장 전 JSON-safe하게 정규화했다.
- React가 snapshot 전체 상태가 아니라 inflation/policy component별 상태로 확률을
  표시하도록 복구했다.
- actual DB reverse command 결과가 `datetime`을 문자열로 변환하고 JSON 직렬화되는지
  확인했다. joint path 부재로 결과 자체는 정확히 `NOT_AVAILABLE`이다.
- Philadelphia Fed SPF Core PCE `PRCPCE` 공식 확률분포 1,560개 bin을
  `spf_core_pce_probability`에 PIT release clock과 함께 적재했다.
- chain-price index rebasing 때문에 서로 다른 최초공개 level을 섞으면 2018/2023 Q4가
  음수로 왜곡되는 문제를 찾고, December 최초 공개시각의 단일 일관 vintage로 실제
  Q4/Q4 target을 계산하도록 수정했다.
- 2018~2025 31개 조사 origin·8개 독립 target year에서 SPF+월별 모델 linear pool을
  직접 검증했다. CRPS 0.3613, 단순 전년 Q4 baseline 0.7823, SPF 단독 0.4217,
  최대 interval calibration error 0.0484로 `READY`다.
- actual 2026-08-03 snapshot의 inflation component를 `READY`로 저장했고 5상태,
  3.4/3.5/3.6% threshold, 다음 발표 0.1~0.5% 민감도를 Browser에서 확인했다.

## Next

- 3차 FOMC decision history를 공식 source에서 backfill한다.
- policy probability와 joint rate path를 chronological holdout에서 검증해 다음 회의,
  연말 경로, 역산 command와 다음 발표 인상 변화 칸을 연결한다.
