# S&P 500 실제 EPS 등록

## 이걸 하는 이유?

경제 사이클의 `실제 TTM EPS`는 공식 완료 분기 actual As-Reported EPS가 8개 필요하지만 현재 DB가 비어 있다. 사용자가 공식 S&P Index Earnings XLSX를 등록하면 검증·저장하고 경제 사이클이 자동으로 읽게 한다.

## Roadmap

1. 원인·소스·제약 분석 및 명세 승인 — 완료
2. 공식 workbook 파서, release-vintage 저장, PIT loader, Ingestion UI — 진행 중
3. 공식 파일 실제 등록, Browser QA, 문서 closeout — 예정

## 완료 조건

- 명시적 actual/as-reported 분기만 저장한다.
- 8개 완료 분기로 current/prior TTM과 YoY를 계산한다.
- 기준일 이후 발표 vintage를 읽지 않는다.
- 업로드 UI와 focused regression test가 통과한다.

