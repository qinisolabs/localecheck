"""Tax-rate lookups: UK VAT by date, US sales tax by state.

This is the hand-curated, date-sensitive part — the bit a raw LLM cannot know
and the most defensible piece of the product.
"""
import datetime as _dt
import json
import os

_DATA = os.path.join(os.path.dirname(__file__), "data")


def _load(name):
    with open(os.path.join(_DATA, name), encoding="utf-8") as f:
        return json.load(f)


_UK = _load("uk_vat.json")
_US = _load("us_sales_tax.json")


def _uk_vat(date_str):
    try:
        d = _dt.date.fromisoformat(str(date_str))
    except ValueError as e:
        return {"ok": False, "reason": f"bad date: {e}"}
    history = _UK["standard_rate_history"]
    # find the last band whose start is <= date
    applicable = None
    for band in history:
        if _dt.date.fromisoformat(band["from"]) <= d:
            applicable = band
        else:
            break
    if applicable is None:
        return {"ok": False, "reason": f"no UK VAT rate recorded for {date_str} "
                f"(records start {history[0]['from']})"}
    return {"ok": True, "country": "GB", "tax_name": "VAT",
            "rate": applicable["rate"], "date": d.isoformat(),
            "effective_from": applicable["from"], "kind": "standard",
            "note": applicable.get("note"),
            "source": _UK["source"], "last_verified": _UK["last_verified"]}


def _us_tax(date_str, state):
    nat = {"ok": True, "country": "US", "tax_name": "Sales tax",
           "national_vat": 0.0, "date": date_str,
           "note": _US["note"], "source": _US["source"],
           "last_verified": _US["last_verified"]}
    if not state:
        nat["rate"] = 0.0
        nat["scope"] = "national (US has no VAT; supply a state for sales tax)"
        return nat
    state = state.upper()
    rates = _US["state_base_rates"]
    if state not in rates:
        return {"ok": False, "reason": f"unknown US state code: {state}"}
    nat["rate"] = rates[state]
    nat["scope"] = "state base rate (local taxes add on top)"
    nat["state"] = state
    if state in _US.get("rate_notes", {}):
        nat["state_note"] = _US["rate_notes"][state]
    return nat


def vat_rate(country: str = "GB", date: str = None, state: str = None) -> dict:
    """Look up the applicable consumption-tax rate.

    GB -> standard VAT for the given date (handles historical/temporary changes).
    US -> national VAT is 0; pass `state` (e.g. 'CA') for the state base sales-tax rate.
    """
    country = (country or "GB").upper()
    date = date or _dt.date.today().isoformat()
    if country == "GB":
        return _uk_vat(date)
    if country == "US":
        return _us_tax(date, state)
    return {"ok": False, "reason": f"country {country} not supported in v1 (GB, US only)"}
