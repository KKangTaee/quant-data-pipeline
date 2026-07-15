# Overview Market Context US Stock Freshness Refresh V1 Design

Status: Approved for Implementation
Last Updated: 2026-07-15

## 이걸 하는 이유?

미국 개별주식의 PER 상대가치와 전환 분석은 화면 진입 시 DB만 읽는다. 이 경계는 안전하지만 선택 종목의 가격·시장가치 snapshot이 뒤처지면 사용자는 오래된 기준일만 보고, 어떤 자료를 갱신해야 하는지 알 수 없다. Cloudflare actual DB에서는 가격이 `2026-07-07`, 시장가치 snapshot이 `2026-02-04`여서 전환 가치평가가 `INPUT_STALE`로 막혔지만, 현재 turnaround collection plan은 SEC CIK가 없다는 이유로 CIK가 필요 없는 profile/가격 갱신까지 차단한다.

V1은 선택 종목 상단에 하나의 `최신 데이터로 다시 계산` action을 두고, repairable freshness gap만 selected-symbol 범위로 수집한 뒤 PER와 전환 분석을 함께 다시 읽는다.

## 승인된 사용자 의도

- PER와 전환 분석에 각각 수집 버튼을 두지 않는다.
- 선택 종목 상단에 하나의 공통 action을 둔다.
- 기준일이 실제 최신 완료 거래일보다 뒤처지거나 시장가치와 가격 basis가 어긋난 경우에만 action을 보여준다.
- 클릭 전에는 provider를 호출하지 않는다.
- 클릭 후에는 필요한 범위만 수집하고 같은 종목의 두 분석을 함께 다시 계산한다.

## 범위

### 포함

- 마지막 완료 NYSE session 기반 price freshness 판정
- profile/시장가치 snapshot과 latest price의 7일 alignment 판정
- 기존 PER·turnaround raw statement gap의 unified selected-symbol collection plan
- profile/price scope는 SEC CIK 없이 수집
- SEC statement scope만 CIK 확인·보강 후 실행
- 선택 종목 상단 single CTA, scope-aware 설명, rerun 후 결과 반영
- PER는 `가격 기준일`, turnaround는 `재무 기준일`과 filing 공개일/가격 기준을 구분 표시

### 제외

- 화면 진입·검색·종목 선택 시 자동 수집
- 전체 미국주식 일괄 최신화
- 새 DB table 또는 market-cap materialization
- provider run/job/row 진단 dashboard
- 아직 발표되지 않은 다음 분기를 stale로 간주하는 filing calendar 추정
- stale raw gap을 임의 보간하거나 PER/valuation gate를 낮추는 처리

## 검토한 접근

### A. PER와 전환 분석에 각각 버튼 유지

- 장점: 기존 action을 거의 그대로 재사용한다.
- 단점: 같은 profile/가격을 두 번 수집할 수 있고, 현재 선택한 분석에 따라 freshness 결과가 달라 보인다.
- 판정: 채택하지 않는다.

### B. 선택 종목 상단 unified refresh action — 채택

- 장점: 사용자는 한 번만 갱신하고 두 분석이 같은 DB snapshot을 다시 읽는다. exact scope dedup과 partial retry도 한 곳에서 관리한다.
- 단점: 두 기존 collection plan을 합치는 명시적 freshness contract가 필요하다.
- 판정: 사용자 승인 방향이며 V1로 채택한다.

### C. 종목 선택 시 자동 갱신

- 장점: 사용자가 stale 화면을 덜 본다.
- 단점: 검색/선택 read-only 계약을 깨고 provider 비용·지연·재실행을 사용자가 통제할 수 없다.
- 판정: 채택하지 않는다.

## Freshness 의미

### 가격

- `expected_price_date`는 미국 동부시간 기준 마지막 완료 NYSE session이다.
- 주말·휴장·장중에는 직전 완료 session을 사용한다.
- `latest_price_date < expected_price_date`일 때만 `prices` scope를 repairable gap으로 둔다.
- 단순히 `latest_price_date != 오늘`이라는 이유로 stale 처리하지 않는다.

### 시장가치/profile

- V1은 기존 `nyse_asset_profile.last_collected_at`을 market-cap snapshot basis로 사용한다.
- market cap이 없거나 profile basis와 latest price date가 7일 넘게 벌어지면 `asset_profile` scope를 추가한다.
- 별도 provider basis date가 없는 한 collection timestamp를 snapshot basis로 쓴다는 한계를 화면/문서에 남긴다.

### 재무제표

- latest quarter의 `period_end`가 오늘보다 과거라는 이유만으로 stale 처리하지 않는다.
- 기존 PER/turnaround coverage가 실제 raw statement gap을 판정한 경우에만 `sec_statements` scope를 추가한다.
- `statement_period_end`와 `statement_available_at`을 별도로 표시해 결산일과 공개일을 혼동하지 않게 한다.

## Unified Read Model

combined U.S.-stock payload에 아래 summary를 추가한다.

```python
{
    "data_freshness": {
        "status": "READY | REFRESH_AVAILABLE | PARTIAL | BLOCKED",
        "expected_price_date": "YYYY-MM-DD",
        "price_basis_date": "YYYY-MM-DD | None",
        "profile_basis_date": "YYYY-MM-DD | None",
        "statement_period_end": "YYYY-MM-DD | None",
        "statement_available_at": "YYYY-MM-DD | None",
        "gaps": [
            {
                "scope": "prices | asset_profile | sec_identity | sec_statements",
                "reason_code": "...",
                "repairable": True,
            }
        ],
        "action": {
            "id": "refresh_us_stock_data",
            "label": "최신 데이터로 다시 계산",
            "symbol": "NET",
            "scopes": ["asset_profile", "prices"],
            "enabled": True,
        },
    }
}
```

- action은 repairable scope가 있을 때만 존재한다.
- structural short listing, non-positive EPS, unsupported valuation sector는 refresh scope가 아니다.
- 기존 PER/turnaround payload field와 legacy collection action은 service compatibility를 위해 유지할 수 있지만 current React는 unified action만 사용한다.

## 수집 경계

```text
selected stock DB read
  -> PER plan + turnaround plan + latest completed NYSE session
  -> unified exact scopes
  -> no gap: button 없음
  -> repairable gap: refresh_us_stock_data CTA

explicit click
  -> selected symbol/event nonce 검증
  -> profile/price scopes 먼저 실행 (CIK 불필요)
  -> SEC scope가 있으면 identity refresh/recheck
  -> CIK 확인 시 statements 실행
  -> CIK 미확인 시 market scope 성공은 보존하고 SEC만 remaining gap
  -> DB cache clear
  -> same selected symbol rerun
  -> PER + turnaround read model 동시 갱신
```

CIK 검증은 symbol validation을 대체하지 않는다. 모든 scope는 exact selected symbol만 실행하고, SEC scope에서만 selected symbol/CIK identity equality를 요구한다.

## 화면 설계

선택 종목 카드와 분석 header 사이에 compact freshness bar를 둔다.

```text
자료 기준  가격 2026-07-07 · 시장가치 2026-02-04 · 재무 2026-03-31 (공개 2026-05-08)
최신 완료 거래일 2026-07-14 대비 가격 자료가 뒤처졌습니다.   [최신 데이터로 다시 계산]
```

- CTA는 PER/전환 selector 바깥에 있어 어느 분석을 보고 있어도 동일하다.
- 실행 중에는 같은 버튼만 disabled/`갱신 중`으로 바뀐다.
- rerun 후 READY면 버튼을 제거하고 최신 basis를 표시한다.
- partial이면 성공한 시장 자료는 즉시 반영하고 남은 SEC identity/statement 이유만 짧게 설명한다.
- 별도 job/row/status 결과 패널을 새로 만들지 않는다. 사용자가 확인할 결과는 갱신된 기준일과 분석 상태다.
- 기존 generic `기준일`은 PER에서 `가격 기준일`, turnaround에서 `재무 기준일`로 바꾼다.

## 오류와 부분 성공

- profile 성공 + price 실패: profile 저장을 보존하고 price scope만 다음 action에 남긴다.
- profile/price 성공 + CIK 실패: market data를 반영하고 SEC gap만 `BLOCKED`로 설명한다.
- provider가 최신 row를 주지 않음: action을 계속 노출하되 exact remaining date/reason을 표시한다.
- no-op READY click은 provider를 호출하지 않고 성공 상태로 종료한다.
- 잘못된 symbol/event 또는 같은 nonce 재전송은 실행하지 않는다.

## 코드 소유 경계

- shared NYSE session helper: 기존 `app/services/backtest_price_refresh.py`의 완료 session 계산을 공용 경계로 추출하고 backtest/Market Context가 재사용한다.
- freshness/collection planner: selected-stock PER와 turnaround plan을 합치는 새 loader/service helper.
- ingestion: profile/price는 symbol validation만, statement는 CIK identity validation을 요구하는 selected-stock unified job.
- overview action/event: single `refresh_us_stock_data` facade와 nonce-dedup event.
- React: unified freshness bar, scope-aware CTA, basis label 분리.
- tests: pure freshness calendar, exact scope/CIK boundary, partial retry, read-only render, event dedup, React source/build, actual Browser QA.

## Tentative Roadmap

### 1차 — 최신성 판정과 수집 경계 분리

- 마지막 완료 NYSE session과 exact price/profile/statement gap을 pure/query-spy tests로 고정한다.
- profile/price가 CIK 없이 실행되고 statement만 CIK를 요구하도록 low-level boundary를 분리한다.

완료 조건: NET-like `profile stale + price stale + CIK missing` plan이 `asset_profile/prices`를 수집 가능하게 반환하고 SEC scope만 별도로 차단한다.

### 2차 — 상단 single CTA와 공동 재계산

- unified read model/action/event/facade를 연결한다.
- PER/전환 selector 밖에서 한 버튼으로 수집하고 두 분석을 함께 rerun한다.
- basis label을 가격/재무/공개일로 분리한다.

완료 조건: 검색·선택·분석 전환은 provider call 0회이고 explicit click 한 번만 exact scopes를 실행한다.

### 3차 — Actual QA · Docs · Closeout

- NET actual DB preflight와 explicit selected-symbol collection을 검증한다.
- desktop/420px Browser QA로 button visibility, no duplicate action, refreshed basis, remaining gap, console/overflow를 확인한다.
- focused/isolated full/build/compile과 durable docs sync를 수행한다.

완료 조건: stale selected stock은 한 CTA로 repairable market data를 갱신하고, READY에서는 버튼이 사라지며, 남은 structural/SEC gap을 정확히 구분한다.

## 중요한 Tradeoff

- provider market cap은 collection timestamp 외 별도 basis date가 없을 수 있다. V1은 이를 명시하고 7일 alignment gate를 유지한다.
- 최신 price를 수집해도 provider delay나 휴장 때문에 expected session을 채우지 못할 수 있다. 이때 gate를 낮추지 않고 remaining gap을 유지한다.
- SEC filing freshness calendar를 추정하지 않는다. 실제 stored raw coverage gap만 수집 대상으로 삼는다.
- unified action은 user workflow를 단순화하지만, 기존 두 plan의 compatibility contract는 회귀 테스트로 보존해야 한다.

## Acceptance Criteria

- selected stock에 repairable freshness gap이 있을 때만 상단 CTA 하나가 보인다.
- CTA label은 `최신 데이터로 다시 계산`이다.
- profile/price 수집은 CIK가 없어도 가능하다.
- SEC statement 수집만 CIK identity를 요구한다.
- 새 action은 selected symbol 하나만 수집하고 rerun 후 PER/turnaround를 함께 갱신한다.
- 주말·휴장·장중을 stale로 오판하지 않는다.
- generic basis date를 가격/재무/공개일로 분리한다.
- 자동 fetch, broad-universe refresh, 새 진단 패널, schema/table 추가가 없다.
