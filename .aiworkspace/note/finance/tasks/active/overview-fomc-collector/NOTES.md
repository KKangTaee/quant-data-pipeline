# Notes

- Official source: `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`.
- The Fed page exposes current and future year sections in HTML with `.fomc-meeting`, `.fomc-meeting__month`, and `.fomc-meeting__date` blocks.
- Store the policy-decision date as `event_date`, which is the final day in a meeting range. Keep the original month/range text in `raw_payload_json`.
