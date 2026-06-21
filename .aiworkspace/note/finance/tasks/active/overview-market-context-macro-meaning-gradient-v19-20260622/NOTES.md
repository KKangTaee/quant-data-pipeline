# Notes

- User wants the matrix to visually encode positive returns with green gradient and negative returns with red gradient.
- User also wants T10Y3M / VIXCLS / BAA10Y reference values to explain what the numeric value means.
- Existing bucket thresholds:
  - T10Y3M: `<= 0` inverted, `<= 0.5` flat, otherwise positive yield curve.
  - VIXCLS: `>= 25` elevated, `>= 18` watch, otherwise calm.
  - BAA10Y: `>= 3` elevated, `>= 2` watch, otherwise contained.
