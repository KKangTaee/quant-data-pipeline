# Economic Cycle Multichannel Asset Interpretation Design

Status: Draft for written review
Design approved in conversation: 2026-07-17
Implementation scope: roadmap stages 1-2

## 이걸 하는 이유

현재 경제사이클 자산 카드는 미국 경제지표를 자산가격의 기준 방향으로 번역한 뒤 실제 가격과 `같은 방향 / 서로 다른 방향`으로 비교한다. 이 구조는 간단하지만 `미국 경제상태상 금이 올라야 하는데 실제 가격은 하락했다`처럼 읽히기 쉽다.

자산가격은 금리, 실질금리, 달러, 위험회피, 상대수익률, 수급 등 여러 경로가 동시에 작용한 결과다. 따라서 미국 경제상태를 정답으로 두지 않고, 현재 저장 데이터로 측정할 수 있는 전달경로와 실제 가격 움직임을 나란히 설명하는 구조로 바꾼다.

이 기능은 가격 원인을 증명하거나 수익률을 예측하지 않는다. 사용자가 다음 질문에 답할 수 있게 하는 것이 목적이다.

1. 현재 미국 경제지표에서는 무엇이 관측됐는가?
2. 자산과 관련된 측정 가능한 시장 경로는 어느 방향으로 움직였는가?
3. 실제 자산가격은 어느 방향으로 움직였는가?
4. 어떤 중요한 경로는 아직 측정하지 못했는가?

## 핵심 원칙

### 경제상태는 관측값이지 자산가격의 정답이 아니다

생산·소비, 고용·소득, 금융·선행, 물가·정책 factor는 카드 상단의 `관측된 경제 상태`에 표시한다. 이 값을 바로 `금을 지지`, `달러에 부담`으로 변환하지 않는다.

예를 들어 경기지표가 약화됐다는 사실만으로 `금리 인하 기대가 금을 지지한다`고 쓰지 않는다. 실제 단기 국채금리 경로가 함께 낮아졌을 때만 `단기금리 경로가 금의 지지 방향과 함께 관측됐다`고 표현한다.

### 측정 가능한 데이터만 설명한다

- 저장된 정량 데이터가 없는 뉴스·지정학은 현재 기능 범위에서 제외한다.
- ETF·중앙은행 수급은 신뢰 가능한 저장 원천을 별도로 승인한 뒤 추가할 후속 후보로 둔다.
- 데이터가 없거나 오래됐으면 방향을 추정하지 않고 `미측정`으로 표시한다.
- 누락값을 보간하거나 직전 값으로 채워 방향을 만들지 않는다.

### 동행을 인과로 표현하지 않는다

허용 문장:

- `금 가격 하락과 함께 실질금리 상승이 관측됐습니다.`
- `측정된 경로 중 실질금리·달러 부담 방향에 더 가깝습니다.`
- `달러를 지지할 수 있는 미국 금리 경로가 관측됐지만 상대국 금리 경로는 측정하지 않았습니다.`

금지 문장:

- `실질금리 상승이 금 하락을 만들었습니다.`
- `달러 상승 원인은 고금리입니다.`
- `이 경로가 맞을 확률은 70%입니다.`

### 하나의 종합 점수로 다시 압축하지 않는다

상승 방향 경로, 하락 방향 경로, 중립·혼재 경로, 미측정 경로를 분리해 보여준다. `우호 2개 - 부담 1개 = 상승` 같은 합산 점수나 매수·매도 결론을 만들지 않는다.

## 전체 로드맵

### 1차 — 공통 해석 기반

- 신규 FRED 시계열 수집과 DB 저장
- 기간 변화, 물질성, 신선도, 경로 상태, 데이터 범위 공통 계약
- 원인 단정 없이 정량 결과를 문장으로 바꾸는 공통 narrative 계약

### 2차 — 금·달러 파일럿

- 금의 실질금리·달러·단기금리·위험회피 경로
- 달러의 미국 금리·실질금리·위험회피 경로
- 달러의 해외 상대금리 미측정 사실 공개
- 승인된 흰색 다중 경로 카드 UI

### 3차 — 채권·금리

- 2년물과 10년물을 분리
- 금리 수준·변화·장단기 스프레드 설명

### 4차 — 주식

- 지수가격과 실질금리·신용스프레드·변동성·이익 경로 연결

### 5차 — 원자재

- 원유 하나로 대표하지 않고 에너지·산업금속·귀금속 등으로 분리

이번 명세와 이어지는 구현 계획은 1·2차만 소유한다. 3~5차는 파일럿의 실제 데이터와 화면 QA가 통과한 뒤 별도 명세로 확장한다.

## 아키텍처 경계

```text
FRED / 기존 가격 수집
  -> finance_meta / finance_price DB
  -> DB loader
  -> 공통 시계열·경로 evaluator
  -> deterministic narrative builder
  -> Overview service read model
  -> Economic Cycle React UI
```

- UI는 FRED나 가격 provider를 직접 호출하지 않는다.
- 신규 시계열도 기존 `Ingestion -> DB -> Loader -> UI` 경계를 따른다.
- API key는 환경변수로만 읽으며 코드, 문서, payload에 저장하지 않는다.
- 경제사이클 확률 모델과 publication gate는 변경하지 않는다.
- 자산 경로 read 실패가 경제사이클 확률이나 다른 화면 렌더링을 막지 않는다.

## 데이터 계약

### 신규 수집 시계열

| Series | 의미 | 저장 위치 | 단위 | 사용처 |
|---|---|---|---|---|
| `DGS2` | 미국 2년 국채 수익률 | `finance_meta.macro_series_observation` | percent | 단기금리·미국 금리 경로 |
| `DGS10` | 미국 10년 국채 수익률 | `finance_meta.macro_series_observation` | percent | 장기금리·미국 금리 경로 |
| `DFII10` | 미국 10년 물가연동국채 실질수익률 | `finance_meta.macro_series_observation` | percent | 실질금리 경로 |

### 기존 사용 데이터

| 데이터 | 의미 | 역할 |
|---|---|---|
| `VIXCLS` | 주식시장 변동성 | 위험회피 경로 |
| `BAA10Y` | Baa 회사채-10년 국채 스프레드 | 위험회피·신용 경로 |
| `GC=F` | 금 연속선물 일봉 | 실제 금 가격 |
| `DX-Y.NYB` | 달러인덱스 연속선물 일봉 | 실제 달러 가격, 금의 달러 경로 |
| 경제사이클 canonical factors | 생산·소비, 고용·소득, 금융·선행, 물가·정책 | 관측된 경제 상태 |

`GC=F`와 `DX-Y.NYB`는 연속선물이므로 계약 교체 효과가 포함될 수 있음을 UI 제한 문구에 유지한다.

### 기준일 계약

- 경제상태는 `economic_as_of_date`를 가진다.
- 각 시장 시계열과 가격은 자체 `as_of_date`를 가진다.
- 기본 live 화면은 최신 materialized 경제 snapshot과 오늘까지 저장된 시장 데이터를 사용하고 두 기준일을 분리 표시한다.
- 호출자가 과거 `as_of_date`를 명시한 historical read에서는 시장 loader도 해당 날짜 이후의 관측값을 사용하지 않는다.
- 물질성 기준 계산도 reference date 이후 데이터를 포함하지 않는다.

## 기간 변화와 물질성

### 관측 기간

- `5거래일`: 단기 맥락만 표시
- `21거래일`: 1개월 경로 판정
- `63거래일`: 3개월 경로 판정

가격·지수는 퍼센트 수익률로 계산한다.

```text
return_pct = (latest / lagged - 1) * 100
```

금리·실질금리·스프레드는 basis point 변화로 계산한다.

```text
change_bp = (latest - lagged) * 100
```

### 작은 변화의 중립 처리

아주 작은 변화를 방향으로 과장하지 않기 위해 고정 임계값 대신 각 시계열의 과거 변동 분포를 사용한다.

1. reference date 이전 최근 5년의 동일 horizon 절대변화를 계산한다.
2. 절대변화의 중앙값을 해당 horizon의 materiality threshold로 둔다.
3. 현재 절대변화가 threshold보다 작으면 `NEUTRAL`이다.
4. 최소 252개의 유효한 historical horizon change가 없으면 threshold를 만들지 않고 `INSUFFICIENT_HISTORY`로 제한한다.

중앙값과 최소 표본 수는 이름 있는 상수로 두어 테스트하고, UI에는 복잡한 통계값 대신 `통상 변동보다 큼 / 작음`으로 번역한다.

### 시계열 horizon 상태

각 21·63거래일 변화는 다음 중 하나다.

- `UP`: 양수이며 material
- `DOWN`: 음수이며 material
- `NEUTRAL`: materiality threshold 미만
- `UNAVAILABLE`: 값·이력·신선도 부족

## 경로 판정 계약

경로 상태는 자산가격 방향과의 경제적 관계를 표현하며 다음 중 하나다.

- `SUPPORTS_RISE`: 21·63거래일 모두 해당 자산의 상승 지지 방향
- `SUPPORTS_FALL`: 21·63거래일 모두 해당 자산의 하락 지지 방향
- `MIXED`: 두 기간 방향이 반대이거나 복수 구성 시계열이 충돌
- `NEUTRAL`: 한 기간 이상이 통상 변동보다 작아 안정적인 방향을 부여하지 않음
- `UNAVAILABLE`: 데이터·이력·신선도 부족

5거래일 변화는 위 상태를 뒤집지 않으며 hover/tap의 단기 맥락으로만 사용한다.

### 금 경로

| 경로 | 측정값 | `SUPPORTS_RISE` | `SUPPORTS_FALL` | 비고 |
|---|---|---|---|---|
| 실질금리 | `DFII10` | 실질금리 하락 | 실질금리 상승 | 핵심 경로 |
| 달러 | `DX-Y.NYB` | 달러 하락 | 달러 상승 | 핵심 경로 |
| 단기금리 | `DGS2` | 2년물 하락 | 2년물 상승 | `정책금리 기대`가 아니라 관측된 2년물 경로로 표현 |
| 위험회피 | `VIXCLS`, `BAA10Y` | 두 지표가 모두 상승 | 두 지표가 모두 하락 | 불일치하면 `MIXED` |

경제사이클 factor 약화 자체는 금 상승 경로로 분류하지 않는다. 카드의 경제상태 영역에만 사실로 표시한다.

### 달러 경로

| 경로 | 측정값 | `SUPPORTS_RISE` | `SUPPORTS_FALL` | 비고 |
|---|---|---|---|---|
| 미국 명목금리 | `DGS2`, `DGS10` | 두 금리 상승 | 두 금리 하락 | 상대금리가 아니므로 조건부 표현 |
| 미국 실질금리 | `DFII10` | 실질금리 상승 | 실질금리 하락 | 조건부 표현 |
| 위험회피 | `VIXCLS`, `BAA10Y` | 두 지표 상승 | 두 지표 하락 | 달러 안전수요 경로, 불일치 시 `MIXED` |
| 해외 상대금리 | 미수집 | 해당 없음 | 해당 없음 | 항상 `UNAVAILABLE`, 후속 데이터 후보 |

`DX-Y.NYB`는 달러 카드의 실제 가격이므로 달러 자체의 원인 경로로 다시 사용하지 않는다.

미국 금리가 상승해도 해외 금리가 더 크게 상승했을 수 있으므로, 해외 상대금리가 없는 동안 달러 카드의 전체 데이터 범위는 `SUFFICIENT`가 될 수 없다.

## 신선도와 데이터 범위

### 신선도

- 일별 시장 시계열은 reference date 기준 최근 5 business day 안에 유효 관측값이 있어야 한다.
- 월별 경제지표는 series별 발표 주기와 공개 지연 허용치를 metadata로 관리한다.
- 수집 실패 시 마지막 저장값을 삭제하지 않지만 stale 값은 방향 판정에서 제외한다.
- stale, missing, insufficient history를 모두 사용자에게 같은 `미측정`으로 뭉개지 않고 상세 reason code로 보존한다.

예상 reason code:

- `MISSING_SERIES`
- `STALE_SERIES`
- `INSUFFICIENT_HISTORY`
- `CONFLICTING_HORIZONS`
- `BELOW_MATERIALITY`
- `RELATIVE_RATE_NOT_COLLECTED`

### 설명 데이터 범위

`coverage`는 설명이 맞을 확률이 아니라 확보된 측정 데이터 범위다.

- `SUFFICIENT`: 실제 가격이 최신이고 자산의 핵심 경로가 모두 최신
- `PARTIAL`: 실제 가격과 핵심 경로 일부는 있으나 중요한 경로가 미측정
- `INSUFFICIENT`: 실제 가격이 없거나 핵심 경로를 하나도 평가할 수 없음

자산별 규칙:

- 금: 실제 가격 + 실질금리 + 달러 경로가 모두 유효하면 `SUFFICIENT`; 둘 중 하나만 유효하면 `PARTIAL`.
- 달러: 해외 상대금리 경로가 없는 파일럿 동안 최대 `PARTIAL`.

## Read model 계약

경제사이클 service는 금·달러 항목에 아래 구조를 제공한다. 정확한 Python 타입은 구현 계획에서 확정하되 의미 계약은 유지한다.

```json
{
  "asset_group": "gold",
  "label": "금",
  "economic_state": {
    "as_of_date": "YYYY-MM-DD",
    "observations": []
  },
  "pathways": [
    {
      "pathway_id": "real_yield",
      "label": "실질금리 경로",
      "status": "SUPPORTS_FALL",
      "reason_code": null,
      "series": [
        {
          "series_id": "DFII10",
          "as_of_date": "YYYY-MM-DD",
          "change_5d": 0.0,
          "change_21d": 0.0,
          "change_63d": 0.0,
          "unit": "bp",
          "freshness": "CURRENT"
        }
      ]
    }
  ],
  "price_context": {},
  "coverage": "SUFFICIENT",
  "coverage_label": "데이터 범위 충분",
  "narrative": "...",
  "unmeasured_pathways": []
}
```

schema version은 새 계약을 구분할 수 있도록 올린다. 3~5차 대상인 채권·주식·원자재는 파일럿 동안 기존 `FAVORABLE/BURDEN` 자산 방향 결론을 화면에서 제거한다. 관측된 경제상태와 `시장 경로 미연결 · 단계적 확장 예정`만 표시해 금·달러와 같은 수준의 분석처럼 보이지 않게 한다.

## Narrative 계약

문장은 LLM이나 외부 뉴스 요약이 아니라 상태값과 숫자에서 deterministic하게 생성한다.

순서:

1. 관측된 경제상태
2. 측정된 상승 방향 경로
3. 측정된 하락 방향 경로
4. 실제 가격 1·3개월 방향
5. 미측정 경로와 해석 한계

금 예시:

> 생산·소비와 고용·소득은 약화했고 물가·정책 압력은 강화됐습니다. 시장에서는 실질금리와 달러가 상승해 금의 부담 방향과 함께 관측됐으며, 실제 금 가격도 최근 1개월과 3개월 하락했습니다. 다만 ETF·중앙은행 수급과 외부 사건은 이번 데이터 범위에 포함하지 않아 가격 원인을 확정하지 않습니다.

달러 예시:

> 미국 2년·10년 금리와 실질금리가 상승해 달러 지지 방향과 함께 관측됐고, 달러지수도 최근 1개월과 3개월 상승했습니다. 다만 해외 상대금리 경로를 측정하지 않아 미국 금리만으로 달러 상승 원인을 확정할 수 없습니다.

숫자가 상태 기준을 만족하지 않으면 해당 문장을 만들지 않는다. `금리 인하 기대`, `안전자산 수요 증가`처럼 직접 측정하지 않은 중간 상태를 사실형으로 쓰지 않는다.

## UI 설계

### 채택안

- 처음 제시한 다중 전달경로 구조를 사용한다.
- 경로 카드는 모두 흰색으로 둔다.
- 카드 왼쪽의 라운드 컬러 강조선은 제거한다.
- 상승·하락·데이터 범위 밖 그룹 전체에 색을 칠하지 않는다.
- 그룹 제목과 여백, 얇은 구분선으로 구조를 나눈다.

### 카드 순서

1. 자산명과 경로 상태
2. 관측된 경제 상태
3. 상승 요인이 될 수 있는 측정 경로
4. 하락 요인이 될 수 있는 측정 경로
5. 현재 데이터 범위 밖
6. 실제 가격 5·21·63거래일 변화
7. 현재 해석
8. 데이터 범위와 제한

경로 상태는 합산 점수가 아니라 현재 화면에 `측정 경로: 상승 방향 / 하락 방향 / 양방향 / 중립·미측정` 중 무엇이 존재하는지를 요약한다. `상승 우세`, `하락 우세`처럼 수익률 전망으로 읽히는 표현은 사용하지 않는다.

### 상세정보 노출

기본 카드에는 경로명, 방향, 21·63거래일 변화를 표시한다.

- desktop: hover/focus 시 source, 정확한 기준일, 5거래일 변화, freshness, reason code 설명 노출
- mobile: tap으로 같은 상세내용 확장
- hover에만 필수 의미를 숨기지 않는다. 방향과 핵심 1·3개월 수치는 기본 화면에서 읽을 수 있어야 한다.

### 데이터 범위 밖

- `ETF·중앙은행 수요`: `후속 후보`
- `뉴스·지정학`: `현재 범위 제외`
- 달러 `해외 상대금리`: `미측정 · 후속 데이터 후보`

`현재 데이터 범위 밖`은 개발 오류가 아니라 이번 정량 범위의 명시적 경계다.

## 오류 격리

- 신규 FRED 수집 실패는 기존 저장 자료와 경제사이클 snapshot을 손상시키지 않는다.
- macro loader 실패 시 금·달러 카드만 `데이터 범위 부족`으로 제한한다.
- 금 가격 누락은 달러 카드와 경제사이클 본문을 막지 않는다.
- 달러 가격 누락도 동일하게 격리한다.
- React는 누락 배열이나 알 수 없는 상태값을 받아도 화면 전체가 깨지지 않는 fallback을 가진다.
- fallback은 방향을 만들어내지 않고 `측정 자료 부족`을 표시한다.

## 변경 예상 파일

- `finance/data/macro.py`: `DGS2`, `DGS10`, `DFII10` metadata와 수집 대상
- `finance/loaders/macro.py`: reference date, 기간 history, latest/freshness용 DB read
- `finance/economic_cycle_interpretation.py`: 시계열 변화·materiality·경로·coverage·narrative 계약
- `app/services/overview/economic_cycle.py`: macro DB loader 연결과 새 read model 조립
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`: 흰색 다중 경로 카드와 hover/tap
- `app/web/streamlit_components/economic_cycle_workbench/src/style.css`: 구분선·반응형·상세정보 스타일
- `tests/test_economic_cycle_asset_pathways.py`: evaluator와 asset mapping focused tests
- `tests/test_economic_cycle_service.py`: DB read failure, schema, narrative, coverage
- `tests/test_market_context_economic_cycle.py`: React source contract

DB table schema 추가는 예상하지 않는다. 기존 `macro_series_observation`과 가격 테이블을 사용한다.

## 테스트 및 QA

### 수집·loader

- 세 신규 FRED series metadata, 정규화, UPSERT 계약
- reference date 이후 행 제외
- 빈 값, 중복 날짜, 비수치 관측 처리
- 최신값과 5년 history 정렬

### evaluator

- price/index 퍼센트 변화와 yield/spread bp 변화
- 5·21·63거래일 lag
- 최근 5년 중앙값 materiality 경계값
- 21·63 방향 일치, 충돌, 중립, 부족
- stale, missing, insufficient history reason code
- 금·달러 각 경로의 asset-specific 방향 매핑
- 금 `SUFFICIENT/PARTIAL/INSUFFICIENT`
- 달러 최대 `PARTIAL`

### narrative와 service

- 문장의 수치·방향이 payload와 일치
- 미측정 원인을 사실처럼 생성하지 않음
- `가격을 만들었다`, 원인 확률, 매매 표현이 없음
- 한 loader 실패가 다른 카드와 경제사이클 본문을 막지 않음
- live와 historical reference date 계약

### React와 Browser QA

- production build
- desktop 2열 및 좁은 화면 1열
- 흰색 카드, 왼쪽 강조선 없음
- hover/focus와 mobile tap 상세정보
- 긴 한국어 문장 overflow
- 자료 충분·부분·부족 및 경로 혼재·중립·미측정 상태
- 실제 DB read model로 localhost 화면 확인
- 최종 QA 스크린샷 1장 보존, generated artifact는 commit 제외

## 완료 조건

- 미국 경제상태가 자산가격의 정답처럼 표현되지 않는다.
- 금과 달러에서 실제 측정 경로가 상승·하락·혼재·중립·미측정으로 분리된다.
- 1주는 단기 맥락, 1·3개월은 방향 판정이라는 규칙이 일관된다.
- 작은 움직임은 최근 5년 분포 기준으로 중립 처리된다.
- 오래되거나 부족한 데이터에서 방향을 생성하지 않는다.
- 달러의 해외 상대금리 부재가 항상 공개된다.
- 카드 설명만 읽어도 경제상태, 측정 경로, 실제 가격, 한계를 구분할 수 있다.
- 기존 경제사이클 현재/+1M/+2M 판단, cycle map, 5년 ribbon에 회귀가 없다.
- focused Python tests, React build, Browser QA를 통과한다.

## 제외 범위

- 가격 예측, 목표가격, 매수·매도 추천
- 경로별 원인 확률 또는 종합 자산 점수
- 실시간·intraday provider
- 뉴스·지정학 자동 해석
- ETF·중앙은행 수급 수집
- 해외 상대금리 수집
- 경제사이클 확률 모델과 publication gate 변경
- 채권·주식·원자재 다중 경로 구현

## 근거

- Federal Reserve, [Monetary Policy and Exchange Rates during the Global Tightening](https://www.federalreserve.gov/econres/notes/feds-notes/monetary-policy-and-exchange-rates-during-the-global-tightening-20240510.html): 금리차·위험선호와 달러의 동행 및 내생 변수의 인과 해석 한계.
- Federal Reserve, [The Sensitivity of the U.S. Dollar Exchange Rate to Changes in Monetary Policy Expectations](https://www.federalreserve.gov/econres/notes/ifdp-notes/the-sensitivity-of-the-us-dollar-exchange-rate-to-changes-in-monetary-policy-expectations-20170922.htm): 상대 정책금리 기대와 달러 반응.
- IMF, [Gold as International Reserves: A Barbarous Relic No More?](https://www.elibrary.imf.org/abstract/journals/001/2023/014/article-A001-en.xml): 금의 상대수익률·미국 금리·불확실성 등 복수 경로.
- NBER, [The Transmission Mechanism and the Role of Asset Prices in Monetary Policy](https://www.nber.org/papers/w8617): 통화정책의 금리·주식·환율 등 복수 전달경로.
- IMF, [The Power of Prices: How Fast Do Commodity Markets Adjust to Shocks?](https://www.imf.org/en/publications/wp/issues/2024/04/09/the-power-of-prices-how-fast-do-commodity-markets-adjust-to-shocks-547625): 원자재별 공급·수요 탄력성과 조정 시차의 이질성.

## 후속 확장 조건

3차로 넘어가기 전에 다음을 확인한다.

- 금·달러 파일럿에서 경로 `UNAVAILABLE/NEUTRAL` 비중이 과도하지 않은가?
- 5년 중앙값 materiality가 실제 화면에서 지나치게 보수적이거나 민감하지 않은가?
- hover/tap 없이도 핵심 해석이 읽히는가?
- 사용자가 `함께 관측`을 원인 확정으로 오해하지 않는가?

파일럿 결과에 따라 공통 threshold를 자산·series별로 조정할 수 있지만, 그 변경은 검증 근거와 별도 명세를 요구한다.
