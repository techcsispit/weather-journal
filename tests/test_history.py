"""Tests for the `history` command: newest first, one city if named, and `add` feeding it."""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from weather_journal.cli import main
from weather_journal.store import get_history, save_entry


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "weather.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def _cli(self, *args):
        """Run the real CLI against the temp database and return what it printed."""
        out = io.StringIO()
        with patch.object(sys, "argv", ["weather_journal", "--db", self.db_path] + list(args)):
            with redirect_stdout(out):
                main()
        return out.getvalue()

    def _save(self, city, temp, day):
        save_entry(city, temp, 60, "clear sky", logged_at=f"2026-10-0{day} 12:00:00",
                   db_path=self.db_path)

    def _save_three(self):
        self._save("Mumbai", 30.0, 1)
        self._save("London", 11.0, 2)
        self._save("Mumbai", 31.0, 3)

    def test_everything_is_listed_newest_first(self):
        self._save_three()

        records = get_history(db_path=self.db_path)

        self.assertEqual([r["temp"] for r in records], [31.0, 11.0, 30.0])
        self.assertEqual([r["logged_at"][:10] for r in records],
                         ["2026-10-03", "2026-10-02", "2026-10-01"])

    def test_history_output_prints_newest_row_first(self):
        self._save_three()

        output = self._cli("history")

        self.assertIn("All Weather History", output)
        newest = output.index("2026-10-03")
        middle = output.index("2026-10-02")
        oldest = output.index("2026-10-01")
        self.assertTrue(newest < middle < oldest)

    def test_naming_a_city_lists_only_that_city_newest_first(self):
        self._save_three()

        records = get_history("Mumbai", db_path=self.db_path)
        self.assertEqual([r["temp"] for r in records], [31.0, 30.0])
        self.assertEqual({r["city"] for r in records}, {"Mumbai"})

        output = self._cli("history", "Mumbai")
        self.assertIn("Weather History for Mumbai", output)
        self.assertNotIn("London", output)
        self.assertNotIn("2026-10-02", output)

    def test_city_filter_ignores_letter_case(self):
        self._save_three()

        records = get_history("mUMBAI", db_path=self.db_path)

        self.assertEqual([r["temp"] for r in records], [31.0, 30.0])

    def test_unknown_city_says_no_records_found(self):
        self._save_three()

        self.assertEqual(get_history("Paris", db_path=self.db_path), [])
        self.assertIn("No records found.", self._cli("history", "Paris"))

    def test_empty_database_says_no_records_found(self):
        self.assertIn("No records found.", self._cli("history"))

    def test_add_saves_an_entry_that_history_shows(self):
        added = self._cli("add", "Pune", "25.5", "60", "Rain")
        self.assertIn("Logged manually: Pune - 25.5°C, 60% humidity, Rain", added)

        records = get_history("Pune", db_path=self.db_path)
        self.assertEqual(len(records), 1)
        self.assertEqual(
            (records[0]["temp"], records[0]["humidity"], records[0]["condition"]),
            (25.5, 60, "Rain"),
        )
        output = self._cli("history")
        self.assertIn("Pune", output)
        self.assertIn("25.5°C", output)


if __name__ == "__main__":
    unittest.main()
