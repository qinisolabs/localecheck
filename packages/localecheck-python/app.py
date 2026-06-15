"""localecheck REST API (FastAPI). UK + USA v1.

Run:  uvicorn app:app --reload
Docs: http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, Query
from localecheck import __version__, SUPPORTED_COUNTRIES
from localecheck.dates import parse_date
from localecheck.phone import validate_phone
from localecheck.currency import format_money
from localecheck.holidays_ import is_holiday, next_holiday
from localecheck.vat import vat_rate
from localecheck.address import parse_address

app = FastAPI(
    title="localecheck",
    version=__version__,
    description="Locale-correctness API for AI agents — UK + USA v1. "
                "Verified dates, phone, currency, VAT/sales-tax, holidays, addresses.",
)


@app.get("/health")
def health():
    return {"status": "ok", "version": __version__, "countries": SUPPORTED_COUNTRIES}


@app.get("/v1/date/parse")
def date_parse(input: str = Query(..., description="e.g. 03/04/2025"),
               locale: str = Query("en-GB", description="en-GB or en-US")):
    return parse_date(input, locale)


@app.get("/v1/phone/validate")
def phone_validate(number: str = Query(..., description="raw phone number"),
                   region: str = Query("GB", description="GB or US")):
    return validate_phone(number, region)


@app.get("/v1/currency/format")
def currency_format(amount: float = Query(...),
                    currency: str = Query("GBP"),
                    locale: str = Query(None, description="e.g. en-GB, en-US")):
    return format_money(amount, currency, locale)


@app.get("/v1/tax/rate")
def tax_rate(country: str = Query("GB", description="GB or US"),
             date: str = Query(None, description="YYYY-MM-DD (UK VAT is date-sensitive)"),
             state: str = Query(None, description="US state code, e.g. CA")):
    return vat_rate(country, date, state)


@app.get("/v1/holiday/check")
def holiday_check(date: str = Query(..., description="YYYY-MM-DD"),
                  country: str = Query("GB"),
                  subdiv: str = Query(None, description="region/state, e.g. England, CA")):
    return is_holiday(date, country, subdiv)


@app.get("/v1/holiday/next")
def holiday_next(country: str = Query("GB"),
                 after: str = Query(None, description="YYYY-MM-DD, default today"),
                 subdiv: str = Query(None)):
    return next_holiday(country, after, subdiv)


@app.get("/v1/address/parse")
def address_parse(input: str = Query(..., description="full address string")):
    return parse_address(input)
