# Risks

- Local 13F DB가 한 분기만 있으면 분기 변화 board는 일부 항목이 계속 0이다. UI 문구로 데이터 상태를 분리해야 한다.
- 가격 DB에 일부 holding symbol이 없거나 CUSIP-symbol mapping이 틀릴 수 있다. 성과 요약은 covered weight와 caveat를 함께 보여야 한다.
- Report-period ranking aggregate는 `report_period + cusip + cik` 접근이 필요해 index가 없으면 느릴 수 있다. schema index와 local DB index 적용 여부를 검증한다.
- Browser QA screenshot은 generated artifact로 커밋하지 않는다.

## Closeout Notes

- Streamlit page-path routing can delay component event settlement in Browser QA. React now clears pending state after timeout and shows a local payload-based selected-security detail while waiting for server response.
- CUSIP-symbol mapping remains partial and can be wrong in old local rows. Loader joins now require exact issuer-name match for display mapping, and popularity ranking displays CUSIP / issuer when a safe symbol is not available.
- Portfolio performance coverage is calculated against the full displayed portfolio weight, so unmapped holdings reduce coverage instead of being silently ignored.
