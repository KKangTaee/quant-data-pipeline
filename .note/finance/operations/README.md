# Finance Operations Notes

## 목적

이 폴더는 finance 프로젝트의 운영성 문서를 모아 둔다.

여기에는 phase plan이나 backtest report가 아니라,
반복 실행, runtime artifact, registry, 설정 외부화, 데이터 수집 UI,
daily market update 운영 같은 문서를 둔다.

## 문서 분류

| 구분 | 대표 문서 |
|---|---|
| Registry / artifact 운영 | `CURRENT_CANDIDATE_REGISTRY_GUIDE.md`, `CANDIDATE_REVIEW_NOTES_GUIDE.md`, `PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md`, `PORTFOLIO_PROPOSAL_REGISTRY_GUIDE.md`, `RUNTIME_ARTIFACT_HYGIENE.md` |
| 작업 로그 정책 | `FINANCE_WORK_PROGRESS_POLICY.md` |
| 설정 / 운영 준비 | `CONFIG_EXTERNALIZATION_INVENTORY.md` |
| 데이터 수집 운영 | `DATA_COLLECTION_UI_STRATEGY.md`, `OHLCV_AND_FINANCIAL_INGESTION_REVIEW.md` |
| Daily market update | `daily_market_update/` |

## 관리 기준

- 루트 `.note/finance/`에는 상위 지도, 활성 로그, 템플릿만 둔다.
- 운영성 문서는 이 폴더로 모은다.
- 코드 수정 흐름은 `../code_analysis/`를 우선한다.
- DB / data 의미는 `../data_architecture/`를 우선한다.
