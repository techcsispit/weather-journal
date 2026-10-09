import unittest
from unittest.mock import patch, MagicMock
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
import requests

from weather_journal.fetch import get_current, _cache

class TestFetch(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_path = Path(self.temp_dir.name) / "weather-cache.db"
        _cache.clear()

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("weather_journal.fetch.requests.get")
    def test_get_current_success(self, mock_get):
        # Mock a successful API response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "name": "London",
            "main": {"temp": 15.6, "humidity": 80},
            "weather": [{"description": "light rain"}]
        }
        mock_get.return_value = mock_resp

        result = get_current("London", api_key="fake-key", cache_path=self.cache_path)

        self.assertEqual(result["city"], "London")
        self.assertEqual(result["temp"], 15.6)
        self.assertEqual(result["humidity"], 80)
        self.assertEqual(result["condition"], "light rain")
        mock_get.assert_called_once()

    @patch("weather_journal.fetch.requests.get")
    def test_caching(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "name": "Paris",
            "main": {"temp": 20.0, "humidity": 50},
            "weather": [{"description": "clear sky"}]
        }
        mock_get.return_value = mock_resp

        # First call hits the API
        res1 = get_current("Paris", api_key="fake-key", cache_path=self.cache_path)
        self.assertEqual(mock_get.call_count, 1)

        # Second call within 10 minutes should hit the cache
        res2 = get_current("Paris", api_key="fake-key", cache_path=self.cache_path)
        self.assertEqual(mock_get.call_count, 1)  # Still 1
        self.assertEqual(res1, res2)

    @patch("weather_journal.fetch.time.sleep")
    @patch("weather_journal.fetch.requests.get")
    def test_network_retry_and_failure(self, mock_get, mock_sleep):
        # Make the request raise a ConnectionError on all attempts
        mock_get.side_effect = requests.ConnectionError("Connection timeout")

        with self.assertRaises(ValueError) as context:
            get_current("Berlin", api_key="fake-key", cache_path=self.cache_path)

        self.assertIn("Network error: Connection timeout", str(context.exception))
        # It should have retried 3 times (initial + 2 retries)
        self.assertEqual(mock_get.call_count, 3)
        # It should have slept twice
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_any_call(1) # 2**0
        mock_sleep.assert_any_call(2) # 2**1

    def test_cache_survives_separate_python_processes(self):
        env = os.environ.copy()
        env["WEATHER_JOURNAL_CACHE"] = str(self.cache_path)
        repo_root = Path(__file__).resolve().parent.parent
        populate = """
from unittest.mock import MagicMock, patch
from weather_journal.fetch import get_current
response = MagicMock(status_code=200)
response.json.return_value = {
    "name": "Mumbai",
    "main": {"temp": 29.0, "humidity": 75},
    "weather": [{"description": "haze"}],
}
with patch("weather_journal.fetch.requests.get", return_value=response):
    get_current("Mumbai", api_key="fake-key")
"""
        consume = """
from unittest.mock import patch
from weather_journal.fetch import get_current
with patch("weather_journal.fetch.requests.get", side_effect=AssertionError("API called")):
    print(get_current("Mumbai")["city"])
"""

        first = subprocess.run(
            [sys.executable, "-c", populate], cwd=repo_root, env=env,
            text=True, capture_output=True,
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        second = subprocess.run(
            [sys.executable, "-c", consume], cwd=repo_root, env=env,
            text=True, capture_output=True,
        )

        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(second.stdout.strip(), "Mumbai")

    @patch("weather_journal.fetch.requests.get")
    def test_expired_persistent_entry_is_refetched(self, mock_get):
        stale_response = MagicMock(status_code=200)
        stale_response.json.return_value = {
            "name": "Paris",
            "main": {"temp": 10.0, "humidity": 50},
            "weather": [{"description": "cloudy"}],
        }
        fresh_response = MagicMock(status_code=200)
        fresh_response.json.return_value = {
            "name": "Paris",
            "main": {"temp": 20.0, "humidity": 45},
            "weather": [{"description": "clear sky"}],
        }
        mock_get.side_effect = [stale_response, fresh_response]

        get_current("Paris", api_key="fake-key", cache_path=self.cache_path)
        _cache.clear()
        conn = sqlite3.connect(str(self.cache_path))
        try:
            conn.execute("UPDATE weather_cache SET fetched_at = 0")
            conn.commit()
        finally:
            conn.close()

        result = get_current("Paris", api_key="fake-key", cache_path=self.cache_path)

        self.assertEqual(result["temp"], 20.0)
        self.assertEqual(mock_get.call_count, 2)

if __name__ == "__main__":
    unittest.main()
