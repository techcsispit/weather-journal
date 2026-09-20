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
        """Should count records with rain in condition description."""
        # 2 records have rain
        self.assertEqual(rainy_days(self.sample_data), 2)

    def test_rainy_days_empty(self):
        """Empty records list should return 0 rainy days."""
        self.assertEqual(rainy_days([]), 0)


if __name__ == "__main__":
    unittest.main()
