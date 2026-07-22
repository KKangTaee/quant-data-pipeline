# Today Portfolio Intraday Auto Refresh V1 Risks

- Streamlit fragment rerun에서 custom component key가 불안정하면 iframe reset이 보일 수 있다. stable key와 actual no-reset QA가 완료 조건이다.
- Python background future만 중복 기준으로 쓰면 multi-session/process에서 provider가 중복 호출된다. DB advisory lock과 DB due-check가 함께 필요하다.
- partial quote를 silently previous-close fallback하면 live value로 오해할 수 있다. coverage와 fallback count를 표시한다.
- intraday quote를 daily close row로 저장하면 backtest/EOD 의미가 오염된다. 두 저장 계약을 분리한다.
- same-day position event가 있으면 단순 `last value × price ratio`가 틀릴 수 있다. existing position ledger와 flow-adjusted valuation을 재사용한다.
- provider quote timestamp가 오래됐거나 delayed일 수 있다. timestamp와 10분 stale gate를 적용한다.
- 장 마감 직후 daily row가 아직 provider에 없을 수 있다. 5분 grace, bounded retry와 `종가 반영 대기`를 사용한다.
- background executor는 process restart 때 future state를 잃는다. DB snapshot/EOD state를 recovery source-of-truth로 둔다.
