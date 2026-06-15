"""
Generate ground-truth test cases for phone, currency formatting, and holidays
using authoritative libraries (phonenumbers, babel, holidays).

The point: these libraries ARE the kind of correctness the proposed API would sell.
This eval measures how often a raw LLM disagrees with them. A high disagreement
rate = a real problem worth solving.

Run:  python generate_dataset.py
Writes JSON files into ./data/
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def gen_phone():
    import phonenumbers
    # (raw_input, region_hint) pairs — deliberately messy formatting
    samples = [
        ("020 7946 0958", "GB"),
        ("+44 7911 123456", "GB"),
        ("07911 123456", "GB"),
        ("(030) 12345678", "DE"),
        ("+49 30 12345678", "DE"),
        ("06 12345678", "NL"),
        ("+31 6 12345678", "NL"),
        ("01 234 5678", "IE"),
        ("+353 1 234 5678", "IE"),
        ("06 12 34 56 78", "FR"),
        ("+33 6 12 34 56 78", "FR"),
        ("03-1234-5678", "JP"),
        ("+81 3 1234 5678", "JP"),
        ("(11) 98765-4321", "BR"),
        ("+55 11 98765-4321", "BR"),
        ("098765 43210", "IN"),
        ("+91 98765 43210", "IN"),
        ("0412 345 678", "AU"),
        ("+61 412 345 678", "AU"),
        ("044 668 18 00", "CH"),
        ("212-555-0199", "US"),
        ("+1 212-555-0199", "US"),
        ("123", "GB"),               # invalid: too short
        ("not a phone", "GB"),       # invalid: garbage
        ("+44 1234", "GB"),          # invalid: incomplete
    ]
    cases = []
    for i, (raw, region) in enumerate(samples):
        try:
            num = phonenumbers.parse(raw, region)
            valid = phonenumbers.is_valid_number(num)
            e164 = phonenumbers.format_number(
                num, phonenumbers.PhoneNumberFormat.E164) if valid else "INVALID"
        except phonenumbers.NumberParseException:
            valid, e164 = False, "INVALID"
        cases.append({
            "id": f"phone-{i}",
            "input": raw,
            "region": region,
            "expected": e164,            # E.164 string, or "INVALID"
        })
    return {
        "category": "phone",
        "description": "Validate and normalise a phone number to E.164 given a region hint. Ground truth from libphonenumber (phonenumbers). 'INVALID' means not a valid number.",
        "cases": cases,
    }


def gen_currency():
    from babel.numbers import format_currency
    # (amount, currency, locale)
    samples = [
        (1234.5, "EUR", "de_DE"),
        (1234.5, "EUR", "en_IE"),
        (1234.5, "EUR", "fr_FR"),
        (1234.5, "EUR", "nl_NL"),
        (1234.5, "GBP", "en_GB"),
        (1234.5, "USD", "en_US"),
        (1234567.89, "JPY", "ja_JP"),
        (1234567.89, "USD", "en_US"),
        (1234.5, "CHF", "de_CH"),
        (1234.5, "BRL", "pt_BR"),
        (1234567.5, "INR", "en_IN"),   # Indian digit grouping (lakh/crore)
        (1234.5, "SEK", "sv_SE"),
        (1234.5, "NOK", "nb_NO"),
        (1234.5, "AUD", "en_AU"),
        (1234.5, "CAD", "en_CA"),
        (1234.5, "CAD", "fr_CA"),
        (0.5, "EUR", "de_DE"),
        (1000000, "EUR", "de_DE"),
    ]
    cases = []
    for i, (amount, cur, loc) in enumerate(samples):
        expected = format_currency(amount, cur, locale=loc)
        cases.append({
            "id": f"cur-{i}",
            "amount": amount,
            "currency": cur,
            "locale": loc.replace("_", "-"),
            "expected": expected,
        })
    return {
        "category": "currency_format",
        "description": "Format a numeric amount as a currency string for a given locale (correct symbol, position, decimal/grouping separators, and digits). Ground truth from babel/CLDR.",
        "cases": cases,
    }


def gen_holiday():
    import holidays as hol
    # (country, year, date, ...) -> is this date a public holiday?
    # Pick a mix of real holidays and non-holidays per country.
    probes = [
        ("GB", 2025, "2025-12-26"),  # Boxing Day - holiday
        ("GB", 2025, "2025-07-04"),  # not a UK holiday (US Independence Day)
        ("GB", 2025, "2025-05-05"),  # Early May bank holiday - holiday
        ("US", 2025, "2025-07-04"),  # Independence Day - holiday
        ("US", 2025, "2025-12-26"),  # not a US federal holiday
        ("US", 2025, "2025-11-27"),  # Thanksgiving 2025 - holiday
        ("DE", 2025, "2025-10-03"),  # German Unity Day - holiday
        ("DE", 2025, "2025-07-14"),  # not a German holiday (Bastille Day)
        ("FR", 2025, "2025-07-14"),  # Bastille Day - holiday
        ("FR", 2025, "2025-10-03"),  # not a French holiday
        ("IE", 2025, "2025-03-17"),  # St Patrick's Day - holiday
        ("JP", 2025, "2025-05-05"),  # Children's Day - holiday
        ("JP", 2025, "2025-12-25"),  # not a Japanese public holiday
        ("IN", 2025, "2025-01-26"),  # Republic Day - holiday
        ("AU", 2025, "2025-01-26"),  # Australia Day - holiday
        ("NL", 2025, "2025-04-27"),  # King's Day - holiday
        ("ES", 2025, "2025-10-12"),  # Fiesta Nacional - holiday
        ("IT", 2025, "2025-04-25"),  # Liberation Day - holiday
        ("CH", 2025, "2025-08-01"),  # Swiss National Day - holiday
        ("SE", 2025, "2025-06-06"),  # National Day of Sweden - holiday
    ]
    cases = []
    for i, (country, year, date) in enumerate(probes):
        try:
            cal = hol.country_holidays(country, years=year)
            is_hol = date in cal
        except Exception:
            continue
        cases.append({
            "id": f"hol-{i}",
            "country": country,
            "date": date,
            "expected": "YES" if is_hol else "NO",
        })
    return {
        "category": "holiday",
        "description": "Is the given date a public/national holiday in the given country? Answer YES or NO. Ground truth from the python-holidays library (national-level holidays).",
        "cases": cases,
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    generators = {
        "gen_phone.json": gen_phone,
        "gen_currency.json": gen_currency,
        "gen_holiday.json": gen_holiday,
    }
    for fname, fn in generators.items():
        try:
            payload = fn()
        except ImportError as e:
            print(f"SKIP {fname}: missing dependency ({e}). Run pip install -r requirements.txt")
            continue
        path = os.path.join(DATA_DIR, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"Wrote {path} ({len(payload['cases'])} cases)")


if __name__ == "__main__":
    main()
