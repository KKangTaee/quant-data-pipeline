# Inflation Policy Preparation Baseline UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `다음 Core PCE 발표 전 준비표` 바로 위에서 현재 재가속 확률과 연말 순인상 경로의 구성·합계를 확인하게 한다.

**Architecture:** 기존 `inflation_policy_v1` payload의 `state_probabilities`와 `net_move_probabilities`만 React presentation layer에서 합산한다. `InflationPolicyWorkbench`가 policy payload와 독립 publication gate를 `InflationStatePanel`에 전달하고, 준비표가 같은 화면 문맥에서 기준값과 변화량을 함께 설명한다.

**Tech Stack:** React 18, TypeScript, Vitest, Testing Library, Vite, Streamlit custom component static bundle

## Global Constraints

- Core PCE, policy, joint-path 모델과 DB payload를 변경하지 않는다.
- 확률은 READY component에서만 공개한다.
- 연말 정책 경로는 25bp 단위 현재 대비 순변화이며 회의 순서를 뜻하지 않는다.
- 구성 bucket과 합계는 모두 소수 둘째 자리까지 표시한다.
- 새 탭이나 V2/V3 surface를 만들지 않는다.
- 사용자 registry, run history와 generated QA artifact를 commit하지 않는다.

---

### Task 1: 현재 비교 기준 표시 계약

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationStatePanel.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/PolicyPathPanel.tsx`

**Interfaces:**
- Consumes: `InflationPolicyPayload["inflation"]`, `InflationPolicyPayload["policy"]`, 두 component의 `publication_status`
- Produces: `InflationStatePanel` props `policy`와 `showPolicyProbabilities`, 접근 가능한 `다음 Core PCE 현재 비교 기준` 영역

- [ ] **Step 1: READY와 policy LIMITED 표시 계약을 실패 테스트로 추가**

```tsx
it("shows exact current reacceleration and net-hike baselines beside the next-print table", () => {
  const payload = readyPayload();
  payload.inflation.state_probabilities = {
    ...payload.inflation.state_probabilities,
    reacceleration: 0.143,
    shock_reacceleration: 0.0174,
  };
  payload.policy.net_move_probabilities = {
    cut_1: 0.06428571428571428,
    cut_2: 0.014285714285714285,
    cut_3_plus: 0.014285714285714285,
    hold: 0.41428571428571426,
    hike_1: 0.16428571428571428,
    hike_2: 0.2642857142857143,
    hike_3_plus: 0.06428571428571428,
  };

  render(<InflationPolicyWorkbench payload={payload} onCommand={vi.fn()} />);

  const baseline = screen.getByRole("region", { name: "다음 Core PCE 현재 비교 기준" });
  expect(within(baseline).getByText("16.04%")).toBeInTheDocument();
  for (const value of ["16.43%", "26.43%", "6.43%", "49.29%"] ) {
    expect(within(baseline).getByText(value)).toBeInTheDocument();
  }
});

it("does not publish the net-hike baseline when policy validation is pending", () => {
  render(<InflationPolicyWorkbench payload={mixedComponentPayload()} onCommand={vi.fn()} />);
  const baseline = screen.getByRole("region", { name: "다음 Core PCE 현재 비교 기준" });
  expect(within(baseline).getByText("정책 경로 검증 후 공개")).toBeInTheDocument();
  expect(within(baseline).queryByText("49.29%")).not.toBeInTheDocument();
});
```

- [ ] **Step 2: 새 테스트가 실패하는지 확인**

Run: `npm --prefix app/web/streamlit_components/economic_cycle_workbench test -- --run InflationPolicyWorkbench.test.tsx`

Expected: `다음 Core PCE 현재 비교 기준` region을 찾지 못해 FAIL.

- [ ] **Step 3: Workbench에서 policy와 gate를 InflationStatePanel에 전달**

```tsx
<InflationStatePanel
  inflation={payload.inflation}
  policy={payload.policy}
  showProbabilities={showInflationProbabilities}
  showPolicyProbabilities={showPolicyProbabilities}
/>
```

- [ ] **Step 4: 준비표 기준 합계와 fail-closed 표시를 구현**

```tsx
type Props = {
  inflation: InflationPolicyPayload["inflation"];
  policy: InflationPolicyPayload["policy"];
  showProbabilities: boolean;
  showPolicyProbabilities: boolean;
};

const exactPct = (value: number) => `${(value * 100).toFixed(2)}%`;

const reacceleration = inflation.state_probabilities.reacceleration || 0;
const shockReacceleration = inflation.state_probabilities.shock_reacceleration || 0;
const hikeOne = policy.net_move_probabilities.hike_1 || 0;
const hikeTwo = policy.net_move_probabilities.hike_2 || 0;
const hikeThreePlus = policy.net_move_probabilities.hike_3_plus || 0;
const hikeTotal = hikeOne + hikeTwo + hikeThreePlus;
```

READY이면 `재가속`, `충격성 재가속`, `재가속 합계`, `순 1회`, `순 2회`,
`순 3회 이상`, `연말 순인상 경로 합계`를 표시한다. policy가 READY가 아니면
정책 기준 숫자 대신 `정책 경로 검증 후 공개`를 표시한다.

- [ ] **Step 5: 정책 경로와 준비표 용어를 순변화 계약으로 맞춤**

```tsx
const policyLabels: Record<string, string> = {
  cut_3_plus: "순 3회 이상 인하",
  cut_2: "순 2회 인하",
  cut_1: "순 1회 인하",
  hold: "동결",
  hike_1: "순 1회 인상",
  hike_2: "순 2회 인상",
  hike_3_plus: "순 3회 이상 인상",
};
```

준비표 column은 `현재 전망 대비 재가속 변화`와 `현재 전망 대비 연말 순인상 경로 변화`로 바꾼다.

- [ ] **Step 6: React 테스트가 통과하는지 확인**

Run: `npm --prefix app/web/streamlit_components/economic_cycle_workbench test -- --run InflationPolicyWorkbench.test.tsx`

Expected: 모든 `InflationPolicyWorkbench.test.tsx` 테스트 PASS.

---

### Task 2: 읽기 쉬운 baseline summary 스타일과 production bundle

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Rebuild: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: Task 1의 `.next-release-current-baseline`, `.baseline-card`, `.baseline-breakdown`
- Produces: desktop과 좁은 화면에서 순서가 보존되는 compact 2-card summary

- [ ] **Step 1: 기존 next-release 반응형 style 경계를 확인**

Run: `rg -n "next-release|inflation-state|@media" app/web/streamlit_components/economic_cycle_workbench/src/style.css`

Expected: 준비표와 기존 responsive breakpoint 위치가 확인됨.

- [ ] **Step 2: 기준 합계가 먼저 읽히는 2-card style을 추가**

```css
.next-release-current-baseline {
  display: grid;
  gap: 10px;
  margin: 12px 0;
}

.baseline-card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.baseline-breakdown {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
```

기존 breakpoint에서는 `.baseline-card-grid { grid-template-columns: 1fr; }`로 전환한다.

- [ ] **Step 3: typecheck와 전체 React test를 실행**

Run: `npm --prefix app/web/streamlit_components/economic_cycle_workbench run typecheck`

Expected: exit 0.

Run: `npm --prefix app/web/streamlit_components/economic_cycle_workbench test`

Expected: 모든 test file PASS.

- [ ] **Step 4: production component_static을 재빌드**

Run: `npm --prefix app/web/streamlit_components/economic_cycle_workbench run build`

Expected: Vite build exit 0, `component_static/index.html`이 새 hashed CSS/JS를 참조함.

- [ ] **Step 5: 구현 단위를 commit**

```bash
git add app/web/streamlit_components/economic_cycle_workbench/src \
  app/web/streamlit_components/economic_cycle_workbench/component_static
git commit -m "물가 준비표 현재 비교 기준 표시"
```

---

### Task 3: 실제 DB Browser QA와 closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/inflation-policy-preparation-baseline-ux-20260804/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/inflation-policy-preparation-baseline-ux-20260804/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/inflation-policy-preparation-baseline-ux-20260804/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/inflation-policy-preparation-baseline-ux-20260804/RISKS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`

**Interfaces:**
- Consumes: 실제 DB-backed `inflation_policy_v1` READY snapshot
- Produces: 2/2 complete task record와 generated QA screenshot

- [ ] **Step 1: 사용자 8501을 건드리지 않고 별도 QA 서버를 실행**

Run: `.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8502 --server.headless true`

Expected: 8501은 계속 LISTEN, 8502가 QA 서버로 LISTEN.

- [ ] **Step 2: Browser에서 물가·정책 경로와 준비표 확인**

Expected:

- `현재 비교 기준`에 14.30%, 1.74%, 16.04%가 보인다.
- `순 1회 16.43%`, `순 2회 26.43%`, `순 3회 이상 6.43%`, 합계 49.29%가 보인다.
- 준비표의 기존 0.1~0.5 scenario와 정책·역산·주가·침체 panel이 유지된다.
- component crash와 새 console error가 없다.

- [ ] **Step 3: QA screenshot을 generated artifact로 저장**

Save: `inflation-policy-preparation-baseline-qa.png`

Expected: screenshot은 사용자에게 전달하지만 commit하지 않음.

- [ ] **Step 4: task 상태와 실행 근거를 2/2 complete로 갱신**

`STATUS.md`는 `State: complete`, manifest는 current active product task `none`으로
복구하고 테스트·build·Browser 결과를 `RUNS.md`에 기록한다.

- [ ] **Step 5: 문서 diff와 staged 범위를 검증하고 closeout commit**

Run: `git diff --check`

Expected: exit 0.

사용자 registry, research, run history, screenshots와 기타 generated artifact가 staged
목록에 없는지 확인한 뒤 task 문서만 commit한다.
