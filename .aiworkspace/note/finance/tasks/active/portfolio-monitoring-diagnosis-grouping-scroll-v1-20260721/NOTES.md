# Portfolio Monitoring Diagnosis Grouping / Scroll V1 Notes

- 같은 문구의 correlation row는 중복 계산이 아니라 서로 다른 종목쌍의 유효한 원시 fact였다. 문제는 subject identity를 숨긴 표시 계층이었다.
- 표시 그룹은 `meaning` 문자열을 파싱하지 않고 Python의 명시적 family와 `subject_ids`/`primary_metric`을 사용한다.
- correlation summary는 최대 상관계수와 최대 영향 비중, drawdown summary는 가장 큰 음의 낙폭을 사용한다.
- React는 active item id를 `source_ref`로 치환하며 찾지 못한 identity는 `추적 항목`으로 표시한다.
- Browser fixture의 disclosure 자동 펼침은 브라우저 제어 표면에서 native `<details>` 상태가 유지되지 않아 시각 상호작용으로 확정하지 못했다. DOM에는 세 correlation member와 AMD/NVDA/MSFT subject가 모두 존재했고 자동/계약 테스트가 member 렌더를 보호한다.
