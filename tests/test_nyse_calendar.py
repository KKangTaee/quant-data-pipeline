from __future__ import annotations

import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo


class NyseCalendarTests(unittest.TestCase):
    def test_latest_completed_session_uses_previous_day_before_regular_close(self) -> None:
        from app.services.nyse_calendar import latest_completed_nyse_session

        now = datetime(2026, 7, 15, 15, 59, tzinfo=ZoneInfo("America/New_York"))

        self.assertEqual(latest_completed_nyse_session(now), date(2026, 7, 14))

    def test_latest_completed_session_accepts_current_day_after_regular_close(self) -> None:
        from app.services.nyse_calendar import latest_completed_nyse_session

        now = datetime(2026, 7, 15, 16, 1, tzinfo=ZoneInfo("America/New_York"))

        self.assertEqual(latest_completed_nyse_session(now), date(2026, 7, 15))

    def test_latest_completed_session_handles_weekend_observed_holiday(self) -> None:
        from app.services.nyse_calendar import latest_completed_nyse_session

        now = datetime(2026, 7, 4, 12, 0, tzinfo=ZoneInfo("America/New_York"))

        self.assertEqual(latest_completed_nyse_session(now), date(2026, 7, 2))

    def test_latest_completed_session_accepts_day_after_thanksgiving_early_close(self) -> None:
        from app.services.nyse_calendar import latest_completed_nyse_session

        now = datetime(2026, 11, 27, 13, 1, tzinfo=ZoneInfo("America/New_York"))

        self.assertEqual(latest_completed_nyse_session(now), date(2026, 11, 27))


if __name__ == "__main__":
    unittest.main()
