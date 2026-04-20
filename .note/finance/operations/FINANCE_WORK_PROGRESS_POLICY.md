# Finance Work Progress Policy

## 목적

- `WORK_PROGRESS`를 계속 쓰되,
  시간이 갈수록 너무 커져서 읽기 어렵거나 유지가 불편해지는 문제를 막는다.
- finance 프로젝트는 월 단위보다 phase 단위로 움직이므로,
  로그도 phase 구조를 기준으로 관리하는 것이 더 자연스럽다.

## 결론

- `.note/finance/WORK_PROGRESS.md`는 계속 유지한다.
- 하지만 앞으로는 이 파일을 **모든 세부 기록을 끝없이 쌓는 단일 저장소**로 쓰지 않는다.
- 운영 원칙은 아래처럼 가져간다.

## 기본 운영 방식

### 1. 루트 `WORK_PROGRESS.md`는 계속 canonical log로 유지

- 역할:
  - 현재 active workstream 진행 상황
  - 큰 구현 milestone
  - 중요한 설계 결정
  - handoff에 필요한 핵심 요약
- 즉, 가장 먼저 열어보는 top-level 진행 로그 역할은 계속 이 파일이 맡는다.

### 2. 월별 분리보다 phase별 분리를 우선

- 이 프로젝트는 phase 중심으로 진행된다.
- 그래서 월별로 자르면:
  - 같은 phase가 여러 파일로 찢어지고
  - later review에서 흐름을 다시 따라가기 어려워진다.
- 반면 phase별로 나누면:
  - 왜 그 작업을 했는지
  - 어떤 구현이 연결되는지
  - 언제 closeout 되었는지
  를 한 덩어리로 보기 쉽다.

## 권장 구조

### 루트

- `.note/finance/WORK_PROGRESS.md`
  - 현재 진행 중인 workstream
  - high-signal milestone
  - top-level handoff note

### phase archive

- `.note/finance/phase7/PHASE7_WORKLOG.md`
- `.note/finance/phase8/PHASE8_WORKLOG.md`
- `.note/finance/phase12/PHASE12_WORKLOG.md`

형태로, phase가 커졌을 때 상세 구현 로그를 옮기는 방식을 기본으로 한다.

## 언제 분리하나

아래 중 하나에 해당하면 phase worklog를 만드는 것이 좋다.

1. root `WORK_PROGRESS.md`가 너무 커져서 빠르게 읽기 어렵다
2. 한 phase에서 구현/실험/문서화 로그가 특히 많다
3. closeout 이후에도 그 phase의 작업 흐름을 다시 참고할 일이 많다

## 실제 기록 원칙

### 루트 `WORK_PROGRESS.md`에 남길 것

- 시작
- 주요 milestone
- 중요한 설계 결정
- closeout / handoff 상태

### phase worklog에 남길 것

- 실험 반복
- 검색/탐색 pass
- candidate 비교
- 세부 구현 메모
- 해당 phase 안에서만 유효한 시행착오 기록

## 지금 상태에 대한 판단

- 현재 `.note/finance/WORK_PROGRESS.md`는 이미 길이가 충분히 커졌다.
- 그래서 first-pass로는:
  - root에는 concise current context만 남기고
  - 이전 full log는 archive snapshot으로 먼저 분리하는 것도 허용한다
- 이후 필요할 때,
  phase별 worklog로 더 세밀하게 다시 나누는 것이 자연스럽다

## 실무 권고

- 당장 가장 좋은 운영은:
  - root `WORK_PROGRESS.md`는 current summary/pointer로 유지
  - full history는 archive snapshot으로 먼저 안전하게 분리
  - active phase에 로그가 많이 쌓이면 `PHASE*_WORKLOG.md` 추가
  - 필요 시 archive snapshot을 phase별 worklog로 later split

즉 정리하면:
- **단일 파일 완전 유지**보다
- **루트 summary + archive + 필요 시 phase worklog** 구조가 가장 효율적이다.
