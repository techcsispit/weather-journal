"""Weather statistics calculations."""


def avg_temp(entries):
    """Calculates the average temperature across weather records."""
    if not entries:
        return None

    temps = [e["temp"] for e in entries if "temp" in e]
    if not temps:
        return None
    return round(sum(temps) / len(temps), 1)


def hottest_day(entries):
    """Finds the record with the highest temperature."""
    if not entries:
        return None
    return max(entries, key=lambda e: e.get("temp", -999))


def rainy_days(entries):
    """Counts unique calendar days that observed rain, drizzle, or thunderstorms."""
    if not entries:
        return 0

    rain_keywords = ("rain", "drizzle", "thunderstorm")
    rainy_dates = set()

    for e in entries:
        condition = (e.get("condition") or "").lower()
        if any(keyword in condition for keyword in rain_keywords):
            logged_at = e.get("logged_at") or ""
            date_str = logged_at.split()[0] if logged_at else None
            if date_str:
                rainy_dates.add(date_str)
            else:
                # If logged_at is missing, treat the entry itself as a rainy occurrence
                rainy_dates.add(id(e))

    return len(rainy_dates)
