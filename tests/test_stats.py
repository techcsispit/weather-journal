"""Unit tests for weather statistics logic using offline sample data."""

import unittest
from weather_journal.stats import avg_temp, hottest_day, rainy_days


class TestWeatherStats(unittest.TestCase):

    def setUp(self):
        self.sample_data = [
            {"city": "Mumbai", "temp": 32.0, "humidity": 80, "condition": "light rain", "logged_at": "2025-07-01 10:00:00"},
            {"city": "Mumbai", "temp": 28.0, "humidity": 85, "condition": "heavy intensity rain", "logged_at": "2025-07-02 10:00:00"},
            {"city": "Mumbai", "temp": 30.0, "humidity": 70, "condition": "few clouds", "logged_at": "2025-07-03 10:00:00"}
        ]

    def test_avg_temp_valid_data(self):
        """Average temperature should calculate arithmetic mean."""
        # (32 + 28 + 30) / 3 = 30.0
        self.assertEqual(avg_temp(self.sample_data), 30.0)

    def test_hottest_day_detection(self):
        """Hottest day should identify record with highest temperature."""
        hot = hottest_day(self.sample_data)
        self.assertIsNotNone(hot)
        self.assertEqual(hot["temp"], 32.0)

    def test_rainy_days_counting(self):
        """Should count unique calendar days that experienced rain, drizzle, or thunderstorm."""
        self.assertEqual(rainy_days(self.sample_data), 2)

    def test_rainy_days_deduplicates_multiple_entries_on_same_day(self):
        """Multiple rain observations on one calendar day must count as only one rainy day."""
        same_day_entries = [
            {"city": "Mumbai", "temp": 28.0, "humidity": 85, "condition": "light rain", "logged_at": "2025-07-01 09:00:00"},
            {"city": "Mumbai", "temp": 27.0, "humidity": 88, "condition": "moderate rain", "logged_at": "2025-07-01 13:00:00"},
            {"city": "Mumbai", "temp": 26.5, "humidity": 90, "condition": "heavy rain", "logged_at": "2025-07-01 18:00:00"},
        ]
        self.assertEqual(rainy_days(same_day_entries), 1)

    def test_rainy_days_includes_drizzle_and_thunderstorms(self):
        """Drizzle and thunderstorms count as rain across distinct days."""
        entries = [
            {"city": "Mumbai", "temp": 26.0, "humidity": 82, "condition": "light intensity drizzle", "logged_at": "2025-07-02 10:00:00"},
            {"city": "Mumbai", "temp": 29.0, "humidity": 80, "condition": "thunderstorm with heavy rain", "logged_at": "2025-07-03 15:00:00"},
            {"city": "Mumbai", "temp": 28.5, "humidity": 78, "condition": "isolated thunderstorm", "logged_at": "2025-07-04 11:00:00"},
            {"city": "Mumbai", "temp": 31.0, "humidity": 65, "condition": "clear sky", "logged_at": "2025-07-05 12:00:00"},
        ]
        self.assertEqual(rainy_days(entries), 3)

    def test_cmd_stats_displays_rainy_days_label(self):
        """cmd_stats prints 'Rainy Days:' label instead of observations."""
        import tempfile
        from io import StringIO
        from pathlib import Path
        from types import SimpleNamespace
        from contextlib import redirect_stdout
        from weather_journal.cli import cmd_stats
        from weather_journal.store import save_entry

        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "test_weather.db"
            save_entry("Mumbai", 28.0, 85, "light rain", db_path=db_path)
            args = SimpleNamespace(city="Mumbai", db=db_path)
            out = StringIO()
            with redirect_stdout(out):
                cmd_stats(args)
            output = out.getvalue()
            self.assertIn("Rainy Days: 1", output)
            self.assertNotIn("Rainy Observations:", output)

    def test_avg_temp_empty(self):
        """Empty records list should return None."""
        self.assertIsNone(avg_temp([]))

    def test_hottest_day_empty(self):
        """Empty records list should return None."""
        self.assertIsNone(hottest_day([]))

    def test_cmd_stats_empty_records(self):
        """cmd_stats should print no records message and exit cleanly without raising TypeError."""
        import tempfile
        from io import StringIO
        from pathlib import Path
        from types import SimpleNamespace
        from contextlib import redirect_stdout
        from weather_journal.cli import cmd_stats

        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "test_weather.db"
            args = SimpleNamespace(city="Mumbai", db=db_path)
            out = StringIO()
            with redirect_stdout(out):
                cmd_stats(args)
            self.assertEqual(out.getvalue().strip(), "No records logged for 'Mumbai'.")


if __name__ == "__main__":
    unittest.main()
