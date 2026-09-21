# 설계

## 데이터와 해석 경계
`DB 완료 5분봉 → windows → reading → overview read model → React / Streamlit fallback`을 유지한다. 현재와 이전 관측은 같은 provider의 정확한 끝점만 사용한다. 새로운 수집기/테이블/PIT 예측 모델을 만들지 않는다.

| 선택 구간 | 현재 범위 | 이전 범위 |
|---|---|---|
| 미국장 마감 이후 | 직전 공식 cash close C → 공통 종료 T | 같은 C → T−60분; C 이상 종료를 확보하지 못하면 비교 불가 |
| 최근 1시간 | T−60분 → T | T−120분 → T−60분 |

- `previous_window`는 DB raw 가격의 재계산 결과이며 과거 수집 당시 immutable 판정이 아니다.
- `condition_results`: 주가지수 동행과 국채·달러 조합을 독립적으로 계산. 각 항목은 실제값/방향, case/verdict/tone/explanation, comparison을 포함한다.
- `comparison`: 이전 구간이 정확히 맞고 입력이 유효할 때만 CHANGED/UNCHANGED. 분류 이름과 개별 자산 부호를 모두 비교한다. 그 외 UNAVAILABLE.
- `time_context`: KST 표시용 UTC 시작/종료·평가 시각, 평가 당시 관측 경과 분. 현재시각으로 계속 움직이는 live ticker가 아니다.
- 달러는 고정 EUR/JPY/GBP/AUD/CAD 5종 역방향 동일 가중 평균. 하나라도 없으면 가용 통화만으로 재가중하지 않는다.
- STALE은 저장값을 남기고 현재 해석 보류. UNAVAILABLE은 유효 구간이 아니므로 0%를 관측으로 노출하지 않는다. PARTIAL일 때 가용한 주가지수 확인은 독립 표시한다.

## 화면 순서
연한 배경의 workbench → refresh 한 개 → 두 비교구간 → 종합 해석/판정 배지 → 시작·종료·조회 시각과 선물 6개 카드 → 두 실제 확인 결과 → 월간 경기 배경 → 접힌 구성/추가 근거.

상승/하락 숫자 색과 지지/부담 결론 색은 역할을 구분하고 문자도 반드시 표시한다. 420px은 가격 2열/조건 1열, 넓은 화면은 가격 6열/조건 2열이다. 기존 reload action은 frontend와 Python dispatcher에서 함께 제거한다.

## 해석 제한
부호 조합은 가격 동반 반응의 설명이다. 통계적 유의성, 인과, 이후 수익 확률, 개별주 추천으로 승격하지 않는다. 혼합 조합도 두 축의 상충을 구체적으로 설명한다. 영향의 크기와 0.01% 표시 부호가 다름을 화면에 알린다.
