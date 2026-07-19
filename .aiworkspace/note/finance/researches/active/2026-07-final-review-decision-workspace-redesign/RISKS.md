# Risks

Status: Active implementation risks
Last Updated: 2026-07-16

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Approved research design is mistaken for already-scheduled roadmap work | High | Use it as implementation-plan input and update durable roadmap only during explicit docs sync. |
| Trait map is read as a quality score | High | Label outward direction as exposure/pressure, show raw observation, prohibit composite/ranking. |
| Evidence disclosure grows back into the main flow | High | Enforce fixed IA and render accepted limits/provenance only in collapsed disclosure. |
| Positive verdict is generated from process readiness | High | Strength/weakness/thesis must reference measured portfolio behavior; Gate/readiness cannot be narrative input. |
| New labels break saved decision compatibility | High | Map labels to existing four canonical routes and keep row schema append-only. |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Current read model is large and coupled | High | Introduce a pure decision brief service; keep existing file as adapter/compatibility boundary. |
| Performance or benchmark series is absent from stored payload | High | Never fabricate charts; omit/mark unmeasured and record the limitation in confidence/disclosure. |
| Same observation appears in strength, weakness, trigger, trait map | Medium | Stable observation id and primary-role dedup contract in Python. Trait map may reference the observation visually but cannot create a second score impact. |
| React/Streamlit event reruns use stale candidate state | High | Include candidate/source/validation identity in intent and revalidate in Python before append. |
| React component failure resurrects old long report | Medium | Implement compact fallback from the same decision brief schema. |
| Scope expands into provider or historical universe work | High | Preserve no-fetch Final Review boundary and defer new provider work. |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| Exact availability of cumulative benchmark and underwater series by candidate source type | Some saved validation rows may carry summaries without chart-ready series. | During PLAN/systematic debugging, inventory current/saved/legacy source coverage and define adapter tests. |
| Trait axis thresholds for every source type | A normalized shape without explicit thresholds would recreate arbitrary scoring. | Start only with axes that already have measured observation and documented threshold; leave others unmeasured. |
| Narrow viewport chart interaction | A desktop-first behavior board can become unreadable on mobile. | Require narrow Browser QA and simplified stacked layout. |
| Existing final decision rows with old labels | History UI must still display old records consistently. | Keep canonical routes as source-of-truth and change only current UI labels. |
