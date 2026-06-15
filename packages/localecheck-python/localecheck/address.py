"""Best-effort UK/US address parsing into structured components.

v1 is regex-based (no libpostal dependency): detect country, extract a valid
postcode/ZIP, and a best-guess city. Returns a confidence flag so agents know
when to fall back. Validation of *real* deliverability is out of scope for v1.
"""
import re

# Official-form UK postcode pattern
_UK_POSTCODE = re.compile(
    r"\b(GIR ?0AA|[A-PR-UWYZ][A-HK-Y]?[0-9][0-9A-HJKPS-UW]? ?[0-9][ABD-HJLNP-UW-Z]{2})\b",
    re.IGNORECASE,
)
# US: STATE-abbrev + 5(-4) ZIP, e.g. "CA 94043" or "NY 10001-1234"
_US_STATE_ZIP = re.compile(
    r"\b([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b"
)
_US_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC",
}
_UK_HINT = re.compile(r"\b(United Kingdom|U\.?K\.?|England|Scotland|Wales|Northern Ireland)\b", re.I)
_US_HINT = re.compile(r"\b(United States|U\.?S\.?A?\.?)\b", re.I)


def parse_address(text: str) -> dict:
    """Parse a UK or US address string into {country, postcode, city}."""
    raw = (text or "").strip()
    if not raw:
        return {"ok": False, "reason": "empty input"}

    uk_pc = _UK_POSTCODE.search(raw)
    us_sz = _US_STATE_ZIP.search(raw)
    us_state_valid = bool(us_sz and us_sz.group(1).upper() in _US_STATES)

    country, postcode, state = None, None, None

    # Decide country: prefer a structurally valid postcode match
    if uk_pc and not us_state_valid:
        country = "GB"
        postcode = _normalise_uk(uk_pc.group(1))
    elif us_state_valid:
        country = "US"
        state = us_sz.group(1).upper()
        postcode = us_sz.group(2)
    elif _UK_HINT.search(raw):
        country = "GB"
        postcode = _normalise_uk(uk_pc.group(1)) if uk_pc else None
    elif _US_HINT.search(raw):
        country = "US"

    city = _guess_city(raw, country, postcode, state)
    confidence = _confidence(country, postcode, city)

    return {
        "ok": True,
        "input": raw,
        "country": country,
        "postcode": postcode,
        "state": state,
        "city": city,
        "confidence": confidence,
    }


def _normalise_uk(pc: str) -> str:
    pc = re.sub(r"\s+", "", pc).upper()
    # canonical form: space before the final 3 chars
    return pc[:-3] + " " + pc[-3:]


def _guess_city(raw, country, postcode, state):
    parts = [p.strip() for p in re.split(r",", raw) if p.strip()]
    if not parts:
        return None
    if country == "US" and state and postcode:
        # city is usually the segment immediately before "ST ZIP"
        for i, p in enumerate(parts):
            if state in p and postcode in p and i > 0:
                return parts[i - 1]
    if country == "GB" and postcode:
        # city is usually the segment containing the postcode, minus the postcode
        for p in parts:
            if re.sub(r"\s+", "", postcode.replace(" ", "")).upper() in re.sub(r"\s+", "", p).upper():
                cleaned = _UK_POSTCODE.sub("", p).strip(" ,")
                if cleaned:
                    return cleaned
        # else the segment before the last (country) one
        return parts[-2] if len(parts) >= 2 else None
    return None


def _confidence(country, postcode, city):
    score = 0
    if country:
        score += 1
    if postcode:
        score += 1
    if city:
        score += 1
    return {0: "none", 1: "low", 2: "medium", 3: "high"}[score]
