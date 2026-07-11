# Design

## 화면 구조

```text
Sector Breadth
├─ 고정 헤더 · 상태
├─ 현재 확산 결과 · 핵심 통계
├─ 섹터별 방향성 lane
└─ 안내 · 상세 표

종목 조사 워크스페이스 ───────── 선택 순위
│
├─ 종목 선택
├─ 선택 종목 요약 · 조회 버튼
└─ 조사 단서
   ├─ 기본 지표
   │  ├─ Research Snapshot
   │  └─ 기본 지표 그래프
   └─ 시장 관심
```

## 코드 소유 경계

- React Sector Breadth: `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx`, `style.css`
- Streamlit 흐름/부모 container: `app/web/overview/market_movers_helpers.py`
- HTML fallback/shared styling: `app/web/overview/components/market_movers.py`, `common.py`
- 회귀 계약: `tests/test_service_contracts.py`

## 시각 원칙

- Sector outer surface는 공통 primary tone을 2~3%만 혼합해 영역을 묶는다.
- 각 sector lane은 자체 tone을 4% 혼합하고 현재 30% tone border와 bar는 유지한다.
- 종목 조사 workspace는 외곽 박스 1개를 주 경계로 쓰고, 내부 컴포넌트는 얇은 구분선과 간격을 우선한다.
- 안전 안내와 상세 표는 중립 배경을 유지해 방향성 색과 의미를 섞지 않는다.
