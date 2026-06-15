# localecheck (TypeScript MCP server)

Locale-correctness tools for AI agents — verified **dates, phone numbers,
currency formatting, VAT/sales-tax by date, public holidays, and addresses**.
Coverage: UK + USA (v1). Free, no API key.

This is the **TypeScript / npm** build for the widest MCP-client reach. The same
tools also exist as a Python package + REST API (see the `locale-api` project).

## Add to your AI app (zero install via npx)

**Claude Desktop / Cursor / Cline** — add to your MCP config:

```json
{
  "mcpServers": {
    "localecheck": {
      "command": "npx",
      "args": ["-y", "localecheck"]
    }
  }
}
```

Restart the app and the `localecheck` tools appear. Then just ask naturally —
the agent picks the right tool:

- "An invoice is dated 1 June 2009 in the UK — what VAT applies?" → 15%
- "Is 21 April 2025 a working day in England?" → no (Easter Monday)
- "Format 1234.5 as GBP for a UK customer." → £1,234.50
- "My user in London typed 03/04/2025 — what date is that?" → 3 April 2025

## Use as a library (in code you/an agent are writing)

The same package is also a typed library — `npm install localecheck` then import
the functions directly:

```ts
import { vatRate, parseDate, formatMoney, validatePhone } from "localecheck";

vatRate("GB", "2009-06-01").rate;            // 15
parseDate("03/04/2025", "en-GB").iso;        // "2025-04-03"
formatMoney(1234.5, "GBP", "en-GB").formatted; // "£1,234.50"
validatePhone("020 7946 0958", "GB").e164;   // "+442079460958"
```

Full TypeScript types ship with the package. So one install covers both ways an
agent uses it: **live in a chat** (MCP server) and **baked into an app** (library).

## Tools

| Tool | Purpose |
|---|---|
| `parse_date` | Human date → ISO 8601, locale-aware day/month order; flags impossible dates |
| `validate_phone` | → E.164 + line type (libphonenumber-js) |
| `format_currency` | Locale-correct currency string (native Intl/CLDR) |
| `tax_rate` | UK VAT **by date** (historical/temporary); US state base sales tax |
| `is_holiday` | Public/bank-holiday check (date-holidays); GB defaults to England |
| `next_holiday` | Next public holiday on/after a date |
| `parse_address` | UK/US address → {country, postcode, city} + confidence |

## Develop

```bash
npm install
npm test       # 34 parity tests vs the Python implementation — all pass
npm run build  # tsc -> dist/
npm start      # run the MCP server over stdio
```

## What's wrapped vs curated

Phone (libphonenumber-js), currency/dates (native `Intl`), and holidays
(date-holidays) are authoritative libraries — zero data maintenance. The
**tax data** (`data/uk_vat.json`, `data/us_sales_tax.json`) is hand-curated and
is the defensible asset; see the main project's `BUSINESS_MODEL.md`.

## Caveats

- US state sales-tax values are 2025 **state base** rates (local taxes add on
  top); verify against an authoritative feed before live invoicing.
- UK VAT covers the **standard** rate by date (modern era reliable).
- Addresses parse + extract a valid postcode/ZIP; they do not verify
  deliverability. `confidence` flags low-certainty results.

Apache-2.0 (code). UK + USA v1, expanding.
