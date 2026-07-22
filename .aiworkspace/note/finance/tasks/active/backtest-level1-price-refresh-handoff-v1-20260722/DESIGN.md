# Level1 Price Refresh Handoff V1 Design

Status: User-approved design direction; written spec review pending
Date: 2026-07-22

## 1. 문제 정의

사용자가 Level1 검증 종료일을 `2026-07-22`로 선택해도 포트폴리오 계산에 필요한 일부 종목의 DB 가격이 그 시점까지 없으면 전략은 사용 가능한 공통 날짜까지만 계산한다. 이 보수적 교집합 계산은 맞지만, 현재 Result Workspace는 다음 행동을 제공하지 않는다.

- 요청 종료일과 실제 공통 계산일의 차이를 first-read에서 설명하지 않는다.
- 기존 `Coverage 최신화` service와 action card는 legacy `_render_last_run_details()`에 연결되어 있고 current Result Workspace에서는 호출되지 않는다.
- current React Result Workspace intent는 `save_and_move`만 지원한다.
- 따라서 가격이 오래된 결과도 lifecycle이 `fresh`이면 Level2 인계가 가능하다.

## 2. 확인된 현재 상태

2026-07-22 13:00 KST 기준 마지막 완료 NYSE 거래일은 `2026-07-21`이다. GTAA 기본 12개 위험자산과 현금 대체자산 `BIL`을 실제 DB에서 점검한 결과는 다음과 같다.

- 요청 종료일: `2026-07-22`
- freshness 목표 거래일: `2026-07-21`
- 공통 최신 가격일: `2026-06-26`
- 최신 가격일: `2026-07-21`
- stale 종목: 11개
- 기존 refresh plan: `refresh_available`
- 수집 범위: `2026-06-27`부터 `2026-07-21`

기존 `app/services/backtest_price_refresh.py`는 대상 종목만 기존 `run_collect_ohlcv()`에 전달하고 DB `finance_price.nyse_price_history`에 저장할 수 있다. 신규 collector는 필요하지 않다.

## 3. 확정된 제품 결정

1. 데이터 최신화는 사용자가 명시적으로 누르는 수동 action이다.
2. 최신화 성공 직후 백테스트를 자동 실행하지 않는다.
3. 기존 결과는 `가격 갱신 전 결과 · 참고용`으로 전환한다.
4. 사용자가 `같은 설정으로 다시 백테스트`를 눌러 새 결과를 만든다.
5. 보강 필요 상태와 보강 후 재실행 전 상태에서는 Level2 인계를 차단한다.
6. 마지막 완료 NYSE 거래일보다 미래인 달력 날짜를 수집 목표로 삼지 않는다.
7. 화면은 raw job / row 진단이 아니라 `왜 결과가 짧은가`, `어떤 행동이 필요한가`, `언제 Level2로 갈 수 있는가`를 우선 설명한다.

## 4. 고려한 접근

### A. Current Result Workspace 정식 통합 — 채택

현재 Python read model, React renderer, fallback, intent consumer에 freshness action을 같은 계약으로 추가한다. Single Strategy와 Portfolio Mix가 동일한 사용자 흐름을 사용하며 legacy UI를 되살리지 않는다.

### B. GTAA 전용 hotfix — 기각

빠르지만 동일 문제가 다른 가격 기반 전략과 Portfolio Mix에서 반복되고, 공통 Result Workspace 소유 경계를 어긴다.

### C. Legacy Data Trust block 복원 — 기각

기존 action을 즉시 재사용할 수 있지만 신·구 결과 화면이 중복되고 current one-shell UX를 훼손한다.

## 5. 아키텍처

### 5.1 가격 최신성 입력 구성

Result Workspace의 web adapter가 current bundle에서 refresh meta를 만든다.

- Single Strategy
  - runtime `meta.price_freshness`
  - 입력 Universe ticker
  - 현금 대체자산
  - 전략 결과 재현에 필요한 ticker Benchmark / guardrail reference
- Portfolio Mix
  - component bundle들의 ticker 합집합
  - component별 현금 / Benchmark / guardrail reference 합집합
  - component price freshness의 stale / missing symbol 합집합
  - 가장 늦은 component requested end가 아니라 current Mix configuration의 end
  - current Mix configuration에 end가 없을 때만 weighted result meta의 requested end를 fallback으로 사용

종목은 대문자 정규화 후 중복을 제거한다. 실제 refresh 가능 대상은 기존 `build_backtest_price_refresh_plan()`이 결정한다. provider/source gap과 active ticker repair 정책도 기존 service 계약을 유지한다.

Result Workspace service는 Streamlit-free pure read model로 유지한다. Web adapter가 refresh meta를 구성하고 `build_backtest_price_refresh_plan()`을 호출한 뒤 JSON-ready plan과 현재 session의 refresh result만 read model에 주입한다. 따라서 `app/services/backtest_analysis_result_workspace.py`는 DB 연결이나 ingestion job을 직접 호출하지 않는다.

### 5.2 날짜 판정

두 날짜를 분리한다.

- `requested_end`: 사용자가 선택한 달력 종료일
- `target_trading_end`: `requested_end` 이하이면서 현재 시각 기준 마지막으로 완료된 NYSE 거래일

다음 조건이면 보강이 필요하다.

```text
current_common_latest < target_trading_end
```

주말, 휴장일, 아직 종료되지 않은 미국 거래일은 결측으로 오판하지 않는다. 결과 curve의 마지막 날짜만으로 판정하지 않고 runtime의 symbol별 freshness evidence와 공통 최신일을 우선한다.

### 5.3 Result Workspace read model

`backtest_analysis_result_workspace_v1`에 사용자-facing `data_freshness_action`을 추가한다.

예상 필드:

```text
state: current | refresh_required | provider_gap | rerun_required
requested_end
target_trading_end
current_common_latest
affected_symbol_count
affected_symbol_sample
summary
guidance
refresh_action
rerun_action
handoff_blocked
```

raw `price_freshness`와 job result는 technical appendix에 보존하되 first-read card에는 사용자 문구만 표시한다.

### 5.4 Lifecycle과 Level2 Gate

Level1 technical readiness는 다음 순서로 판정한다.

1. 핵심 result contract 존재 여부
2. configuration fingerprint 일치 여부
3. 가격 보강 필요 여부
4. 가격 보강 후 재실행 필요 여부
5. `save_and_move` handler 존재 여부

상태별 정책:

| 상태 | 결과 표시 | 최신화 | 같은 설정 재실행 | Level2 인계 |
|---|---|---|---|---|
| `current` | 현재 결과 | 숨김 | 숨김 | 기존 gate 적용 |
| `refresh_required` | 참고 가능 | 활성 | 숨김 | 차단 |
| `provider_gap` | 참고 가능 | 반복 action 숨김 | 설정 수정 안내 | 차단 |
| `rerun_required` | 가격 갱신 전 결과 | 숨김 | 활성 | 차단 |

최신화 결과에 저장 row가 하나라도 있으면 기존 결과는 `rerun_required`가 된다. 사용자가 같은 설정으로 다시 실행한 뒤 새 runtime freshness를 기준으로 남은 refreshable gap은 `refresh_required`, provider/source gap만 남으면 `provider_gap`으로 다시 판정한다. 저장 row가 0이고 unresolved symbol이 있으면 즉시 `provider_gap` 또는 수동 확인 상태로 전환해 같은 refresh action을 반복 노출하지 않는다. 새 실행이 최신 freshness 계약을 통과해야만 `current`가 된다.

### 5.5 Intent와 실행 경계

React는 아래 intent만 전송한다.

- `refresh_prices`
- `rerun_same_configuration`
- 기존 `save_and_move`

Python consumer는 모든 mutation 전에 다음을 다시 검증한다.

- nonce 미소비
- current `run_result_id` 일치
- current configuration fingerprint 일치
- 해당 action이 current read model에서 enabled
- refresh plan이 여전히 eligible

`refresh_prices`는 기존 `run_backtest_price_refresh()`만 호출한다. UI나 React가 provider를 직접 호출하지 않는다.

`rerun_same_configuration`은 저장된 result meta를 재구성하지 않고 current Python-owned draft를 사용한다.

- Single Strategy: `backtest_current_draft_payload`와 current strategy selection으로 기존 pending-run 경로를 사용한다.
- Portfolio Mix: current mix configuration과 기존 `run_current_portfolio_mix` 경로를 사용한다.

### 5.6 UI 배치

freshness card는 Result Header 바로 아래, 성과 요약보다 먼저 표시한다. 오래된 결과를 읽기 전에 데이터 기준과 다음 행동을 먼저 알 수 있어야 한다.

표시 내용:

- 제목: `요청 종료일 기준 데이터가 부족합니다`
- 요청 종료일
- 목표 거래일
- 현재 공통 기준일
- 최신화 대상 종목 수
- 한 문장 영향 설명
- primary action 하나

업데이트 전 primary action은 `종목 데이터 최신화`, 업데이트 성공 후 primary action은 `같은 설정으로 다시 백테스트`다. raw rows-written, job name, target table은 first-read에 표시하지 않는다.

React build가 없을 때 Python fallback도 같은 read model과 동일한 차단 정책을 사용한다.

## 6. 오류 처리

- 수집 성공 + 저장 row 존재: old result를 reference-only로 전환하고 재실행 action 표시
- 부분 성공: 성공/미해결 종목을 사용자 문구로 요약하고 Level2 차단 유지
- 저장 row 0 + unresolved 존재: 동일 refresh 버튼을 반복 노출하지 않고 provider/source 확인 또는 Universe 조정 안내
- collector 예외: 마지막 성공 결과는 유지하고 오류를 card 안에서 설명하며 Level2 차단 유지
- active ticker resolution 존재: 기존 source/resolved split contract를 보존하고 collection symbol만 전환
- 중복 component event: nonce로 한 번만 소비

## 7. 테스트 전략

### Pure contract tests

- `2026-07-22` 요청이 완료 거래일 `2026-07-21`로 변환된다.
- common latest가 목표보다 이르면 `refresh_required`다.
- current이면 freshness card가 없고 기존 handoff gate가 유지된다.
- refresh required / provider gap / rerun required는 모두 Level2를 차단한다.
- Single Strategy가 Universe + cash + required benchmark를 포함한다.
- Portfolio Mix가 component symbol을 합집합·중복 제거한다.

### Intent tests

- 잘못된 run id / fingerprint / nonce action은 실행되지 않는다.
- eligible refresh만 기존 runner를 한 번 호출한다.
- 저장 row가 있으면 old result가 rerun-required가 된다.
- 같은 설정 재실행은 current draft / mix configuration을 사용한다.
- refresh 전후 `save_and_move`는 호출되지 않는다.

### UI contract / Browser QA

- React와 fallback이 같은 문구·action·blocker를 표시한다.
- GTAA actual `2026-07-22` 요청에서 대상 수와 날짜가 실제 DB plan과 일치한다.
- 최신화 후 `같은 설정으로 다시 백테스트`가 표시된다.
- 재실행 후 최신 상태가 되면 freshness card가 사라지고 Level2 인계가 열린다.
- desktop 1280px, compact 760px에서 overflow가 없다.
- application console error가 없다.

## 8. 예상 파일 범위

- `app/services/backtest_analysis_result_workspace.py`
- `app/services/backtest_price_refresh.py` — public adapter가 필요한 경우에만 최소 변경
- `app/web/backtest_analysis_result_workspace.py`
- `app/web/backtest_analysis_result_workspace_panel.py`
- `app/web/backtest_analysis_workspace.py` 또는 existing pending-run owner
- `app/web/components/backtest_analysis_result_workspace/frontend/src/types.ts`
- `app/web/components/backtest_analysis_result_workspace/frontend/src/BacktestAnalysisResultWorkspace.tsx`
- `app/web/components/backtest_analysis_result_workspace/frontend/src/style.css`
- focused service / boundary / visual contract tests

Legacy `_render_last_run_details()`를 primary route로 복원하지 않는다. Registry, saved portfolio, run history generated row는 구현 커밋에 포함하지 않는다.

## 9. 완료 조건

- 실제 데이터 기준으로 보강 필요 여부와 대상 종목이 정확하다.
- 사용자는 결과 상단에서 원인과 다음 행동을 즉시 이해한다.
- 수동 최신화는 기존 ingestion → DB 경계를 따른다.
- 자동 백테스트는 실행되지 않는다.
- 새 실행 전까지 Level2 인계가 불가능하다.
- 새 실행이 최신 기준을 통과하면 기존 결과 workflow가 정상적으로 이어진다.
