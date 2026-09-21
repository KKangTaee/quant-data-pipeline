# 선물 매크로 판정 설명·UX 보완

사용자 승인: 2026-09-21 저장 자료 다시 읽기 제거, 물가정책/심리/일정 탭 스타일 참고, 시점·지표 의미 명확화, 조건을 실제 계산한 판정과 사례별 설명 제공.

## 이걸 하는 이유?
기존 흰 화면과 모호한 시각 문구, 모든 혼합 조합을 보류하는 해석, 사용자에게 확인을 떠넘기는 next_checks 때문에 숫자를 읽고 결론을 이해하기 어려웠다.

## 단계
1. 기존 세 탭의 UI 및 현재 수식/지표 의미 확인. 완료 조건: 비교 시각·파생 지표와 해석 범위 정의.
2. 현재 관측+1시간 전 비교 판정, 사례별 설명, 명확한 가격 구간과 색상/배지 UI 및 fallback. 완료 조건: 실제값→판정→설명이 일치하고 reload 제거.
3. 부호조합·누락·오래된 자료·시간 경계 테스트, 실제 DB 검산, Browser QA, 독립 리뷰 및 로컬 앱 반영.

## 구현 경계
- app/services/futures_macro_windows.py: 기존 raw 5분봉으로 각 구간의 1시간 전 비교값 추가. since_close는 동일 anchor, last_hour는 겹치지 않는 직전 60분. 비교 불가 시 발명하지 않음.
- app/services/futures_macro_reading.py 및 overview/futures_macro.py: 현재 주가지수 동행과 금리·달러 조합을 분리 판정. 부호 전체 조합, neutral, missing, stale 사례. 이전 값은 같은 기준/유효 자료일 때만 변화 설명.
- app/web/overview/futures_macro_helpers.py / futures_macro_workbench: reload 제거, 시점 band와 asset label, 두 조건 결과 카드, 동일 fallback.
- 다른 탭의 코드/계산, ingestion·schema·공유 daily current는 변경하지 않는다.

## 의미와 한계
- 완료봉 두 시각의 선물 가격 변화율. 실시간 틱이나 주가지수 현물 수익률로 명명하지 않는다.
- 국채선물은 가격이며 금리 bp가 아님. 5개 통화 역방향 평균은 자체 달러 대용지표, 공식 DXY 아님.
- 1시간 전 판정과 현재 판정의 비교이지 다음 1시간 예측/검증된 확률이 아님.
- 상승/하락 방향은 표시 단위0.01% 기준. 경제적 유의성·예측 강도를 보장하지 않음.
