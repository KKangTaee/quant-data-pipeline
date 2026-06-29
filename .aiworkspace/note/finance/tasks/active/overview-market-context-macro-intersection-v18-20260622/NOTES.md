# Overview Market Context Macro Intersection V18 Notes

## Decisions

- Final conditioned sample remains the intersection of GLD current-like bucket and Rate Pressure futures current-like bucket.
- GLD and futures counts should be shown as independent broad-sample filters, not as a sequential dependency.
- The existing source detail / dimension audit can remain collapsed, but its preview counts should align with the independent condition count.
