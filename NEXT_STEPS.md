# localecheck — status & next steps

Snapshot of what's shipped and what's left, so work can resume any time.

## ✅ Done

- **npm:** `localecheck@0.1.1` published (unscoped, public), with `mcpName`.
- **GitHub:** public repo `github.com/qinisolabs/localecheck` under the Qiniso org;
  brand set (logo, name, description, site URL).
- **Official MCP Registry:** listed and active as `io.github.qinisolabs/localecheck`.
- **Website:** benchmark/landing page live at `qinisolabs.github.io/localecheck`
  (logo + favicon + `llms.txt`).
- **Verified working:** runs in Claude Desktop; called live by an AI agent.
- **Tests/quality:** 34 parity tests passing; code-reviewed; docs scrubbed + accurate.

## ⏳ Pending (mostly passive — just check back)

- **Glama listing:** submitted; it auto-indexes the public repo. Once it shows a score,
  add the badge to the awesome-mcp-servers PR:
  `[![…](https://glama.ai/mcp/servers/qinisolabs/localecheck/badges/score.svg)](https://glama.ai/mcp/servers/qinisolabs/localecheck)`
- **awesome-mcp-servers PR:** open; merge is gated on the Glama badge above.
- **Confirm latest commit pushed:** make sure the logo, favicon, and doc-accuracy fixes
  are committed/pushed (`git status` should be clean).

## 🎯 Next moves (active — when you want growth)

Priority order:

1. **Real benchmark numbers.** Run the eval (`eval/`) against a real model (needs an
   ANTHROPIC_API_KEY or OPENAI_API_KEY) to replace the illustrative figures on the
   benchmark page with real ones. Highest-value because it powers the launch.
2. **Launch post.** Show HN + r/mcp / r/ClaudeAI + an MCP Discord, led with the real
   benchmark finding (not a pitch). Use brand accounts. This is the active push that
   drives first users/stars/downloads.
3. **Deepen the tax data (the moat).** Currently UK VAT (by date) + US state sales tax.
   Add more countries (e.g. EU members, CA, AU) — this is the defensible asset and the
   path toward a paid tier.
4. **mcp.so submission** (optional; low effort, more reach).
5. **PyPI** (optional). The Python package exists in the repo but is legacy/unmaintained;
   only publish if there's demand for a pip install path. We're TS-first.

## 🛠️ Optional polish (from the code review — safe to defer to 0.1.x)

- Memoize `date-holidays` instances per (country, subdiv) if it ever becomes a hot path.
- Tighten the written-date fallback in `dates.ts` (`new Date(...)` is lenient; e.g.
  `"2025"` parses to Jan 1) or document the edge.
- `holidays.ts`: if an invalid `subdiv` is passed it silently falls back to country-level
  but still echoes the requested subdiv — minor transparency fix.
- `tax_rate` (US) accepts a `date` but ignores it (rates are current-only) — documented,
  but could be made explicit.

## 🔁 Ongoing maintenance

- **Tax data** changes over time (VAT rate changes, new US state rates). Refresh the JSON
  in `packages/localecheck-python/localecheck/data/` (and the TS copy in
  `packages/localecheck-ts/data/`) and bump `last_verified`. This is the real upkeep.
- **Holiday library:** occasionally `npm update date-holidays` to pick up new one-off /
  legislated holidays, then republish.
- Keep the two `data/` copies in sync (TS + Python) until/unless Python is retired.

## 💰 Later (monetization phase — only if adoption shows up)

Open-core: keep the code + commodity wrappers free; charge for the maintained,
multi-country/historical tax data via a hosted, metered API (build it in TS — Hono /
Cloudflare Workers). Free tier + paid tier + SLA. See `BUSINESS_MODEL.md`.

## To resume quickly

1. `cd` into the repo, `git pull`, `git status` (confirm clean).
2. Re-read this file + `BUSINESS_MODEL.md`.
3. Pick the top unchecked item under "Next moves."
4. For any code change: edit `src/`, `npm run build`, `npm test` (34 should pass), bump
   the version, `npm publish`, commit + push, and update `server.json` version if the
   package version changed.
