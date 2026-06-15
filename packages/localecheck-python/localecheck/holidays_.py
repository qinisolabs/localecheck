"""Public-holiday checks via python-holidays (national level)."""
import datetime as _dt
import holidays as _holidays

_SUPPORTED = {"GB", "US"}

# The bare "GB" calendar in python-holidays is an incomplete common subset
# (it omits Easter Monday and the Late Summer Bank Holiday, which ARE bank
# holidays in England & Wales). Default to England so the answer is complete;
# callers can override with subdiv (ENG/SCT/WLS/NIR). US default = federal.
_DEFAULT_SUBDIV = {"GB": "ENG"}


def _parse_date(date_str):
    return _dt.date.fromisoformat(str(date_str))


def is_holiday(date: str, country: str = "GB", subdiv: str = None) -> dict:
    """Is `date` (YYYY-MM-DD) a public holiday in `country`?

    subdiv optionally narrows to a region/state (e.g. 'England', 'CA').
    """
    country = (country or "GB").upper()
    if country not in _SUPPORTED:
        return {"ok": False, "reason": f"country {country} not supported in v1"}
    try:
        d = _parse_date(date)
    except ValueError as e:
        return {"ok": False, "reason": f"bad date: {e}"}
    used_subdiv = subdiv or _DEFAULT_SUBDIV.get(country)
    try:
        cal = _holidays.country_holidays(country, years=d.year, subdiv=used_subdiv)
    except Exception as e:
        return {"ok": False, "reason": str(e)}
    name = cal.get(d)
    return {"ok": True, "date": d.isoformat(), "country": country,
            "subdiv": used_subdiv, "is_holiday": name is not None, "name": name}


def next_holiday(country: str = "GB", after: str = None, subdiv: str = None) -> dict:
    """Return the next public holiday on or after `after` (default today)."""
    country = (country or "GB").upper()
    if country not in _SUPPORTED:
        return {"ok": False, "reason": f"country {country} not supported in v1"}
    start = _parse_date(after) if after else _dt.date.today()
    used_subdiv = subdiv or _DEFAULT_SUBDIV.get(country)
    for yr in (start.year, start.year + 1):
        cal = _holidays.country_holidays(country, years=yr, subdiv=used_subdiv)
        upcoming = sorted(d for d in cal if d >= start)
        if upcoming:
            d = upcoming[0]
            return {"ok": True, "country": country, "subdiv": used_subdiv,
                    "date": d.isoformat(), "name": cal.get(d)}
    return {"ok": False, "reason": "none found in window"}
