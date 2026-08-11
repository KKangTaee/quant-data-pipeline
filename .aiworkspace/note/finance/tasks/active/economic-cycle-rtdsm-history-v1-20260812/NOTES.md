# Notes

- RTDSM workbook은 row=observation month, column=vintage인 wide matrix다.
- 일부 2026 workbook core timestamp가 `T 8:` 형식이라 openpyxl이 그대로는 실패한다.
- monthly vintage known-at은 해당 월말, quarterly vintage는 분기 중간 월말로 보수적으로
  고정한다.
- ADS all-vintages zip은 약 160MB라 long-history sample 확보 단계에는 포함하지 않는다.
- 현재 8지표 state는 frozen scope이며 RTDSM 4지표 state가 자동 대체하지 않는다.

