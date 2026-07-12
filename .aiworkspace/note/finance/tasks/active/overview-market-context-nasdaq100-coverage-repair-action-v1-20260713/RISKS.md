# Overview Market Context Nasdaq-100 Coverage Repair Action V1 Risks

Last Updated: 2026-07-13

## Open Risks

1. 과거 편입·퇴출 종목 가격은 현재 무료 OHLCV provider에서 제공되지 않을 수 있다.
   - 대응: 합성하지 않고 `unsupported_free_source`로 남기며 95% gate를 유지한다.
2. foreign issuer는 SEC에 four-discrete-quarter diluted EPS가 없을 수 있다.
   - 대응: FY-only annual proxy를 도입하지 않고 missing coverage로 남긴다.
3. 전체 60개월 historical universe backfill은 synchronous request가 길어질 수 있다.
   - 대응: small batch, progress callback, per-symbol persistence, resumable planner를 사용한다.
4. React component event가 Streamlit rerun에서 반복 소비될 수 있다.
   - 대응: nonce와 session-state token으로 Python boundary에서 중복을 차단한다.
5. 자료 보강 기능 구현 완료와 실제 60/60 READY는 다른 결과다.
   - 대응: source gap이 남으면 feature는 partial-success evidence와 blocker를 제공하며 READY라고 보고하지 않는다.
