# Final Review Readable Review Evidence V1

Status: Active
Last Updated: 2026-07-11

## 이걸 하는 이유?

Final Review의 `남은 판단 근거`는 저장된 Level2 audit과 연결되어 있지만 내부 영어 label, raw status, 압축된 관측 문자열을 그대로 보여줘 사용자가 검증 의미와 다음 행동을 해석해야 한다. 각 근거를 사용자 언어로 번역하고, 실제 데이터 보강으로 해결되는 항목과 기간·검증 기능·사용자 판단 문제를 분리해 최종 판단 부담을 낮춘다.

## Scope

1. 검증명, 상태, 관측, 판단 기준을 사용자 언어로 변환한다.
2. 각 근거에 검증 설명, 사용자 해석, 개선 방법, 처리 유형을 추가한다.
3. 수집 가능한 provider gap만 후보 context를 유지해 Practical Validation Flow4로 연결한다.
4. focused tests, React build, py_compile, Browser QA와 finance 문서 sync를 수행한다.

## Boundaries

- React는 표시와 navigation intent만 담당한다.
- provider fetch, 수집 계획, 재검증, registry write는 Python 경계를 유지한다.
- `기간 미포함`, strategy-specific `NOT_RUN`, Tax / Account 정성 판단은 데이터 갱신으로 해결되는 것처럼 표시하지 않는다.
- Final Review는 live approval, broker order, auto rebalance가 아니다.

## Stop Condition

- 모든 non-PASS trace가 사용자 의미와 다음 행동을 제공한다.
- 보강 CTA는 실제 수집 가능한 gap이 있을 때만 노출된다.
- 보강 후 Level2 재검증과 Final Review 재확인이 필요하다는 경계가 보인다.
- 관련 자동화·Browser QA와 문서 sync가 완료되고 차수별 commit이 생성된다.
