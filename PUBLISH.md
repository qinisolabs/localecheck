# Publishing checklist — get agents able to find & use localecheck

Goal for this phase: **maximum discoverability, zero friction.** Free, no API
key, installable in one line. You ship **two packages from the same project**:

- **npm** (`locale-api-ts/`) — the TypeScript MCP server. **Primary** distribution:
  `npx` is the path most MCP-client apps (Claude Desktop, Cursor, Cline) use.
- **PyPI** (`locale-api/`) — the Python package + REST API. The `pip`/`uvx` path
  and the hosted-API backend.

Do these in order.

## 0. One-time prep

- [x] Name decided and verified free on npm + PyPI: **`localecheck`**.
- [x] Brand / GitHub org created: **`qinisolabs`** (display name "Qiniso").
- [x] Brand wired into all files: repo `qinisolabs/localecheck`, MCP namespace
      `io.github.qinisolabs/localecheck`. (No placeholders left.)
- [ ] Create the repo `localecheck` inside the `qinisolabs` org and push both packages.
- [ ] Create accounts + tokens (see below).

### Accounts & tokens (do before publishing)

**npm**
1. Sign up at https://www.npmjs.com/signup, verify email.
2. Enable 2FA (Account → Two-Factor Authentication) — required for publishing.
3. Publishing from your machine just needs `npm login` (no token). For CI, make a
   token: avatar → Access Tokens → Generate New Token → Granular/Automation.

**PyPI** (token is mandatory — password upload is disabled)
1. Register at https://pypi.org/account/register/, verify email.
2. Enable 2FA (required before any upload).
3. Account settings → API tokens → Add API token → scope **"Entire account"**
   (the project doesn't exist yet). Copy the `pypi-…` token — shown only once.
4. `twine upload` uses username `__token__` and the `pypi-…` token as the password.

Keep tokens in `~/.npmrc` / `~/.pypirc` or paste at the prompt — never in the repo.

## 1. Publish to npm (primary — enables `npx`)

```bash
cd locale-api-ts
npm install
npm test                 # 34 parity tests — must pass
npm run build            # tsc -> dist/   (verified working)
npm login                # or set NPM_TOKEN
npm publish --access public
```

Verify the install path agents will use:

```bash
npx -y localecheck       # should start the MCP server over stdio
```

## 2. Publish to PyPI (enables `pip` / `uvx`)

```bash
cd locale-api
pip install build twine
python -m build          # dist/*.whl + *.tar.gz   (verified working)
twine upload dist/*      # paste your PyPI API token
```

Verify:

```bash
uvx --from localecheck localecheck-mcp   # should start the MCP server
```

## 3. Publish to the official MCP Registry (so MCP clients discover it)

The registry hosts **metadata only**; your package must already be on npm/PyPI.

```bash
# install the official publisher CLI (modelcontextprotocol.io/registry/quickstart)
# authenticate with GitHub, then from the repo root:
mcp-publisher publish        # reads server.json
```

Notes:
- `server.json` `name` must be `io.github.<username>/localecheck`.
- For a Node server you can point the registry entry at the **npm** package; for
  Python, at the **PyPI** package. You can list both packages in `server.json`.
- The Registry API is at v0.1 (frozen Oct 2025) — confirm the current
  `server.json` schema and CLI flags against the quickstart before running.

## 4. List on the other registries (broader reach)

- [ ] **mcp.so** — self-submit (largest directory, ~20k servers).
- [ ] **Smithery** (smithery.ai) — connect the GitHub repo (auto-builds Node servers).
- [ ] **Glama** (glama.ai/mcp) — submit / auto-indexed from GitHub.
- [ ] **awesome-mcp-servers** (punkpeye/awesome-mcp-servers) — open a PR.

## 5. Make it findable by models & web

- [ ] Host `llms.txt` at your domain root; link it from both READMEs.
- [ ] Publish `benchmark.html` on GitHub Pages (free) — the shareable hook.
- [ ] One launch post (Show HN, an MCP Discord, r/mcp) leading with the
      benchmark: "how often AI agents get UK/US data wrong."

## Which package gets listed where (quick reference)

| Channel | Package | Install command |
|---|---|---|
| Claude Desktop / Cursor / Cline | npm | `npx -y localecheck` |
| Python agents / scripts | PyPI | `uvx --from localecheck localecheck-mcp` or `pip install localecheck[mcp]` |
| Official MCP registry | both (via server.json) | client-managed |
| REST consumers | PyPI / hosted | `GET /v1/...` |

## Success signals to watch (adoption-first)

- npm + PyPI download counts trending up.
- Registry listing views / installs; GitHub stars and issues.
- You are NOT optimising for revenue yet — the win is agents installing and
  calling it. Add a paid tier later, under the installed base.
