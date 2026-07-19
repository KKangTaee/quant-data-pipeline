# Portfolio Monitoring React Redesign Research Plan

Status: Design Handoff Complete
Last Updated: 2026-07-19

## 이걸 하는 이유?

현재 `Operations > Portfolio Monitoring`은 Final Review를 통과한 후보를 사후 추적하는
프로토타입 기능과 계산 기반을 갖고 있지만, Streamlit 관리 패널과 재실행 진단 중심의
정보 구조가 실제 포트폴리오 모니터링 제품 흐름을 가린다.

이번 리서치는 사용자가 포트폴리오 그룹을 만들고, 미국 주식·ETF 및 Final Review 통과
포트폴리오를 최대 10개까지 등록한 뒤, 통합 성과와 개별 성과, 규칙 기반 강점·약점,
매크로 조건부 위험 신호를 React workbench에서 읽는 전면 개편의 가능성과 경계를 정한다.

## Questions

1. React 전환은 기존 Streamlit route 안의 React one-shell인가, 독립 React/API 제품인가?
2. 직접 등록한 미국 주식·ETF와 Final Review 통과 전략을 하나의 그룹 성과곡선으로 어떻게 합산할 것인가?
3. 투자금 입력과 시작일 종가 기준 수량 입력의 저장·가격 기준은 무엇인가?
4. 포트폴리오 노출, 추세, 집중도, drawdown, 매크로 민감도를 어떤 deterministic rule로 진단할 것인가?
5. 어떤 신호까지 현재 위험 관찰로 표시하고, 어떤 표현은 예측·매매 지시로 보지 않을 것인가?

## Tentative Research Flow

1. 현재 제품·코드·데이터 계약 감사
2. 제품 범위와 React 배포 경계 확정
3. 2~3개 접근법 비교 및 권장안 합의
4. 화면·데이터·진단·검증 설계 확정
5. 승인된 설계를 task/phase 구현 계획으로 전환

## Non-Goals During Discovery

- UI 또는 저장 schema 구현
- registry/saved JSONL 재작성
- broker account 연동, 주문, 자동 리밸런싱
- AI 호출을 전제로 한 매일의 서술 생성
- 근거가 없는 수익률 예측 또는 매수·매도 신호

## Handoff

승인된 제품·데이터·진단 설계는
`.aiworkspace/note/finance/tasks/active/portfolio-monitoring-react-command-center-v1-20260719/DESIGN.md`
로 전환했다. 구현은 written spec review와 detailed implementation plan 승인 뒤 시작한다.
