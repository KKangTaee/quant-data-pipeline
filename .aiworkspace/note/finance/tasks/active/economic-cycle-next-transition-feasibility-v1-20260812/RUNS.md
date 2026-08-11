# Runs

## 2026-08-12 Baseline

- Focused economic-cycle regression: `95 passed`, external deprecation warning 3건.
- Existing linked worktree: `codex/main-dev`; 별도 worktree 생성 없음.

## 2026-08-12 Manual PIT Reproduction

- panel: 811 origins, 1959-01-31 through 2026-07-31
- usable observed state: 148 origins, 2014-04-30 through 2026-07-31
- data status: READY 106 / LIMITED 42 / UNAVAILABLE 663
- two-release confirmed transitions: 32
- destinations: recovery 7 / expansion 9 / slowdown 5 / contraction 11
- origins: recovery 7 / expansion 9 / slowdown 5 / contraction 11
- current evidence therefore fails the minimum experiment sample gate.

## 2026-08-12 Automated Feasibility Report

- status: `NO_GO_DATA`
- usable origins: 148 / required 180
- confirmed events: 32 / required 48
- destinations: recovery 7 / expansion 9 / slowdown 5 / contraction 11
- holdout events: 8 / required 12
- holdout destinations: recovery 4 / expansion 0 / slowdown 0 / contraction 4
- 주요 reason: usable origin, total event, recovery/slowdown support와 holdout
  expansion/slowdown support 부족

## 2026-08-12 Official Source Check

- Philadelphia Fed RTDSM은 full vintage history를 월말 갱신하며 payroll employment
  monthly vintages는 1964-12부터 제공한다.
- RTDSM variable catalog에 unemployment, weekly hours, industrial production과 capacity
  utilization이 포함된다.
- Philadelphia Fed ADS는 assessed-in-real-time all-vintages file을 제공한다.
- 신규 provider ingestion은 이번 task에서 수행하지 않고 다음 승인 경계로 남겼다.

## 2026-08-12 Verification

- next-transition + observed-state focused: 23 passed
- all economic-cycle tests: 226 passed, external deprecation warning 3건
- `py_compile`: pass
- `git diff --check`: pass
- `ruff`: project environment에 설치되어 있지 않아 미실행
- repository-wide pytest: 2317 passed / 345 failed / 158 subtests passed; existing
  Streamlit `DeltaGeneratorSingleton instance already exists` order-isolation failure
