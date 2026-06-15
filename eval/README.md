# Locale-correctness eval

A throwaway-cheap test of one question: **how often does a raw LLM get "boring"
international data wrong?** If the answer is "often," there's a real gap an
API / MCP server could fill. If it's "almost never," skip the idea — no eval
needed beyond this.

It scores a model across six categories that agents routinely mangle outside
US-English:

| Category | What it tests | Ground truth |
|---|---|---|
| `date_parse` | Ambiguous dates by locale → ISO 8601 | hand-curated |
| `vat_rate` | Standard VAT/GST by **country + date** (incl. temporary changes) | hand-curated |
| `phone` | Validate + normalise to E.164 | libphonenumber |
| `currency_format` | Locale-correct currency string | babel / CLDR |
| `holiday` | Is date X a national holiday in country Y? | python-holidays |
| `address_parse` | Messy international address → country/postcode/city | hand-curated |

The `phone`, `currency_format`, and `holiday` ground truth is generated *from the
very libraries the product would wrap* — so the eval measures how far the LLM
strays from a correct deterministic source. That gap is the product.

## Setup

```bash
pip install -r requirements.txt
python generate_dataset.py        # builds the library-derived test cases
```

## Run

```bash
# No API key — simulated output, just to see the pipeline:
python run_eval.py --provider mock

# Real numbers (set the matching key first):
export ANTHROPIC_API_KEY=sk-...
python run_eval.py --provider anthropic --model claude-sonnet-4-6

export OPENAI_API_KEY=sk-...
python run_eval.py --provider openai --model gpt-4o
```

Outputs `report.md` (human-readable table + sample failures) and `report.json`.

## How to read the result

- **Error rate per category is the signal.** The `--provider mock` run is
  *simulated* to illustrate the pipeline — ignore its numbers. Only a real
  provider run tells you anything.
- **Kill threshold = 15%.** Categories below it, the LLM already handles well —
  drop them from any MVP. Categories well above it are your wedge.
- **`vat_rate` is the one to watch.** The date-sensitive cases (temporary COVID
  rates, historical rates) are where being wrong is expensive, so willingness to
  pay is highest. If a frontier model nails current rates but fails the dated
  ones, that's the most defensible slice of the product.
- The failed-case list in `report.md` doubles as marketing: "frontier models get
  international VAT-by-date wrong N% of the time" is a publishable benchmark and a
  landing-page hook.

## Decision gates (decide before you build)

1. Real-provider overall error rate **< 5%** across the top categories → no
   problem to solve. Stop.
2. One or two categories **> 20%** → you have a wedge. Build *those only* as a
   first MCP server, publish the benchmark, collect signups.
3. The high-error categories are dominated by `vat_rate` / `address_parse`
   (the hand-curated, data-maintenance-heavy ones) → the moat is maintenance,
   not cleverness. Only proceed if maintaining that data for years sounds fine.

## Extending

- Add cases by dropping JSON into `data/` (match the existing shape) or editing
  `generate_dataset.py`. Aim for ~30–50 cases/category before trusting a rate.
- Add a provider by implementing a `generate(category, case)` method in
  `run_eval.py` (see `AnthropicProvider`).
- Run the same eval against 2–3 models to see if this is a "models will fix it
  soon" problem or a persistent one. If the newest model is as wrong as the
  oldest, the gap is durable and the business is more defensible.

## Caveats

- Hand-curated ground truth (VAT, addresses, dates) is best-effort from public
  records — spot-check edge cases before quoting them publicly.
- `python-holidays` covers *national* holidays; regional/bank-holiday nuance
  varies. Treat `holiday` as indicative.
- This measures correctness, not latency or cost — separate questions if you
  productise.
