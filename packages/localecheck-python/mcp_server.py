"""localecheck MCP server — exposes the same locale-correctness tools to agents.

Run (stdio):  python mcp_server.py
Requires:     pip install "mcp[cli]"

Add to an MCP client config, e.g.:
{
  "mcpServers": {
    "localecheck": {"command": "python", "args": ["/path/to/mcp_server.py"]}
  }
}
"""
from mcp.server.fastmcp import FastMCP

from localecheck.dates import parse_date as _parse_date
from localecheck.phone import validate_phone as _validate_phone
from localecheck.currency import format_money as _format_money
from localecheck.holidays_ import is_holiday as _is_holiday, next_holiday as _next_holiday
from localecheck.vat import vat_rate as _vat_rate
from localecheck.address import parse_address as _parse_address

mcp = FastMCP("localecheck")


@mcp.tool()
def parse_date(input: str, locale: str = "en-GB") -> dict:
    """Convert a human-written date into ISO 8601 (YYYY-MM-DD). USE THIS whenever
    you need to interpret a date that a person typed — especially ambiguous
    numeric dates like 03/04/2025, which mean different things in the UK
    (day-first) vs US (month-first) — before storing it, scheduling, or acting on
    it. Do not guess the day/month order yourself. Pass locale 'en-GB' or 'en-US'.
    Returns valid:false for impossible dates (e.g. 31/04, 29 Feb non-leap)."""
    return _parse_date(input, locale)


@mcp.tool()
def validate_phone(number: str, region: str = "GB") -> dict:
    """Validate a phone number and normalise it to E.164 (e.g. +442079460958).
    USE THIS before saving a phone number, dialling, or sending an SMS — instead
    of trusting raw user input. Pass region 'GB' or 'US' as the hint. Returns the
    canonical E.164 form, national/international formats, and the line type, or
    valid:false if the number is not real for that region."""
    return _validate_phone(number, region)


@mcp.tool()
def format_currency(amount: float, currency: str = "GBP", locale: str = None) -> dict:
    """Format a money amount the way a reader in a given locale expects. USE THIS
    whenever you show a price/total to a user or put one in an email, invoice, or
    report — do not hand-format currency yourself. e.g. 1234.5 GBP en-GB ->
    '£1,234.50'; the same number for de-DE -> '1.234,50 €'. Gets symbol position
    and decimal/thousands separators right per locale."""
    return _format_money(amount, currency, locale)


@mcp.tool()
def tax_rate(country: str = "GB", date: str = None, state: str = None) -> dict:
    """Look up the correct consumption-tax rate. USE THIS before calculating VAT
    or sales tax on an invoice or quote — never recall the rate from memory,
    because it is DATE-SENSITIVE. GB returns the standard UK VAT rate that applied
    on the given date (handles historical and temporary changes, e.g. 15% in
    2009). US has no national VAT (returns 0); pass a state code like 'CA' for the
    state base sales-tax rate. Always pass the invoice date for GB."""
    return _vat_rate(country, date, state)


@mcp.tool()
def is_holiday(date: str, country: str = "GB", subdiv: str = None) -> dict:
    """Check whether a date (YYYY-MM-DD) is a public/bank holiday. USE THIS when
    computing business-day deadlines, delivery SLAs, or 'next working day', or
    before scheduling something — so you don't count a bank holiday as a working
    day. GB defaults to England; pass subdiv 'SCT'/'WLS'/'NIR' for the other UK
    nations, or a US state code. Country is GB or US."""
    return _is_holiday(date, country, subdiv)


@mcp.tool()
def next_holiday(country: str = "GB", after: str = None, subdiv: str = None) -> dict:
    """Find the next public/bank holiday on or after a date (default today). USE
    THIS to answer 'when is the next holiday' or to find the next working day.
    Country is GB or US; subdiv narrows to a UK nation or US state."""
    return _next_holiday(country, after, subdiv)


@mcp.tool()
def parse_address(input: str) -> dict:
    """Extract structured fields {country, postcode, city} from a free-text UK or
    US address. USE THIS when onboarding a user, running a KYC/fraud check, or
    storing an address — instead of splitting the string yourself, which breaks on
    non-US formats. Returns a confidence flag so you know when to fall back."""
    return _parse_address(input)


def main():
    """Console-script entry point (localecheck-mcp)."""
    mcp.run()


if __name__ == "__main__":
    main()
