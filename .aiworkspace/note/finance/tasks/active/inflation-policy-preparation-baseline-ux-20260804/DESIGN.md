# Inflation Policy Preparation Baseline UX Design

State: active
Last Verified: 2026-08-04

## 사용자 문제

현재 준비표는 `재가속 변화`와 `인상 경로 변화`만 보여준다. 사용자는 인상 경로의
현재 기준값 49.29%를 화면에서 직접 볼 수 없고, 아래 정책 경로에 표시된 반올림된
개별 행을 스스로 찾아 합산해도 48%가 되어 내부 기준과 일치하지 않는다.

## 채택 설계

`다음 Core PCE 발표 전 준비표` heading과 scenario table 사이에 `현재 비교 기준`
영역을 둔다.

### 물가 기준

- `재가속 14.30%`
- `충격성 재가속 1.74%`
- `재가속 합계 16.04%`

### 정책 기준

- `순 1회 인상 16.43%`
- `순 2회 인상 26.43%`
- `순 3회 이상 인상 6.43%`
- `연말 순인상 경로 합계 49.29%`

`순`은 25bp 단위 연말 정책금리의 현재 대비 순변화이며, 중간 FOMC 회의의 실제
인상·인하 순서를 뜻하지 않는다. 준비표 heading은 `현재 전망 대비 재가속 변화`와
`현재 전망 대비 연말 순인상 경로 변화`로 명확히 한다.

## 데이터 흐름

새 계산이나 저장 필드는 만들지 않는다.

- 물가 기준: 기존 `inflation.state_probabilities`
- 정책 기준: 기존 `policy.net_move_probabilities`
- 합계: presentation layer에서 관련 bucket을 더한다.

`InflationPolicyWorkbench`가 기존 inflation과 policy payload를
`InflationStatePanel`에 함께 전달한다. policy component가 READY가 아니면 정책
기준을 숫자로 공개하지 않고 기존 publication gate를 유지한다.

## 변경 범위

- `InflationPolicyWorkbench.tsx`: policy payload와 gate 전달
- `InflationStatePanel.tsx`: current baseline 계산과 표시, table copy 보정
- `PolicyPathPanel.tsx`: 연말 경로 label을 `순` 기준으로 정렬
- `style.css`: compact baseline summary 배치
- `InflationPolicyWorkbench.test.tsx`: 표시값, gate와 용어 회귀
- `component_static/`: 검증된 production build 반영

## 고려한 대안

1. `PolicyPathPanel`에 합계만 추가: 중복은 적지만 준비표와 떨어져 있어 변화량의
   기준을 즉시 이해하기 어렵다.
2. 각 scenario를 `49.3% -> 39.3%`로 변환: 결과는 빠르게 읽히지만 사용자가 요청한
   1회·2회·3회 이상 구성 근거를 숨긴다.
3. 채택안: 준비표에 기준 구성과 합계를 함께 둬 근거와 변화량을 한 문맥에서 읽는다.

## 테스트와 오류 처리

- READY payload에서 두 기준 합계와 세 순인상 bucket을 정확히 표시한다.
- policy LIMITED/NOT_AVAILABLE이면 숨겨진 합계를 계산해 공개하지 않는다.
- 확률이 누락된 bucket은 0으로 안전하게 처리하되 component gate를 우선한다.
- React test, TypeScript typecheck, production build와 실제 DB Browser QA를 수행한다.

## 범위 밖

- Core PCE, policy, joint path 모델 재학습
- probability calibration과 DB schema 변경
- scenario별 정책 횟수 분포 신규 계산
- 새 탭 또는 V2/V3 surface 생성
