import unittest
from unittest.mock import patch, MagicMock
import time
import requests

from weather_journal.fetch import get_current, _cache

class TestFetch(unittest.TestCase):
    def setUp(self):
        # Clear the cache before each test
        _cache.clear()

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

        result = get_current("London", api_key="fake-key")

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
        res1 = get_current("Paris", api_key="fake-key")
        self.assertEqual(mock_get.call_count, 1)

        # Second call within 10 minutes should hit the cache
        res2 = get_current("Paris", api_key="fake-key")
        self.assertEqual(mock_get.call_count, 1)  # Still 1
        self.assertEqual(res1, res2)

    @patch("weather_journal.fetch.time.sleep")
    @patch("weather_journal.fetch.requests.get")
    def test_network_retry_and_failure(self, mock_get, mock_sleep):
        # Make the request raise a ConnectionError on all attempts
        mock_get.side_effect = requests.ConnectionError("Connection timeout")

        with self.assertRaises(ValueError) as context:
            get_current("Berlin", api_key="fake-key")

        self.assertIn("Network error: Connection timeout", str(context.exception))
        # It should have retried 3 times (initial + 2 retries)
        self.assertEqual(mock_get.call_count, 3)
        # It should have slept twice
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_any_call(1) # 2**0
        mock_sleep.assert_any_call(2) # 2**1

    @patch("weather_journal.fetch.requests.get")
    def test_units_metric_requested(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "name": "Tokyo",
            "main": {"temp": 22.4, "humidity": 65},
            "weather": [{"description": "clear sky"}]
        }
        mock_get.return_value = mock_resp

        get_current("Tokyo", api_key="test-key")

        # Verify units=metric is explicitly requested for Celsius temperatures
        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"].get("units"), "metric")
        self.assertEqual(kwargs["params"].get("q"), "Tokyo")
        self.assertEqual(kwargs["params"].get("appid"), "test-key")

    @patch("weather_journal.fetch.requests.get")
    def test_invalid_api_key_401(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"cod": 401, "message": "Invalid API key."}
        mock_get.return_value = mock_resp

        with self.assertRaises(ValueError) as ctx:
            get_current("Mumbai", api_key="bad-key")

        self.assertEqual(str(ctx.exception), "Invalid API key.")

    @patch("weather_journal.fetch.requests.get")
    def test_city_not_found_404(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.json.return_value = {"cod": "404", "message": "city not found"}
        mock_get.return_value = mock_resp

        with self.assertRaises(ValueError) as ctx:
            get_current("NonExistentCity123", api_key="valid-key")

        self.assertEqual(str(ctx.exception), "City 'NonExistentCity123' not found.")

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key(self):
        with self.assertRaises(ValueError) as ctx:
            get_current("Mumbai")
        self.assertIn("Missing API key", str(ctx.exception))

    @patch("weather_journal.fetch.requests.get")
    def test_non_200_api_error(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.json.return_value = {"message": "Internal Server Error"}
        mock_get.return_value = mock_resp

        with self.assertRaises(ValueError) as ctx:
            get_current("Berlin", api_key="test-key")

        self.assertIn("API Error: Internal Server Error", str(ctx.exception))

    @patch("weather_journal.cli.get_current")
    def test_cmd_log_error_output(self, mock_get_current):
        from io import StringIO
        from types import SimpleNamespace
        from contextlib import redirect_stdout
        from weather_journal.cli import cmd_log

        mock_get_current.side_effect = ValueError("City 'FakeCity' not found.")

        out = StringIO()
        with redirect_stdout(out):
            cmd_log(SimpleNamespace(city="FakeCity", key="fake-key", db="test.db"))

        self.assertEqual(out.getvalue().strip(), "Error fetching weather: City 'FakeCity' not found.")


if __name__ == "__main__":
    unittest.main()
