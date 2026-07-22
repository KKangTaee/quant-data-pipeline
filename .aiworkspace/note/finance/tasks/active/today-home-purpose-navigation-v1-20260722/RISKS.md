# Risks

- 여러 DB-backed loader의 직렬 호출 latency는 기존 cache를 재사용한다. actual 첫 reload에서 완료를 확인했지만 별도 성능 budget은 아직 없다.
- source별 as-of/freshness는 compact normalization과 최대 근거 기준일을 사용한다. future event 날짜가 header as-of를 앞당기지 않도록 회귀 테스트로 고정했다.
- initial Futures Macro MISSING과 final `3/5 READY · 5/5 available` partial layout 모두 desktop·760px·420px에서 정상 표시됐다.
- 대표 포트폴리오 active item 부재/valuation 실패는 `EMPTY / PARTIAL`로 표시하고 0% 성과를 합성하지 않는다.
- 기존 상세 화면 내부의 legacy owner-path copy는 이번 renderer 보존 범위 때문에 남아 있으며 navigation label 정합성 cleanup은 별도 승인 과제다.
- 전용 default-group loader는 list/read와 계산만 사용하고 자동 생성·command·session 선택을 거치지 않는다. fake repository behavioral test가 write method 호출 0을 고정한다.
