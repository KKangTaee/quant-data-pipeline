# Inflation Policy Data Pipeline Notes

- 2026-08-02: UI 시안 승인 뒤 실제 구현 순서는 data -> engine -> workbench로 확정했다.
- 기존 경제 사이클 서비스와 결과는 새 데이터/모델의 dependency가 아니다.
- 2026 SEP 분포는 aggregate count만 저장하며 participant mapping을 생성하지 않는다.
- FRED HTTP·pagination·normalization·UPSERT primitive만 공통 module로 분리했다. 기존
  경제 사이클 catalog와 수집 orchestration은 기존 module에 남겼다.
- verified clock이 없는 series는 `END_OF_DAY_ET`로 보수적으로 공개시각을 잡는다.
