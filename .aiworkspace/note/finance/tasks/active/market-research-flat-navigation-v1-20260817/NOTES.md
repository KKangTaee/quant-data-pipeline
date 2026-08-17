# Notes

- Preserve `economic-cycle` as the compatibility slug for 경기 국면.
- Add `inflation-policy` as a direct sibling route without copying data or service logic.
- Mobile subtab is a one-line text rail; bounded horizontal swipe is allowed only when labels cannot fit.
- Existing unrelated registry, run history and QA artifacts must remain untouched and unstaged.
- `PRODUCT_DIRECTION.md`, `PROJECT_MAP.md`, `ROADMAP.md`, `flows/README.md`, the inflation-policy architecture flow, data flow path and Overview runbook were updated because the canonical user journey changed from 7 to 8 views.
- The 360px navigation iframe measured 51px high with `flex-wrap: nowrap`; the page document retained `scrollWidth == clientWidth == 360` while only the view rail exposed bounded horizontal swipe.
