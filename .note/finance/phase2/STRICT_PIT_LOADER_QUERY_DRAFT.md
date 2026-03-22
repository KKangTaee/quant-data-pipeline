# Strict PIT Loader Query Draft

## 목적
이 문서는 future strict point-in-time loader가
`nyse_financial_statement_values`를 어떤 조건으로 읽어야 하는지 초안을 정리한다.

핵심 원칙:
- mixed-state 전체 테이블을 그대로 읽지 않는다
- accession-bearing / available-at-aware rows만 strict PIT 후보로 사용한다
- latest available snapshot은 `period_end`가 아니라 `available_at` 기준으로 결정한다

---

## 1. strict PIT 기본 필터

상세 재무제표 strict loader는 기본적으로 아래 조건을 포함한다.

```sql
accession_no IS NOT NULL
AND accession_no <> ''
AND unit IS NOT NULL
AND unit <> ''
AND available_at IS NOT NULL
```

의미:
- old legacy row 제외
- identity-incomplete row 제외
- public availability timing이 없는 row 제외

---

## 2. 시계열 조회 조건

strict PIT 시계열 조회는 아래 두 축으로 본다.

1. 회계 row 자체 범위
2. 그 row가 실제로 사용 가능했던 시점

예시:

```sql
SELECT *
FROM nyse_financial_statement_values
WHERE symbol IN (...)
  AND freq = 'annual'
  AND accession_no IS NOT NULL
  AND accession_no <> ''
  AND unit IS NOT NULL
  AND unit <> ''
  AND available_at IS NOT NULL
  AND period_end BETWEEN %(start)s AND %(end)s
  AND available_at <= %(as_of_cutoff)s
```

비고:
- pure historical analysis면 `period_end` 중심 range도 가능
- 실제 backtest snapshot이면 결국 `available_at <= rebalance_date` 조건이 더 중요하다

---

## 3. snapshot 조회 조건

strict PIT snapshot은
“`as_of_date` 시점에 사용 가능했던 row 중 가장 최신”이어야 한다.

즉:
- `period_end <= as_of_date`만으로는 부족
- 반드시 `available_at <= as_of_date`를 포함한다

---

## 4. latest available snapshot 패턴

예시 목표:
- 특정 symbol / concept / statement_type / unit 조합에 대해
- `as_of_date` 시점의 최신 row 1개 반환

### 패턴 A. window function

```sql
SELECT *
FROM (
    SELECT
        v.*,
        ROW_NUMBER() OVER (
            PARTITION BY v.symbol, v.statement_type, v.concept, v.unit
            ORDER BY v.available_at DESC, v.period_end DESC, v.accession_no DESC
        ) AS rn
    FROM nyse_financial_statement_values v
    WHERE v.symbol IN (...)
      AND v.freq = %(freq)s
      AND v.accession_no IS NOT NULL
      AND v.accession_no <> ''
      AND v.unit IS NOT NULL
      AND v.unit <> ''
      AND v.available_at IS NOT NULL
      AND v.available_at <= %(as_of_date)s
) t
WHERE t.rn = 1
```

장점:
- loader 구현이 직관적

주의:
- MySQL 버전/성능 확인 필요

### 패턴 B. subquery + join

window function이 부담이면
`MAX(available_at)` subquery와 join으로 대체 가능

---

## 5. period_end와 available_at의 우선순위

strict PIT snapshot 정렬 우선순위는 아래가 권장된다.

1. `available_at DESC`
2. `period_end DESC`
3. `accession_no DESC`

이유:
- 같은 `period_end`라도 더 늦게 시장에 알려진 filing이 있을 수 있다
- first priority는 availability다

---

## 6. loader 구현 규칙

### `load_statement_values(...)`
- strict mode가 아니면 broader read 허용 가능
- strict mode면 기본 필터를 항상 적용

### `load_statement_snapshot(...)`
- strict mode 기본값을 권장
- `available_at <= as_of_date` 필수
- latest available row selection 필수

### `load_statement_labels(...)`
- strict snapshot source가 아니라
  UI label lookup / summary용으로 제한

---

## 7. 당장 구현할 때의 현실적 규칙

현재 mixed-state 환경에서는 아래가 현실적이다.

1. strict PIT loader는 accession-bearing rows만 읽는다
2. broad research loader는 필요 시 legacy rows도 읽을 수 있다
3. 두 loader를 이름/문서에서 명확히 구분한다

예:
- `load_statement_values(...)`
  - broad/raw research
- `load_statement_snapshot_strict(...)`
  - strict PIT snapshot

---

## 8. 다음 작업 연결

이 초안 다음의 자연스러운 작업:

1. loader 구현 범위 확정
2. strict / broad loader naming 규칙 확정
3. research-universe backfill 대상 확정
4. 필요 시 MySQL query helper 설계

