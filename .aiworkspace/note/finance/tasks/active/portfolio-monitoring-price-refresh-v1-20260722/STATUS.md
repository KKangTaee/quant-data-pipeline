# Status

- 상태: 완료
- 전체 roadmap: 3/3차
  - 1차: freshness/수집 서비스와 Python event bridge
  - 2차: 공통 기준일 배너 action과 component build
  - 3차: 통합 검증, actual Browser QA, 문서·commit
- 완료 결과: 선택 그룹의 활성 direct stock·ETF가 최근 완료 NYSE 거래일보다 오래되면 공통 기준일 배너에 지연 종목과 `보유 종목 가격 최신화` action을 표시한다. 명시 클릭은 기존 OHLCV ingestion job을 실행하고 DB 최신성을 재검증한 뒤 공통 기준일과 종합 가치곡선을 다시 계산한다.
- actual QA: AMD/RKLB/TEM/QQQ/SOXX를 2026-07-21까지 갱신했고, 공통 기준일이 2026-07-16에서 2026-07-21로 이동했으며 완료 후 action이 사라지는 것을 확인했다.
- 경계: selected strategy와 종료 항목은 대상이 아니며 raw run 진단은 Portfolio Monitoring에 추가하지 않고 기존 Ingestion 실행 기록에 남긴다.
