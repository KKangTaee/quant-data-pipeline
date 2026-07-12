# Final Review Investment Report Redesign V1 Risks

- 기존 payload와 fallback render의 호환성을 유지하면서 점수 의미를 바꿔야 한다.
- 패턴 가이드가 저장 evidence보다 강한 투자 조언으로 읽히지 않도록 지원 수준과 근거 공백을 함께 표시해야 한다.
- generated QA PNG와 run history JSONL은 stage하지 않는다.
- 패턴 가이드는 V1 규칙 / token 기반 프로토타입이다. 직접 signal과 trace가 부족하면 `indicative` 또는 `insufficient`로 낮추며 자유 생성형 조언을 만들지 않는다.
- Browser QA로 stale report 차단과 세 상세 탭 전환을 확인했다.
- 남은 blocker는 없다.
