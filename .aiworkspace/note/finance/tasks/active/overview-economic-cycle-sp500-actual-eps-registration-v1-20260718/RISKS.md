# Risks

- 2026-05-27 보존본으로 raw layout은 검증했지만 S&P의 향후 workbook 머리글이 바뀌면 저장을 중단하고 parser fixture를 보강해야 한다.
- 코드 완료와 DB 실제 8분기 적재는 구분한다. 사용자가 직접 받은 현재 공식 파일이 없으면 제품 경로는 완성해도 `실제 TTM EPS`는 자료 부족을 유지한다.
- S&P 접근 제한을 자동화로 우회하지 않는다.
- 현재 공식 workbook을 등록하기 전에는 UI에 `실제 TTM EPS`가 활성화됐다고 말하지 않는다. 보존본은 parser QA 자료일 뿐 canonical DB 입력이 아니다.
