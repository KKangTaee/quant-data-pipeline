# Strategy Inventory

Status: Active
Last Verified: 2026-06-08

## Purpose

이 문서는 현재 Backtest 제품에 있는 전략을 `실행 가능성`, `후보 evidence`, `workflow 연결성` 기준으로 분류한다.

핵심 구분:

- `Executable`: Single / Compare에서 실행 가능하다.
- `Replayable`: history / saved / Candidate Library에서 재실행 가능하다.
- `Evidence Mature`: current anchor, weakness, next action이 durable report로 설명된다.
- `Workflow Ready`: Practical Validation / Final Review / Portfolio Monitoring으로 넘길 준비가 되어 있다.

## Strategy List

| Strategy | Family | Role | Runtime | Replay / lifecycle | Evidence maturity | Current product interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| Equal Weight | ETF static basket | Exposure sleeve / baseline | Supported | Candidate Library supports ETF replay | Medium | 단독 alpha보다 GTAA / strict annual과 섞는 sleeve |
| GTAA | ETF tactical allocation | Low-MDD tactical sleeve | Supported | Candidate Library supports ETF replay | High | ETF 계열의 가장 성숙한 후보군 |
| Global Relative Strength | ETF relative strength | Price-only ETF momentum | Supported | UI / saved replay smoke exists; Candidate Library includes key | Medium-low | 기능 연결은 됐지만 current candidate hub가 부족 |
| Risk Parity Trend | ETF defensive allocation | Volatility-aware defensive component | Supported | Candidate Library supports ETF replay | Low | 제품 노출은 있으나 durable candidate evidence 부족 |
| Dual Momentum | ETF tactical allocation | Concentrated momentum switch | Supported | Candidate Library supports ETF replay | Low | 실행 가능하지만 current anchor / weakness report 부족 |
| Risk-On Momentum 5D | Daily stock swing | Short-term research lane | Supported | History payload restore tests exist; generated artifacts | Medium for research, low for workflow | Backtest Analysis research lane; validation / monitoring governance deferred |
| Quality Snapshot | Broad factor prototype | Early broad research | Supported | Not primary candidate lifecycle | Low | legacy / broad research path로 낮게 본다 |
| Quality Strict Annual | Factor equity | Quality-only annual strategy | Supported | Candidate Library supports strict annual replay | High | 구조 조정으로 살아난 reference family |
| Value Strict Annual | Factor equity | Value annual return engine | Supported | Candidate Library supports strict annual replay | High | raw return 최강 축이나 MDD / review gap 존재 |
| Quality + Value Strict Annual | Factor equity | Blended factor annual strategy | Supported | Candidate Library supports strict annual replay | High | 가장 잘 정리된 blended practical family |
| Quality Strict Quarterly Prototype | Factor equity prototype | Quarterly contract validation | Supported | Candidate lifecycle incomplete | Low-medium | runtime smoke / contract 보존 수준 |
| Value Strict Quarterly Prototype | Factor equity prototype | Quarterly contract validation | Supported | Candidate lifecycle incomplete | Low-medium | runtime smoke / contract 보존 수준 |
| Quality + Value Strict Quarterly Prototype | Factor equity prototype | Quarterly contract validation | Supported | Candidate lifecycle incomplete | Low-medium | runtime smoke / contract 보존 수준 |

## Strategy Family Notes

### ETF Family

ETF 전략은 실전 운용성, 비용, benchmark, liquidity / provider evidence를 더 중요하게 본다.
GTAA와 Equal Weight는 current report가 있으나, Global Relative Strength / Risk Parity / Dual Momentum은 같은 깊이의 current anchor가 부족하다.

### Strict Annual Factor Family

가장 풍부한 strategy report와 candidate evidence를 가진 family다.
Value는 return engine, Quality는 구조적 reference, Quality + Value는 blended candidate anchor로 읽는다.

### Quarterly Prototype Family

runtime contract smoke는 통과했지만, 아직 strict annual과 같은 candidate lifecycle로 보지 않는다.
quarterly는 filing lag, PIT handling, replay, validation evidence를 더 확인해야 한다.

### Risk-On Momentum 5D

Daily swing research evidence는 강하지만 기존 monthly / annual validation gate와 성격이 다르다.
따라서 governance design 없이 Final Review / Portfolio Monitoring으로 직접 연결하면 안 된다.

## Maturity Summary

| Maturity | Strategies |
| --- | --- |
| High | GTAA, Value Strict Annual, Quality Strict Annual, Quality + Value Strict Annual |
| Medium | Equal Weight, Global Relative Strength, Risk-On Momentum 5D research lane |
| Low / Prototype | Risk Parity Trend, Dual Momentum, Quality Snapshot, strict quarterly prototypes |

## Immediate Reading Order For 3차

1. `RECOMMENDATION.md`
2. `NEXT_SESSION_HANDOFF.md`
3. `WEAKNESS_MATRIX.md`
4. `CURRENT_PROJECT_AUDIT.md`
5. source docs listed in `SOURCES.md`
