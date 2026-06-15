"""End-to-end tests for localecheck core + REST API."""
from fastapi.testclient import TestClient
from app import app

from localecheck.dates import parse_date
from localecheck.phone import validate_phone
from localecheck.currency import format_money
from localecheck.holidays_ import is_holiday
from localecheck.vat import vat_rate
from localecheck.address import parse_address

client = TestClient(app)


# ---------- dates ----------
def test_date_gb_dayfirst():
    assert parse_date("03/04/2025", "en-GB")["iso"] == "2025-04-03"

def test_date_us_monthfirst():
    assert parse_date("03/04/2025", "en-US")["iso"] == "2025-03-04"

def test_date_invalid_leap():
    assert parse_date("29/02/2023", "en-GB")["valid"] is False

def test_date_invalid_month():
    assert parse_date("31/04/2025", "en-GB")["valid"] is False

def test_date_iso_not_reordered():
    # regression: ISO input must NOT be reordered by locale dayfirst
    assert parse_date("2025-09-08", "en-GB")["iso"] == "2025-09-08"


# ---------- phone ----------
def test_phone_gb_valid():
    r = validate_phone("020 7946 0958", "GB")
    assert r["valid"] and r["e164"] == "+442079460958"

def test_phone_us_valid():
    r = validate_phone("(212) 555-0199", "US")
    assert r["valid"] and r["e164"] == "+12125550199"

def test_phone_invalid():
    assert validate_phone("123", "GB")["valid"] is False


# ---------- currency ----------
def test_currency_gbp():
    assert format_money(1234.5, "GBP", "en-GB")["formatted"] == "£1,234.50"

def test_currency_usd():
    assert format_money(1234.5, "USD", "en-US")["formatted"] == "$1,234.50"


# ---------- VAT / sales tax (the date-sensitive bit) ----------
def test_uk_vat_current():
    assert vat_rate("GB", "2025-06-01")["rate"] == 20.0

def test_uk_vat_temporary_2009():
    # temporary 15% during the financial crisis
    assert vat_rate("GB", "2009-06-01")["rate"] == 15.0

def test_uk_vat_175_era():
    assert vat_rate("GB", "2010-06-01")["rate"] == 17.5

def test_us_national_zero():
    assert vat_rate("US", "2025-06-01")["rate"] == 0.0

def test_us_state_rate():
    r = vat_rate("US", "2025-06-01", state="CA")
    assert r["rate"] == 7.25 and r["state"] == "CA"


# ---------- holidays ----------
def test_uk_boxing_day():
    assert is_holiday("2025-12-26", "GB")["is_holiday"] is True

def test_us_july4_not_uk():
    assert is_holiday("2025-07-04", "GB")["is_holiday"] is False

def test_us_july4():
    assert is_holiday("2025-07-04", "US")["is_holiday"] is True

def test_uk_default_includes_easter_monday():
    # regression: bare GB calendar omits Easter Monday; default must be complete
    assert is_holiday("2025-04-21", "GB")["is_holiday"] is True

def test_uk_default_includes_summer_bank_holiday():
    assert is_holiday("2025-08-25", "GB")["is_holiday"] is True

def test_uk_scotland_subdiv_override():
    # 2 Jan is a Scotland-only bank holiday
    assert is_holiday("2025-01-02", "GB", subdiv="SCT")["is_holiday"] is True
    assert is_holiday("2025-01-02", "GB", subdiv="ENG")["is_holiday"] is False


# ---------- address ----------
def test_address_uk():
    r = parse_address("221B Baker Street, London NW1 6XE, United Kingdom")
    assert r["country"] == "GB" and r["postcode"] == "NW1 6XE"

def test_address_us():
    r = parse_address("1600 Amphitheatre Parkway, Mountain View, CA 94043, USA")
    assert r["country"] == "US" and r["postcode"] == "94043" and r["state"] == "CA"


# ---------- REST API smoke ----------
def test_api_health():
    assert client.get("/health").json()["status"] == "ok"

def test_api_tax_endpoint():
    r = client.get("/v1/tax/rate", params={"country": "GB", "date": "2009-06-01"})
    assert r.status_code == 200 and r.json()["rate"] == 15.0

def test_api_date_endpoint():
    r = client.get("/v1/date/parse", params={"input": "12/01/2024", "locale": "en-GB"})
    assert r.json()["iso"] == "2024-01-12"

def test_api_phone_endpoint():
    r = client.get("/v1/phone/validate", params={"number": "07911 123456", "region": "GB"})
    assert r.json()["valid"] is True
