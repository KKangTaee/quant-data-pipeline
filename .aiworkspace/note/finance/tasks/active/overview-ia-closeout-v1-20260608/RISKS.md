# Risks

- Candidate Ops가 여전히 Overview 안에 남아 있어 완전한 IA 분리는 아니다.
- 실제 relocation / removal은 Backtest workflow impact가 있으므로 별도 승인 task가 필요하다.
- Static guide는 read-model metadata라 runtime freshness는 보여주지 않는다. Freshness는 cockpit/source confidence/data health가 소유한다.
- in-app Browser screenshot API가 이 페이지에서 timeout되어 screenshot artifact는 별도 Playwright session으로 생성했다.
