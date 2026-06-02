# Selected Dashboard Live Readiness Follow-up V1

## Goal

Final Review에서 저장된 selected row가 Selected Portfolio Dashboard에서 open issue / follow-up과 live-readiness preflight를 read-only로 확인할 수 있게 만들고, 이후 fresh selected row 생성 가능 여부를 다시 점검한다.

## 이걸 하는 이유?

Final Review selection gate는 이제 Dashboard 관찰 후보 선정 기준으로 분리됐다. 따라서 Final Review에서 허용된 `REVIEW` 항목은 사라지면 안 되고, Selected Portfolio Dashboard와 future Live / Deployment Readiness에서 계속 보여야 한다.

## Scope

- 5차: Selected Dashboard에 `open_review_items` 기반 Open Issues / Follow-up view를 추가한다.
- 6차: Selected Dashboard 안에 Live / Deployment Readiness read-only preflight view를 추가한다.
- 7차: 기존 DB / registry / saved portfolio를 활용해 fresh selected row 생성 여부를 확인한다.

## Out Of Scope

- live approval, broker order, account sync, auto rebalance.
- provider 직접 fetch 또는 DB schema 변경.
- registry rewrite.
- 별도 top-level Deployment page 생성.
