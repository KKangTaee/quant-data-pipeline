# Notes

- RTDSM workbook은 row=observation month, column=vintage인 wide matrix다.
- 일부 2026 workbook core timestamp가 `T 8:` 형식이라 openpyxl이 그대로는 실패한다.
- monthly vintage known-at은 해당 월말, quarterly vintage는 분기 중간 월말로 보수적으로
  고정한다.
- ADS all-vintages zip은 약 160MB라 long-history sample 확보 단계에는 포함하지 않는다.
- 현재 8지표 state는 frozen scope이며 RTDSM 4지표 state가 자동 대체하지 않는다.
- 실제 sample gate는 통과했으므로 기존 `NO_GO_DATA` 원인은 해소됐다. 최종 blocker는
  충분한 row/event 수가 아니라 두 current-state label의 의미 불일치다.
- 사전 등록 parity 기준은 overlap 96개월, exact agreement 60%, Cohen's kappa 0.40,
  level-side agreement 75%이며 실제로는 각각 142개월, 54.2%, 0.368, 83.1%였다.
- 사전에 경제적 역할을 정한 real GDP output과 capacity utilization 대안 감사도 exact
  agreement 60%를 넘지 못했다. 결과를 보고 threshold나 조합을 바꾸지 않는다.
