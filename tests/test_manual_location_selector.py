"""A city saved with `add` and the same city from `log` can both be selected by name."""

import io
import sqlite3
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from weather_journal.cli import main
from weather_journal.store import get_history

MUMBAI_FROM_API = {
    "city": "Mumbai",
    "temp": 31.2,
    "humidity": 70,
    "condition": "haze",
    "location": {
        "provider": "openweathermap",
        "provider_id": 1275339,
        "requested_name": "Mumbai",
        "country": "IN",
        "latitude": 19.0144,
        "longitude": 72.8479,
    },
}


class TestManualLocationSelector(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "weather.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def _cli(self, *args):
        out = io.StringIO()
        argv = ["weather_journal", "--db", self.db_path] + list(args)
        with patch.object(sys, "argv", argv):
            with patch("weather_journal.cli.get_current", return_value=MUMBAI_FROM_API):
                with redirect_stdout(out):
                    main()
        return out.getvalue()

    def _add_then_log_mumbai(self):
        self._cli("add", "Mumbai", "30", "80", "haze")
        self._cli("log", "Mumbai")

    def test_bare_name_is_ambiguous_and_suggests_a_manual_label(self):
        self._add_then_log_mumbai()

        output = self._cli("history", "Mumbai")

        self.assertEqual(
            output.strip(),
            "Location 'Mumbai' is ambiguous. Choose one of: "
            "Mumbai [manual], Mumbai, IN (19.0144, 72.8479) [owm:1275339]",
        )

    def test_suggested_manual_label_selects_only_the_manual_entries(self):
        self._add_then_log_mumbai()

        history = self._cli("history", "Mumbai [manual]")
        self.assertIn("30.0°C", history)
        self.assertNotIn("31.2°C", history)

        stats = self._cli("stats", "Mumbai [manual]")
        self.assertIn("Total Observations: 1", stats)
        self.assertIn("Average Temperature: 30.0°C", stats)

    def test_api_entries_stay_selectable_by_id(self):
        self._add_then_log_mumbai()

        history = self._cli("history", "owm:1275339")

        self.assertIn("31.2°C", history)
        self.assertNotIn("30.0°C", history)

    def test_manual_label_ignores_letter_case(self):
        self._add_then_log_mumbai()

        records = get_history("mumbai [MANUAL]", db_path=self.db_path)

        self.assertEqual([r["temp"] for r in records], [30.0])

    def test_manual_and_legacy_rows_each_have_a_working_label(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                temp REAL NOT NULL,
                humidity INTEGER,
                condition TEXT,
                logged_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            INSERT INTO entries (city, temp, humidity, condition, logged_at)
            VALUES ('Mumbai', 25, 60, 'mist', '2026-10-01 12:00:00')
        """)
        conn.commit()
        conn.close()
        self._cli("add", "Mumbai", "30", "80", "haze")

        output = self._cli("history", "Mumbai")
        self.assertEqual(
            output.strip(),
            "Location 'Mumbai' is ambiguous. Choose one of: Mumbai [manual], Mumbai [legacy]",
        )

        legacy = get_history("Mumbai [legacy]", db_path=self.db_path)
        manual = get_history("Mumbai [manual]", db_path=self.db_path)
        self.assertEqual([r["temp"] for r in legacy], [25.0])
        self.assertEqual([r["temp"] for r in manual], [30.0])

    def test_unambiguous_manual_city_still_works_by_its_plain_name(self):
        self._cli("add", "Pune", "25.5", "60", "Rain")

        output = self._cli("history", "pune")

        self.assertNotIn("ambiguous", output)
        self.assertIn("25.5°C", output)


if __name__ == "__main__":
    unittest.main()
