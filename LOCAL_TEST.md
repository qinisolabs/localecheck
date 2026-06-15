# Test localecheck locally (before any GitHub / npm / PyPI publish)

You can fully exercise both packages on your own machine — including using the
MCP server inside Claude Desktop or Cursor — **without publishing anything**.
Replace `/ABS/PATH` below with the real path to each folder on your computer.

---

## A. TypeScript package (`locale-api-ts/`)

### 1. Build + automated tests

```bash
cd /ABS/PATH/locale-api-ts
npm install
npm test            # expect: 34 passed, 0 failed
npm run build       # compiles to dist/
```

### 2. Try the MCP server inside a real AI app (local build, no publish)

Add this to your MCP config, pointing at your **local** compiled server:

**Claude Desktop** — `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "localecheck": {
      "command": "node",
      "args": ["/ABS/PATH/locale-api-ts/dist/server.js"]
    }
  }
}
```

**Cursor** — `~/.cursor/mcp.json`: same block.

Restart the app. You should see the `localecheck` tools appear. Then ask:

- "A UK invoice is dated 1 June 2009 — what VAT rate applies?" → 15%
- "Is 25 August 2025 a working day in England?" → no (Summer bank holiday)
- "My user in London typed 03/04/2025 — what date is that?" → 3 April 2025

### 3. Verify it as a library (how a code-writing agent uses it)

```bash
cd /ABS/PATH/locale-api-ts
node --input-type=module -e '
import { vatRate, parseDate, formatMoney } from "./dist/index.js";
console.log(vatRate("GB","2009-06-01").rate);          // 15
console.log(parseDate("03/04/2025","en-GB").iso);      // 2025-04-03
console.log(formatMoney(1234.5,"GBP","en-GB").formatted); // £1,234.50
'
```

### 4. (Optional) Test the exact published artifact before going live

```bash
npm pack                         # creates localecheck-0.1.0.tgz
npx ./localecheck-0.1.0.tgz      # runs the server exactly as users would via npx
```

---

## B. Python package (`locale-api/`)

### 1. Automated tests

```bash
cd /ABS/PATH/locale-api
pip install -r requirements.txt
pytest -q           # expect: 27 passed
```

### 2. REST API

```bash
uvicorn app:app --reload
# in another terminal:
curl "http://127.0.0.1:8000/v1/tax/rate?country=GB&date=2009-06-01"
# open http://127.0.0.1:8000/docs for the interactive UI
```

### 3. Python MCP server in a real AI app (local, no publish)

```json
{
  "mcpServers": {
    "localecheck-py": {
      "command": "python3",
      "args": ["/ABS/PATH/locale-api/mcp_server.py"]
    }
  }
}
```

(Run `pip install -r requirements.txt` first so `mcp` is available.)

---

## C. Run the eval (optional — proves the gap is real)

```bash
cd /ABS/PATH/locale-eval
pip install -r requirements.txt
python generate_dataset.py
export ANTHROPIC_API_KEY=sk-...        # or OPENAI_API_KEY
python run_eval.py --provider anthropic
# writes report.md with the per-category error rate
```

---

## What "passing locally" looks like

| Check | Expected |
|---|---|
| `npm test` (TS) | 34 passed, 0 failed |
| TS MCP server in Claude/Cursor | tools appear, answers correct |
| TS library import | 15 / 2025-04-03 / £1,234.50 |
| `pytest` (Python) | 27 passed |
| REST API `/v1/tax/rate` | `{"rate": 15.0, ...}` |

All of these were verified green in a clean sandbox build, so if a step fails on
your machine it's almost certainly an environment issue (Node/Python version,
missing `npm install`/`pip install`), not the code. Node ≥ 18 and Python ≥ 3.9.

Only once you're happy here do you move on to `locale-api/PUBLISH.md`.
