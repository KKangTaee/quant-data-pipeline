# Economic Cycle Usability Follow-up V2 Plan

State: active
Last Updated: 2026-08-04

## 이걸 하는 이유?

Observed-state V1은 미래 확률을 제거하고 현재 국면과 조건부 전환을 분리했지만,
실사용 화면에는 네 가지 해석 문제가 남아 있다.

- 수동 Freshness 확인이 약 1분 동안 동기 실행되며 화면이 멈춘 것처럼 보인다.
- Actual Cycle Map이 12개 좌표를 모두 연결해 핵심 변화보다 월별 잡음을 강조한다.
- 현재 관측이 `위축`인데 전환 앵커 `회복 → 확장`이 주 정보로 보여 확장 예측처럼
  읽힌다.
- 12개월 리본의 색상과 각 월의 국면을 사용자가 직접 해석하기 어렵다.

이번 후속 작업은 계산 근거를 숨기지 않으면서 현재 관측을 첫 판단으로 만들고,
구조적 다음 국면과 모델 앵커를 예측과 명확히 분리한다.

## Roadmap

### 1차 — Runtime / contract diagnosis

- 최근 수동 실행 로그, 현재 월말·월중 snapshot, transition monitor를 대조한다.
- 완료 조건: 실패인지 지연인지, current/anchor/target 조합이 계산 오류인지 표현
  문제인지 근거로 구분한다.

### 2차 — User-facing meaning design

- current-observed-first 전환 카드와 네 지점 Actual Cycle Map을 확정한다.
- Freshness의 확인일·계산일·원천 관측일을 분리한다.
- 완료 조건: 사용자가 `현재 위축`, `앵커 회복`, `구조적 목표 확장`의 의미를
  혼동하지 않는다.

### 3차 — TDD implementation / Browser QA

- domain metadata, service normalization, React UI와 CSS를 테스트 우선으로 수정한다.
- production component를 다시 빌드하고 실제 Streamlit 화면을 검증한다.
- 완료 조건: Python/React 테스트와 build가 통과하고 desktop Browser QA에서 네
  이슈가 재현되지 않는다.

## Scope

- `finance/economic_cycle_observed_state.py`
- `app/services/overview/economic_cycle.py`
- `app/services/overview/economic_cycle_freshness.py`
- `app/web/streamlit_components/economic_cycle_workbench/src/`
- 관련 Python / React tests와 production component build
- 이 active task의 설계·실행·위험 기록

## Frozen Scope

- `market_implications` payload 계약
- `MarketImplicationCard` 이하 `자산별 확인 포인트` markup, copy, CSS
- 자산별 계산·가격·관찰 경로·향후 확인 조건

## Out Of Scope

- FRED/ALFRED provider 교체
- 비동기 queue 또는 별도 운영 job 화면
- 새로운 미래 확률 모델
- 기존 월말 snapshot의 대규모 DB migration
- 포트폴리오 추천 또는 자동 행동

## Stop Condition

Freshness 의미와 대기 피드백, 6·3·1개월 전/현재 지도, current-first 전환 설명,
네 국면 범례와 월별 tooltip이 한 화면에서 검증되고 자산 영역이 그대로 유지되면
완료한다.
