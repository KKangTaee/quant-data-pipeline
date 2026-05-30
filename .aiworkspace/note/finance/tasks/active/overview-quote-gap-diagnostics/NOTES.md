# Notes

- 1차 diagnosis는 evidence-based hint로 취급한다. `possible_stale_universe`도 상장폐지 / 거래정지 확정 판정이 아니다.
- Overview UI는 provider를 직접 fetch하지 않고 job wrapper를 호출해 결과를 표시한다.
- 진단 결과는 local run history에는 남을 수 있지만, 1차에서는 별도 persistent diagnostic table을 만들지 않는다.
