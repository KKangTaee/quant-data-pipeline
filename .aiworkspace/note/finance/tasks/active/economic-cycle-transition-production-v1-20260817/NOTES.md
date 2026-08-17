# Notes

- 기존 DB schema를 확장하지 않고 versioned `transition_monitor_json`을 사용한다.
- `forecast_path_json`/`probabilities_json` legacy horizon 필드는 새 예측에서 비운다.
- 자산별 확인 포인트 소유 코드와 JSX section은 변경하지 않는다.
- 전환압력의 숫자는 특정 월의 국면 확률이 아니라 다음 3개 usable release 안에 공식 국면이
  바뀔 보정 확률이다.
- 목적지 확률은 전환이 발생한다는 조건 아래 현재 국면을 제외한 모든 국면의 상대 분포다.
- `위축`은 RTDSM 상대 성장순환 국면이며 NBER 경기침체 선언과 동일한 의미가 아니다.
- historical percentile은 확률 의미와 혼동되므로 UI에서는 제거하고 내부 evidence에만 남겼다.
