# localecheck — business model & go-to-market plan

## TL;DR recommendation

**Open-core.** Open-source the code and the commodity functions (Apache-2.0) to
win recognition, GitHub stars, and registry installs. Keep the *maintained,
multi-country, date-sensitive tax data* behind a hosted, metered API as the paid
product. Give away the wrappers; charge for the data and the reliability.

This is not a guess — it is the model a direct competitor (vatnode) is already
running successfully (free offline VAT data via MCP, paid API key for live
validation). The market has validated the shape; the question is execution and
differentiation.

## Competitive reality (verified June 2026 — read this first)

The "nobody has built this" assumption is **only half true now**. VAT-for-agents
specifically has several players:

- **vatnode-mcp** — official MCP server, free offline VAT rates + format checks
  for 45 European countries, paid API key for live VIES validation. Freemium /
  open-core, exactly the model below.
- **EU VAT Rates MCP server** (businesspress.io) — current rates for all 27 EU
  states (standard/reduced/super-reduced/parking).
- **vat-validator-mcp** — EU VIES, UK HMRC, Australian ABN number validation.
- **MCP Europe Business Suite** — the closest to *our* broad pitch: deterministic
  validation + reference data (VAT rates, payment terms, e-invoicing, holiday
  calendars) as a "first-line compliance layer."
- **Avalara** — the incumbent, now shipping "agentic tax and compliance."

What this means: **VAT-rate-lookup alone is now commodity and getting crowded.**
A bare "current EU VAT rates" MCP is not a business. The defensible angles that
remain:

1. **Breadth, not a single field.** One tool that covers dates + phone + currency
   + holidays + addresses + tax together is less crowded than VAT alone. MCP
   Europe Business Suite is the only close bundle competitor.
2. **Date-sensitive / historical accuracy.** Most VAT tools return *today's*
   rate. The ability to answer "what was the rate on 2009-06-01" (historical and
   temporary changes) is rarer and is exactly where being wrong is expensive.
3. **Geography beyond the EU.** The field is EU-saturated. UK-first then US,
   Canada, Australia, LatAm is less contested.
4. **Correctness contract + provenance.** `last_verified` dates, source citations,
   confidence flags, and a public accuracy benchmark — trust as the product.

Honest take: differentiate on breadth + non-EU + historical, or don't enter the
VAT lane and instead own the *non-tax* locale bundle (dates/phone/currency/
holidays/address) where there is almost no competition, using tax as a feature
rather than the headline.

## The open-core split

| Layer | Open source (Apache-2.0) | Hosted / paid |
|---|---|---|
| MCP server + REST code | ✅ | — |
| Wrappers: phone, currency, dates, holidays, address | ✅ (libraries are free anyway) | — |
| Tax data: small SAMPLE (UK + a few US states) | ✅ in repo | — |
| Tax data: full, maintained, multi-country, historical | ❌ | ✅ metered API |
| Freshness guarantees, SLA, support, audit log | — | ✅ |

The open repo ships a *limited sample* of the tax data so the tool works and is
demoable. The full, continuously-maintained dataset lives server-side and is
reached through an API key. Maintenance is the moat: the data degrades the moment
you stop updating it, which is precisely why competitors won't casually copy it.

## Why open-core (vs the alternatives)

- **Pure open-source:** great for recognition, zero revenue, and anyone can host
  your work. You become a maintainer, not a business.
- **Pure closed/hosted SaaS:** hard to get discovered; agent developers prefer
  inspectable, self-hostable tools; registries and communities favour open. You
  fight uphill on distribution.
- **Open-core:** open repo is the *funnel* (stars, registry installs, trust);
  hosted API with maintained data is the *product*. Distribution and monetisation
  both work. This is the standard winning pattern for dev infrastructure.

## Hosting

Start cheap and serverless; the workload is small, stateless, read-heavy and
cacheable.

- **Compute:** Fly.io / Railway / Render for a container, or Cloudflare Workers /
  Vercel / AWS Lambda for serverless. Any is fine at low volume.
- **Edge cache** in front (Cloudflare): tax/holiday lookups are highly cacheable,
  which keeps costs near zero and latency low.
- **API gateway** for API-key auth, per-key rate limiting, and usage metering
  (roll your own, or use an API-management layer / a billing provider like Stripe
  metered billing or an API-monetisation service).
- **Data store:** the curated data is small — versioned JSON/SQLite in the repo
  for sample, a managed Postgres or just versioned files for the full set.

## Monetisation

- **Free tier:** commodity functions (phone/currency/dates/holidays/address) +
  sample tax data, with a generous-but-capped rate limit. This is the adoption
  engine; keep it genuinely useful.
- **Paid (usage-based):** full multi-country + historical tax data, higher rate
  limits, freshness SLA, audit metadata. Price per call (e.g. fractions of a
  cent) or tiered monthly plans. A few hundred paying teams at $100–1,000/mo is a
  real solo-dev business; that is the realistic ceiling and it is fine.
- **Optional enterprise:** self-host the full dataset under a commercial licence,
  SLA + support contract.

## 90-day plan

1. **Decide the lane** (week 1): broad locale bundle with tax as a feature
   (recommended, low competition) vs head-on VAT (crowded, needs strong
   historical/geo differentiation).
2. **Ship open source** (weeks 1–2): public GitHub repo (Apache-2.0), publish to
   PyPI, run the `mcp-publisher` flow to list on the official MCP registry, and
   self-submit to mcp.so, Smithery, Glama, and the awesome-mcp-servers list.
3. **Publish the benchmark** (week 2): the "how often do agents get international
   data wrong" page from the `locale-eval` project. This is the marketing hook —
   post it to HN, dev communities, and the MCP Discords.
4. **Stand up the hosted API** (weeks 3–6): API-key auth, metering, edge cache,
   free + paid tiers, a landing page with a "get a key" form.
5. **Expand the moat data** (weeks 4–12): add countries/historical depth where
   competitors are thin (UK done; US in progress; then CA/AU and EU historical).
6. **Measure demand:** track installs, key signups, and which endpoints get
   called. Let usage tell you which data to deepen.

## Kill / pivot signals

- If the free tool gets installs but nobody upgrades, the data isn't painful
  enough to pay for → pivot to the highest-pain vertical (e-invoicing/tax) or stay
  open-source as a portfolio/reputation asset.
- If VAT competitors expand into your geography/historical niche faster than you
  can, retreat to the non-tax locale bundle where you're less contested.
- If a frontier model release closes the accuracy gap on your top categories
  (re-run the benchmark each model launch), the wedge is shrinking — lean harder
  on freshness/SLA/provenance, which models can't provide.
