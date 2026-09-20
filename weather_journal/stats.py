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
    """Counts how many entries observed rain."""
    if not entries:
        return 0
    return sum(1 for e in entries if "rain" in e.get("condition", "").lower())
