# Use localecheck in your AI app

localecheck is a free, no-API-key MCP server. Once connected, your AI assistant
can call it automatically to get verified dates, phone numbers, currency
formatting, tax rates, holidays, and addresses (UK + USA).

`uvx` runs it straight from PyPI with **no manual install** — you don't need to
clone anything or manage Python. (`uvx` ships with [uv](https://docs.astral.sh/uv/).)

## Claude Desktop / Claude Code

Add this to your MCP config (Settings → Developer → Edit Config, or
`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "localecheck": {
      "command": "uvx",
      "args": ["--from", "localecheck", "localecheck-mcp"]
    }
  }
}
```

Restart the app. You'll see a `localecheck` tool group appear.

## Cursor

`~/.cursor/mcp.json` (or Settings → MCP → Add):

```json
{
  "mcpServers": {
    "localecheck": {
      "command": "uvx",
      "args": ["--from", "localecheck", "localecheck-mcp"]
    }
  }
}
```

## Cline / Continue / other MCP clients

Same shape — point the client at the `uvx` command above. Any MCP-compatible
client works the same way.

## Prefer Python already installed?

```bash
pip install "localecheck[mcp]"
# then use command "localecheck-mcp" with empty args in the config above
```

## Try it

After connecting, just ask your assistant naturally — it will pick the tool on
its own:

- "An invoice is dated 1 June 2009 in the UK — what VAT rate applies?" → 15%
- "Is 21 April 2025 a working day in England?" → no, Easter Monday
- "Format 1234.5 as GBP for a UK customer." → £1,234.50
- "Normalise this phone number: 020 7946 0958." → +442079460958
- "My user typed 03/04/2025 and they're in London — what date is that?" → 3 April 2025

## Not using an MCP app? Call the REST API

If you've deployed the hosted API (or run `uvicorn app:app` locally), any agent
or script can hit plain HTTP — no MCP needed:

```
GET /v1/tax/rate?country=GB&date=2009-06-01   ->  {"rate": 15.0, ...}
```

Interactive docs are at `/docs`.
