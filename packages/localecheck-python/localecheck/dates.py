"""Locale-aware date parsing -> ISO 8601, or INVALID."""
import re
from dateutil import parser as dtparser

# locale -> day-first ordering for ambiguous numeric dates
_DAYFIRST = {"en-GB": True, "en-US": False}
# Unambiguous ISO 8601 calendar date (YYYY-MM-DD) — must never be reordered
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_date(text: str, locale: str = "en-GB") -> dict:
    """Parse an ambiguous human date string for a locale.

    Returns {"iso": "YYYY-MM-DD", "valid": True} or {"valid": False, ...}.
    Respects day/month ordering for the locale instead of assuming US MM/DD.
    ISO 8601 input (YYYY-MM-DD) is always read as-is regardless of locale.
    """
    locale = locale or "en-GB"
    dayfirst = _DAYFIRST.get(locale, True)
    s = str(text).strip() if text else ""
    if not s:
        return {"valid": False, "reason": "empty input", "locale": locale}
    # ISO dates are unambiguous: do not apply locale day/month reordering
    if _ISO_DATE.match(s):
        dayfirst = False
    try:
        dt = dtparser.parse(s, dayfirst=dayfirst, fuzzy=False)
    except (ValueError, OverflowError) as e:
        return {"valid": False, "reason": f"unparseable or impossible date: {e}",
                "locale": locale, "input": text}
    return {"valid": True, "iso": dt.date().isoformat(),
            "locale": locale, "dayfirst": dayfirst, "input": text}
