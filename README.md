# localecheck

**Locale-correctness tools for AI agents.** Agents are systematically wrong about
everyday non-US data — they read `03/04` as March 4 in the UK, apply today's VAT
rate to a historical invoice, format `€1,234.50` for a German reader, and miss
bank holidays in delivery dates. localecheck gives them *verified* answers and
flags impossible inputs instead of guessing.

Coverage: **UK + USA** (v1), expanding. Free, no API key.

## Packages

| | Package | Install | Use |
|---|---|---|---|
| **TypeScript** (primary) | [`packages/localecheck-ts`](packages/localecheck-ts) | `npx -y localecheck` | MCP server **and** importable library |
| **Python** | [`packages/localecheck-python`](packages/localecheck-python) | `pip install localecheck` / `uvx` | MCP server, importable library, REST API |

Both wrap the same authoritative libraries (libphonenumber, CLDR/Intl,
date-holidays) and share the same hand-curated tax data.

## What it does

`parse_date` · `validate_phone` · `format_currency` · `tax_rate` (VAT/sales-tax
by date) · `is_holiday` / `next_holiday` · `parse_address`

## Quick start (in an AI app)

```json
{ "mcpServers": { "localecheck": { "command": "npx", "args": ["-y", "localecheck"] } } }
```

Then ask naturally — the agent picks the tool: *"A UK invoice dated 1 June 2009 —
what VAT rate?"* → **15%**.

## Repo map

- `packages/localecheck-ts` — primary TypeScript package (MCP + library)
- `packages/localecheck-python` — Python package + FastAPI REST API
- `eval/` — benchmark harness: how often raw LLMs get this wrong
- `benchmark.html` — shareable results page · `BUSINESS_MODEL.md` — strategy ·
  `PUBLISH.md` — release steps · `LOCAL_TEST.md` — test before publishing

## Status & caveats

UK VAT history is reliable for the modern era (standard rate). US state
sales-tax values are 2025 **state base** rates (local taxes add on top) — verify
against an authoritative feed before live invoicing. Addresses parse + extract a
valid postcode/ZIP but don't verify deliverability.

Code: Apache-2.0. Curated tax data: see `BUSINESS_MODEL.md`.
