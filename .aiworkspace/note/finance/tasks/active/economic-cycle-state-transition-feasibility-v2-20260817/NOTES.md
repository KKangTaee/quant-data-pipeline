# Notes

## 2026-08-17 Product Contract Reset

- fixed adjacent monitor는 forecast가 아니다.
- RTDSM-only model은 current state 연구에는 유효하지만 원래 transition mechanism을
  충분히 설명하지 못한다.
- extended model은 policy/inflation/rates/credit를 required driver group으로 검증한다.
- market prices는 optional shadow block이며 기존 자산별 확인 포인트와 계산 경계를
  공유하지 않는다.
- fiscal policy는 현재 승인된 long PIT source가 없으므로 heuristic flag를 만들지 않는다.

## 2026-08-17 Implemented Contract

- 최초 official phase와 이후 transition 모두 동일 raw 후보 2회 연속 확인 시 두 번째
  release에서 확정한다. 첫 후보 월로 소급하지 않고 gap은 streak를 끊는다.
- 고정 순환 순서를 target에 사용하지 않는다. actual 116건에는
  `contraction -> expansion`, `recovery -> contraction`, `slowdown -> expansion` 같은
  비인접 경로도 포함됐다.
- 전환압력은 정확한 3개월 뒤 phase가 아니라 다음 3 usable 공식 발표 안의 confirmed
  transition 사건이다.
- 목적지는 시간 제한 없이 다음 confirmed transition의 네 국면 조건부 분포다.
- official state frame을 sample audit와 dataset이 함께 사용하며 두 번째 confirmation을
  중복 적용하지 않는다.

## Actual Interpretation

- historical state는 latest usable 2026-01 기준 `READY`: 587 usable origins,
  116 independent transitions, 국면 점유율 12.78%~39.35%, one-month official episode
  0.85%, revision exact 68.49%, level-side 86.13%, NBER peak/trough capture 각각
  85.71%다.
- 2026-07 cutoff에는 2~7월 raw/official phase가 `UNAVAILABLE`이다. 최초 구현은 마지막
  panel row의 `data_status=LIMITED`만 보고 이를 잘못 `READY`로 승격했으나, 리뷰에서
  exact latest origin에 confirmed phase가 있어야 한다는 gate를 추가했다. current
  report는 `INCOMPLETE_SOURCE_COVERAGE`로 4.441초 안에 model 전 단계에서 중단한다.
- 최초 실행에서 `ANFCI/PERMIT`가 0건으로 보인 것은 DB 부재가 아니라 이 두 series의
  `released_at`이 비어 있고 ALFRED `realtime_start`만 저장된 시간 계약 차이였다.
  conservative realtime-date fallback을 추가해 ANFCI 1,007,328행, PERMIT 3,538행을
  정상 평가했다.
- forecast history의 지배적 병목은 `BAMLH0A0HYM2`: 2026-01 기준 재현 가능한 PIT
  feature가 2023-08부터 30 origins뿐이고 3개월 변화까지 완전한 시점은 27 origins다.
  모든 required feature 교집합은 27 origins,
  다음 목적지가 알려진 독립 transition은 5건뿐이다.
- 그 5건의 destination은 recovery 3 / contraction 2 / expansion 0 / slowdown 0이다.
  이 표본으로 4국면 목적지 확률이나 전환압력 calibration을 학습하지 않았다.
- fiscal은 `NOT_TESTABLE`, market block은 `SHADOW_ONLY`이며 최종 판정을 올리지 않는다.
