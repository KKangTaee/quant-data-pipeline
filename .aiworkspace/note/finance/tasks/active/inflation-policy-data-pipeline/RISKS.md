# Inflation Policy Data Pipeline Risks

- 발표일만 있고 시각이 검증되지 않은 series는 보수적 end-of-day 정책이 필요하다.
- 현재 ACM workbook은 historical publication archive가 아니므로 과거 시점에 소급할 수 없다.
- DB migration helper는 column 추가만 하므로 기존 index/constraint 변경은 별도 검증이 필요하다.
- unrelated dirty files를 stage하지 않는다.

