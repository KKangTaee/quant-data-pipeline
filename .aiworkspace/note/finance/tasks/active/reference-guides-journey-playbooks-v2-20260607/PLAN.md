# Reference Guides Journey / Playbooks V2 2026-06-07

Status: Completed

## Goal

`Reference > Guides` 2차 작업으로 journey guide와 troubleshooting playbook을 더 촘촘히 만든다.

## 이걸 하는 이유?

1차 Reference Center는 사용자가 작업 유형과 owner screen을 찾는 첫 화면을 만들었다.
하지만 실제로 막혔을 때는 어떤 순서로 확인하고, 어디서 멈추고, 어떤 기록을 봐야 하는지까지 한 단계 더 필요하다.
2차는 Reference를 단순 설명 페이지가 아니라 read-only operational guide로 강화한다.

## Scope

- Journey guide에 route별 step, common failure state, next owner screen을 추가한다.
- Troubleshooting playbook에 확인 순서, evidence location, stop condition을 구조화한다.
- UI에서 선택한 journey와 playbook의 상세 guide를 읽기 쉽게 렌더링한다.
- 기존 Portfolio Selection Journey는 유지하되, 2차 내용과 용어가 충돌하지 않게 보강한다.

## Out Of Scope

- `Reference > Glossary` 전체 개편.
- Overview / Backtest / Practical Validation / Portfolio Monitoring 화면에서 Reference contextual link 연결.
- Provider fetch, DB write, registry write, saved setup write, broker order, live approval, auto rebalance.
- 외부 문서 자동 색인이나 AI chat.

## Completion Criteria

- Catalog contract test가 RED 후 GREEN으로 통과한다.
- Journey / playbook 구조가 Streamlit 없이 import 가능하다.
- UI에서 선택한 journey와 playbook 상세가 보인다.
- Durable Reference flow docs와 task/root handoff가 최신 2차 상태를 가리킨다.
- Browser QA로 Reference Center 화면을 확인한다.
