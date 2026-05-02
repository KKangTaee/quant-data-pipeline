# Phase 6 Strict Quarterly Entry Criteria

## 목적

- quarterly strict family를 annual strict family와 같은 public-default 수준으로 바로 올리지 않고,
  research-capable prototype으로 진입하기 위한 최소 기준을 고정한다.

## first candidate

- 첫 대상:
  - `Quality Snapshot (Strict Quarterly Prototype)`

선정 이유:
- quality family는 value family보다 factor semantics가 단순하고,
  quarterly 회전의 해석도 더 직관적이다.
- overlay / interpretation 구조를 annual strict family와 재사용하기 쉽다.

## entry criteria

### 1. point-in-time path가 있어야 한다

- quarterly statement shadow factor history를 읽어야 한다.
- rebalance date 기준으로 `fundamental_available_at <= as_of_date` 경로가 유지되어야 한다.

### 2. monthly canonical price calendar와 함께 동작해야 한다

- quarterly factor라도 first-pass backtest는 월말 rebalance 경로를 그대로 사용한다.
- large-universe sparse calendar regression이 없어야 한다.

### 3. overlay / interpretation contract를 재사용할 수 있어야 한다

- trend filter overlay
- market regime overlay
- selection history
- interpretation summary

이 4개 contract가 annual strict family와 동일한 형태로 붙어야 한다.

### 4. public-default 승격은 별도 판단이다

- first pass에서는 compare public set 편입이나 official preset 승격을 요구하지 않는다.
- single strategy research prototype이면 충분하다.

## research-only 판단 기준

아래 중 하나라도 만족하면 research-only 유지가 맞다.

- coverage가 annual 대비 지나치게 얕다
- runtime cost가 과도하다
- quarterly factor usable history가 불안정하다
- strategy semantics가 아직 annual strict family와 충분히 구분되지 않는다

## current decision

- `Quality Snapshot (Strict Quarterly Prototype)`는
  Phase 6 first pass에서 **research-only single strategy**로 유지한다.
- compare public set 편입은 이번 chapter 범위 밖이다.
