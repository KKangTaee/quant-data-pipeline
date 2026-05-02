# Phase 19 Risk-Off And Weighting Interpretation Cleanup Third Slice

## 무엇을 바꿨는가
- strict annual selection history와 interpretation summary가
  `Risk-Off Contract`와 `Weighting Contract`도
  operator가 바로 읽을 수 있는 언어로 보여주도록 정리했다.

## 기존 문제
- `Rejected Slot Handling`은 previous slice에서 정리됐지만,
  `Weighting Mode`, `Risk-Off Mode`는 아직 raw value나 내부 컬럼 중심으로 남아 있었다.
- 그래서 사용자는:
  - 현재 run이 `Equal Weight`였는지 `Rank-Tapered`였는지
  - full risk-off 시 `Cash Only`였는지 `Defensive Sleeve Preference`였는지
  - 실제로 defensive sleeve가 발동했는지
  를 history / interpretation에서 한 번에 읽기 어려웠다.

## 이번 slice의 정리 포인트
- selection history row에 아래 contract 정보를 같이 남긴다.
  - `Weighting Contract`
  - `Risk-Off Contract`
  - `Risk-Off Reasons`
  - `Defensive Sleeve Tickers`
- interpretation summary에 아래 요약값을 추가했다.
  - `Weighting Contract`
  - `Risk-Off Contract`
  - `Defensive Sleeve Activations`
- row-level interpretation 문구도
  - market regime로 full cash가 되었는지
  - defensive sleeve로 회전했는지
  - 최종 weighting contract가 무엇이었는지
  를 더 직접적으로 설명하게 바꿨다.

## 화면에서 어떻게 달라졌는가
- `History`
  - raw internal mode보다
    `Weighting Contract`, `Risk-Off Contract`, `Risk-Off Reasons` 같은 label을 중심으로 읽는다.
- `Interpretation Summary`
  - 현재 run이 어떤 weighting / risk-off contract를 썼는지 바로 보인다.
  - defensive sleeve가 실제로 몇 번 발동했는지도 따로 요약된다.
- `Selection Interpretation`
  - portfolio-wide risk-off와 trend rejection handling이
    서로 다른 lane임을 더 분명하게 읽을 수 있다.

## 구현 위치
- `app/web/pages/backtest.py`
  - interpretation summary help popover
  - selection history row builder
  - row-level interpretation builder
  - interpretation summary builder
  - selection history meta/header surface

## 왜 필요한가
- `Phase 19`의 목적은
  strict annual 구조 옵션을 "쓸 수 있는 contract"로 정리하는 것이다.
- 그러려면 `Rejected Slot Handling`만 쉬워지는 것으로는 부족하고,
  `Weighting`과 `Risk-Off`도 같은 수준으로 결과 화면에서 읽혀야
  다음 phase의 candidate review와 deep validation이 덜 흔들린다.

## 이번 slice에서 확인한 것
- `python3 -m py_compile app/web/pages/backtest.py`
- `.venv/bin/python` import smoke
- broad rerun은 이번 slice 범위에 포함하지 않음

## 남은 일
- manual UI validation checklist 수행
- 필요하면 strict annual compare/history surface에서
  risk-off reason wording을 더 짧고 일관되게 다듬기
