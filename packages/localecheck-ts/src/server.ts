#!/usr/bin/env node
// localecheck MCP server (TypeScript). UK + USA v1.
// Run: localecheck-mcp   (stdio transport)
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { parseDate } from "./dates.js";
import { validatePhone } from "./phone.js";
import { formatMoney } from "./currency.js";
import { isHoliday, nextHoliday } from "./holidays.js";
import { vatRate } from "./vat.js";
import { parseAddress } from "./address.js";

const server = new McpServer({ name: "localecheck", version: "0.1.0" });

const json = (data: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(data) }] });

server.tool(
  "parse_date",
  "Convert a human-written date into ISO 8601 (YYYY-MM-DD). USE THIS whenever you need to interpret a date a person typed — especially ambiguous numeric dates like 03/04/2025, which mean different things in the UK (day-first) vs US (month-first) — before storing, scheduling, or acting on it. Pass locale 'en-GB' or 'en-US'. Returns valid:false for impossible dates.",
  { input: z.string(), locale: z.string().default("en-GB") },
  async ({ input, locale }) => json(parseDate(input, locale)),
);

server.tool(
  "validate_phone",
  "Validate a phone number and normalise it to E.164 (e.g. +442079460958). USE THIS before saving a phone number, dialling, or sending an SMS, instead of trusting raw input. Pass region 'GB' or 'US'. Returns valid:false if the number is not real for that region.",
  { number: z.string(), region: z.string().default("GB") },
  async ({ number, region }) => json(validatePhone(number, region)),
);

server.tool(
  "format_currency",
  "Format a money amount the way a reader in a given locale expects (symbol position, decimal/thousands separators). USE THIS whenever you show a price/total to a user or put one in an email, invoice, or report. e.g. 1234.5 GBP en-GB -> '£1,234.50'.",
  { amount: z.number(), currency: z.string().default("GBP"), locale: z.string().optional() },
  async ({ amount, currency, locale }) => json(formatMoney(amount, currency, locale)),
);

server.tool(
  "tax_rate",
  "Look up the correct consumption-tax rate. USE THIS before calculating VAT or sales tax on an invoice or quote — never recall the rate from memory, it is DATE-SENSITIVE. GB returns the UK standard VAT rate that applied on the given date (handles historical/temporary changes). US has no national VAT (returns 0); pass a state code like 'CA' for the state base sales-tax rate. Always pass the invoice date for GB.",
  { country: z.string().default("GB"), date: z.string().optional(), state: z.string().optional() },
  async ({ country, date, state }) => json(vatRate(country, date, state)),
);

server.tool(
  "is_holiday",
  "Check whether a date (YYYY-MM-DD) is a public/bank holiday. USE THIS when computing business-day deadlines, delivery SLAs, or 'next working day'. GB defaults to England; pass subdiv 'SCT'/'WLS'/'NIR' or a US state code. Country is GB or US.",
  { date: z.string(), country: z.string().default("GB"), subdiv: z.string().optional() },
  async ({ date, country, subdiv }) => json(isHoliday(date, country, subdiv)),
);

server.tool(
  "next_holiday",
  "Find the next public/bank holiday on or after a date (default today). USE THIS to answer 'when is the next holiday' or find the next working day. Country is GB or US; subdiv narrows to a UK nation or US state.",
  { country: z.string().default("GB"), after: z.string().optional(), subdiv: z.string().optional() },
  async ({ country, after, subdiv }) => json(nextHoliday(country, after, subdiv)),
);

server.tool(
  "parse_address",
  "Extract structured {country, postcode, city} from a free-text UK or US address. USE THIS when onboarding a user, running a KYC/fraud check, or storing an address, instead of splitting the string yourself. Returns a confidence flag.",
  { input: z.string() },
  async ({ input }) => json(parseAddress(input)),
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("localecheck MCP server failed:", err);
  process.exit(1);
});
