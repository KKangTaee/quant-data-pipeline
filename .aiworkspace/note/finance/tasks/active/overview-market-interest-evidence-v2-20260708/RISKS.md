# Overview Market Interest Evidence V2 Risks

## Source / Product Risks

- Analyst ratings and target changes are licensing-sensitive. V2 must not imply the app has checked structured analyst changes unless a source has been approved.
- Google News RSS and existing Korean-news metadata can be useful session leads, but article body collection remains out of scope.
- Naver News API is official for Korean news search but requires credentials and quota management.
- 13F evidence is delayed, incomplete for trading intent, and requires CUSIP-symbol mapping for durable selected-symbol lookup.

## UX Risks

- Removing separate `뉴스` and `SEC 공시` tabs could hide familiar access points unless the `뉴스/공시 촉매` section is visibly useful.
- Source-policy details should stay secondary; the first read should show evidence rows and conservative states.
