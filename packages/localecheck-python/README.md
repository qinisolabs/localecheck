# localecheck — locale-correctness API for AI agents (UK + USA v1)

A working API that gives agents *verified* answers to the "boring" international
data they otherwise hallucinate: dates, phone numbers, currency formatting,
VAT/sales-tax (date-sensitive), public holidays, and addresses.

This v1 is scoped to **the UK and USA** and is fully runnable. It wraps
authoritative open libraries where they exist and adds hand-curated tax data
where they don't.

## What's real vs. what's wrapped

| Capability | Backed by | Data effort |
|---|---|---|
| `parse_date` | python-dateutil + locale day/month rules | logic only |
| `validate_phone` | Google libphonenumber (`phonenumbers`) | none — library |
| `format_currency` | babel / Unicode CLDR | none — library |
| `is_holiday` / `next_holiday` | python-holidays (national) | none — library |
| `tax_rate` (UK VAT by date) | **hand-curated** `data/uk_vat.json` | curated, the moat |
| `tax_rate` (US sales tax) | **hand-curated** `data/us_sales_tax.json` | curated |
| `parse_address` | regex (UK postcode / US state+ZIP) | logic; validation deferred |

## Run it

```bash
pip install -r requirements.txt

# tests (23, all green)
pytest -q

# REST API + interactive docs at http://127.0.0.1:8000/docs
uvicorn app:app --reload

# MCP server for agents (stdio)
pip install mcp
python mcp_server.py
```

## Example calls

```
GET /v1/date/parse?input=03/04/2025&locale=en-GB
    -> {"valid": true, "iso": "2025-04-03", ...}      # day-first, not US month-first

GET /v1/tax/rate?country=GB&date=2009-06-01
    -> {"rate": 15.0, "effective_from": "2008-12-01", "note": "Temporary cut ..."}

GET /v1/tax/rate?country=US&state=CA
    -> {"rate": 7.25, "scope": "state base rate (local taxes add on top)"}

GET /v1/phone/validate?number=020%207946%200958&region=GB
    -> {"valid": true, "e164": "+442079460958", "type": "fixed_line"}

GET /v1/currency/format?amount=1234.5&currency=GBP&locale=en-GB
    -> {"formatted": "£1,234.50"}

GET /v1/holiday/check?date=2025-12-26&country=GB
    -> {"is_holiday": true, "name": "Boxing Day"}

GET /v1/address/parse?input=1600 Amphitheatre Parkway, Mountain View, CA 94043, USA
    -> {"country": "US", "postcode": "94043", "city": "Mountain View", "confidence": "high"}
```

The MCP server exposes the same seven functions as agent tools, so an agent can
call `localecheck.tax_rate(country="GB", date="2020-07-15")` directly.

## Layout

```
localecheck/
  dates.py phone.py currency.py holidays_.py vat.py address.py
  data/uk_vat.json          # UK VAT standard-rate history by date
  data/us_sales_tax.json    # US state base sales-tax rates
app.py                      # FastAPI REST surface
mcp_server.py               # MCP (stdio) server wrapping the same functions
test_localecheck.py         # 23 end-to-end tests
```

## Accuracy & caveats (read before trusting in production)

- **UK VAT** standard-rate history is from public HMRC records and is reliable
  for the modern era (1991→). It models the *standard* rate only — reduced (5%)
  and zero rates are separate. Note: the UK did **not** cut its standard rate
  during COVID (it cut hospitality to 5%); the standard rate stayed 20%.
- **US sales tax** values are commonly published 2025 **state base** rates.
  Local (county/city/district) taxes add on top and the API does not model them.
  Five states levy no state sales tax. **Do not use these for live invoicing
  without verifying against an authoritative feed** (e.g. a commercial tax API).
  Each rate carries a `last_verified` date and per-state notes where relevant.
- **Addresses**: v1 parses and extracts a structurally valid postcode/ZIP; it
  does **not** verify the address is real/deliverable. Returns a `confidence`
  flag so agents can fall back.
- **Holidays**: backed by python-holidays. **GB defaults to England** (the bare
  "GB" calendar in the library is an incomplete subset that omits Easter Monday
  and the Late Summer Bank Holiday). Override with `subdiv` for Scotland (`SCT`),
  Wales (`WLS`), or Northern Ireland (`NIR`) — these genuinely differ (e.g. 2 Jan
  and St Andrew's Day in Scotland). US defaults to the 11 federal holidays; pass
  a state subdiv for state-specific days.

## What to build next

1. **Expand VAT/tax coverage** to more countries (this curated data is the
   defensible asset — the libraries above are commodity).
2. **Address validation** via libpostal + national postcode datasets.
3. **Auth + usage metering** (API keys, per-call billing) to turn this into a
   product.
4. **Run the eval** (see the sibling `locale-eval` project) against frontier
   models to keep proving the gap is real and durable.
