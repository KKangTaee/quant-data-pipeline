# 선물 매크로 갱신 성능과 사용자 가치 감사

State: complete
Date: 2026-09-21

## 이걸 하는 이유?

사용자는 선물 매크로의 최신 데이터 갱신이 느린 이유, 개선 방법, 시장 재가격화 해석·선물군별 방향 정렬·최근 체제 이력을 어떻게 읽어야 하는지, 실제로 유효한 정보가 있는지를 요청했다.

## 범위와 진행

1. 완료: 최근 갱신 기록과 계산 경로를 추적하고 SELECT-only 데이터로 계산 병목을 재현했다.
2. 완료: 현재 브라우저, 가격 점수·체제 규칙, 저장된 예측 검증을 대조해 관측 가치와 예측 한계를 구분했다.
3. 완료: 성능·해석·검증 개선의 우선순위와 후속 구현의 완료 조건을 제안했다.

이번 산출물은 분석 및 제안이다. 제품 코드, 데이터, refresh 실행, 운영 설정은 변경하지 않았다. 개선안은 승인된 개발 범위가 아니다.

## 접근

- finance-product-audit로 제품과 구현 사실을 대조했다.
- dispatching-parallel-agents에 따라 성능 분석을 독립 read-only subagent에 맡기고 주 작업자는 UI·지표 의미를 분석했다.
- 실제 갱신 로그 1건과 동일 입력의 계산 재현 1건을 사용했다. p50/p95 또는 개선 후 속도를 측정한 것은 아니다.
- DB 관측은 SELECT-only / READ ONLY 연결을 사용했다. 기본 query helper 일부에는 DDL이 있어 주입형 query로 우회했다.
- 외부 근거는 CME 공식 자료로 선물 가격 해석과 연속계약 구성의 주의점을 확인했다. 서비스 비교는 요청 범위 밖이다.

## 읽을 위치

- 결론 및 후속 범위: [RECOMMENDATION.md](./RECOMMENDATION.md)
- 구현·화면·실측: [CURRENT_PROJECT_AUDIT.md](./CURRENT_PROJECT_AUDIT.md)
- 사용자 해석 예시: [UI_PATTERNS.md](./UI_PATTERNS.md)
- 근거와 검증 공백: [SOURCES.md](./SOURCES.md), [RISKS.md](./RISKS.md)

finance-doc-sync closeout: canonical doc change 없음. 승인된 제품 약속·구현 소유권·우선순위가 바뀌지 않았으므로 PRODUCT_DIRECTION / PROJECT_MAP / ROADMAP / INDEX는 유지한다.

## 09-21 후속: compact 조건부 전망 가이드

사용자의 ‘현재 강약 → 과거 n회 → 앞으로의 흐름’ 목적에 맞춰 1차 활용 범위, 2차 조건부 빈도/전망 방법, 3차 세 영역 화면 가이드 분석을 완료했다. 상세는 [COMPACT_OUTLOOK_GUIDE.md](./COMPACT_OUTLOOK_GUIDE.md)다. finance-product-audit와 brainstorming으로 현재 계산 계약을 확인하고 대안을 비교했다. 대표 ETF/선물 raw coverage는 SELECT-only로 확인했으며, 실제 새 통계·전망·제품 변경은 실행하지 않았다. 대상 범위는 자산군/대표 지수·ETF를 권고안의 가정으로 두었다.
