"""SQLite storage module for weather history."""

import sqlite3
from datetime import datetime
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "weather_journal.db"


class AmbiguousLocationError(ValueError):
    """Raised when a name refers to more than one stored location."""

    def __init__(self, selector, locations):
        self.selector = selector
        self.locations = locations
        choices = ", ".join(location["location_label"] for location in locations)
        super().__init__(f"Location '{selector}' is ambiguous. Choose one of: {choices}")


def _location_label(name, requested_name, country, latitude, longitude, provider_id):
    """Build a stable, human-readable selector for a location."""
    parts = [requested_name or name]
    if country and country.lower() not in (requested_name or "").lower():
        parts.append(country)
    label = ", ".join(parts)
    if latitude is not None and longitude is not None:
        label += f" ({latitude:.4f}, {longitude:.4f})"
    if provider_id:
        label += f" [owm:{provider_id}]"
    return label


def get_connection(db_path=DEFAULT_DB_PATH):
    """Establish a connection and migrate older databases in place."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            provider_id TEXT,
            name TEXT NOT NULL,
            requested_name TEXT,
            country TEXT,
            latitude REAL,
            longitude REAL,
            location_label TEXT NOT NULL,
            UNIQUE(provider, provider_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            temp REAL NOT NULL,
            humidity INTEGER,
            condition TEXT,
            logged_at TEXT NOT NULL,
            location_id INTEGER REFERENCES locations(id)
        )
    """)

    columns = {row["name"] for row in cursor.execute("PRAGMA table_info(entries)")}
    if "location_id" not in columns:
        cursor.execute("ALTER TABLE entries ADD COLUMN location_id INTEGER REFERENCES locations(id)")

    # Older rows have only a city name. Preserve them under an explicit legacy
    # identity; there is not enough information to guess their real location.
    legacy_cities = cursor.execute(
        "SELECT DISTINCT city FROM entries WHERE location_id IS NULL"
    ).fetchall()
    for row in legacy_cities:
        city = row["city"]
        provider_id = city.casefold()
        label = f"{city} [legacy]"
        cursor.execute("""
            INSERT OR IGNORE INTO locations
                (provider, provider_id, name, requested_name, location_label)
            VALUES ('legacy', ?, ?, ?, ?)
        """, (provider_id, city, city, label))
        location_id = cursor.execute(
            "SELECT id FROM locations WHERE provider = 'legacy' AND provider_id = ?",
            (provider_id,),
        ).fetchone()["id"]
        cursor.execute(
            "UPDATE entries SET location_id = ? WHERE location_id IS NULL AND LOWER(city) = LOWER(?)",
            (location_id, city),
        )

    conn.commit()
    return conn


def _get_or_create_location(conn, city, location):
    location = location or {}
    provider = str(location.get("provider") or "manual")
    provider_id = location.get("provider_id")
    requested_name = str(location.get("requested_name") or city)
    country = location.get("country")
    latitude = location.get("latitude")
    longitude = location.get("longitude")

    # Manual entries have no provider ID, so their full user-supplied location
    # text is their identity. API locations use the provider's stable city ID.
    if provider_id is None:
        if provider == "openweathermap" and latitude is not None and longitude is not None:
            provider_id = f"coord:{float(latitude):.6f},{float(longitude):.6f}"
        else:
            provider_id = requested_name.strip().casefold()
    provider_id = str(provider_id)
    label = _location_label(
        city, requested_name, country, latitude, longitude,
        provider_id if provider == "openweathermap" else None,
    )

    conn.execute("""
        INSERT INTO locations
            (provider, provider_id, name, requested_name, country,
             latitude, longitude, location_label)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(provider, provider_id) DO UPDATE SET
            name = excluded.name,
            requested_name = excluded.requested_name,
            country = excluded.country,
            latitude = excluded.latitude,
            longitude = excluded.longitude,
            location_label = excluded.location_label
    """, (
        provider, provider_id, city, requested_name, country,
        latitude, longitude, label,
    ))
    return conn.execute(
        "SELECT id FROM locations WHERE provider = ? AND provider_id = ?",
        (provider, provider_id),
    ).fetchone()["id"]


def save_entry(city, temp, humidity, condition, logged_at=None,
               db_path=DEFAULT_DB_PATH, location=None):
    """Save a weather observation with a stable location identity."""
    conn = get_connection(db_path)
    try:
        location_id = _get_or_create_location(conn, city, location)
        ts = logged_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("""
            INSERT INTO entries
                (city, temp, humidity, condition, logged_at, location_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (city, temp, humidity, condition, ts, location_id))
        conn.commit()
    finally:
        conn.close()


def _matching_locations(conn, selector):
    provider_selector = selector[4:] if selector.lower().startswith("owm:") else None
    if provider_selector:
        rows = conn.execute("""
            SELECT * FROM locations
            WHERE provider = 'openweathermap' AND provider_id = ?
        """, (provider_selector,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM locations
            WHERE LOWER(location_label) = LOWER(?)
               OR LOWER(requested_name) = LOWER(?)
               OR LOWER(name) = LOWER(?)
            ORDER BY location_label
        """, (selector, selector, selector)).fetchall()
    return [dict(row) for row in rows]


def get_history(city=None, db_path=DEFAULT_DB_PATH):
    """Retrieve records, refusing to merge ambiguous location names."""
    conn = get_connection(db_path)
    try:
        params = ()
        where = ""
        if city:
            locations = _matching_locations(conn, city)
            if not locations:
                return []
            if len(locations) > 1:
                raise AmbiguousLocationError(city, locations)
            where = "WHERE e.location_id = ?"
            params = (locations[0]["id"],)

        rows = conn.execute(f"""
            SELECT e.city, e.temp, e.humidity, e.condition, e.logged_at,
                   l.provider, l.provider_id, l.country, l.latitude,
                   l.longitude, l.location_label
            FROM entries AS e
            JOIN locations AS l ON l.id = e.location_id
            {where}
            ORDER BY e.id DESC
        """, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
