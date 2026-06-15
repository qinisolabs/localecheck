"""
Locale-correctness eval for LLM agents.

Measures how often a raw LLM gets international "boring data" wrong:
dates, phone numbers, currency formatting, VAT-by-date, addresses, holidays.

Usage:
    python run_eval.py --provider mock                      # no API key, simulated
    python run_eval.py --provider anthropic --model claude-sonnet-4-6
    python run_eval.py --provider openai --model gpt-4o

Set ANTHROPIC_API_KEY or OPENAI_API_KEY for real runs.
Outputs: report.md and report.json in this folder, plus a console summary.

The hypothesis being tested: if the per-category error rate is high (say >15%),
there is a real correctness gap an API/MCP server could fill. If it's near zero,
the LLM already handles it and that category is not worth building.
"""
import argparse
import glob
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

KILL_THRESHOLD = 15.0  # % error rate below which a category is "not worth building"


# ---------- normalisation & scoring ----------

def norm_space(s):
    if s is None:
        return ""
    s = str(s)
    # collapse all unicode spaces (incl. NBSP / narrow NBSP) to single space
    s = s.replace(" ", " ").replace(" ", " ")
    s = unicodedata.normalize("NFC", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_basic(s):
    return norm_space(s).upper()


def score_case(category, case, answer):
    """Return (is_correct: bool, detail: str)."""
    exp = case.get("expected")
    if category == "vat_rate":
        try:
            a = float(re.sub(r"[^0-9.]", "", str(answer)))
            e = float(exp)
            return abs(a - e) < 0.001, f"got {a} want {e}"
        except (ValueError, TypeError):
            return False, f"unparseable: {answer!r}"
    if category == "currency_format":
        return norm_space(answer) == norm_space(exp), f"got {answer!r} want {exp!r}"
    if category == "address_parse":
        fields = case.get("expected", {})
        ok = True
        diffs = []
        if not isinstance(answer, dict):
            return False, f"non-dict answer: {answer!r}"
        for k, v in fields.items():
            got = answer.get(k)
            match = norm_basic(got) == norm_basic(v)
            ok = ok and match
            if not match:
                diffs.append(f"{k}: got {got!r} want {v!r}")
        return ok, "; ".join(diffs) if diffs else "all fields ok"
    # date_parse, phone, holiday -> exact normalised string
    return norm_basic(answer) == norm_basic(exp), f"got {answer!r} want {exp!r}"


# ---------- prompts ----------

def build_prompt(category, case):
    if category == "date_parse":
        return (
            f"Parse this date written in locale '{case['locale']}': \"{case['input']}\".\n"
            "Return ISO 8601 (YYYY-MM-DD). If the date is impossible/invalid, return \"INVALID\".\n"
            "Respect the locale's day/month ordering. Respond ONLY as JSON: {\"answer\": \"...\"}"
        )
    if category == "vat_rate":
        return (
            f"What was the STANDARD VAT/GST rate (percent) in country '{case['country']}' "
            f"on date {case['date']}? If the country has no national VAT, answer 0.\n"
            "Give the number only (e.g. 20 or 8.1). Respond ONLY as JSON: {\"answer\": \"...\"}"
        )
    if category == "phone":
        return (
            f"Validate and normalise this phone number to E.164 format. "
            f"Region hint: '{case['region']}'. Number: \"{case['input']}\".\n"
            "If it is not a valid number, return \"INVALID\".\n"
            "Respond ONLY as JSON: {\"answer\": \"+...\"}"
        )
    if category == "currency_format":
        return (
            f"Format the amount {case['amount']} in currency {case['currency']} "
            f"for locale '{case['locale']}', exactly as it should be displayed to a user "
            "(correct symbol, position, decimal and grouping separators).\n"
            "Respond ONLY as JSON: {\"answer\": \"...\"}"
        )
    if category == "holiday":
        return (
            f"Is {case['date']} a national public holiday in country '{case['country']}'? "
            "Answer YES or NO.\nRespond ONLY as JSON: {\"answer\": \"YES\" or \"NO\"}"
        )
    if category == "address_parse":
        return (
            f"Parse this address into structured fields. Address: \"{case['input']}\".\n"
            "Return country as ISO-2 code, plus postcode and city.\n"
            "Respond ONLY as JSON: {\"country\": \"..\", \"postcode\": \"..\", \"city\": \"..\"}"
        )
    raise ValueError(category)


def parse_answer(category, raw_text):
    """Extract the answer from the model's JSON-ish reply."""
    m = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not m:
        return raw_text.strip()
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return raw_text.strip()
    if category == "address_parse":
        return obj
    return obj.get("answer", obj)


# ---------- providers ----------

class MockProvider:
    """Simulates a plausible LLM with the systematic locale weaknesses the
    proposed product targets. Output is illustrative, NOT real model data."""
    name = "mock (SIMULATED)"

    # current VAT rates the mock 'knows', ignoring historical dates
    CURRENT_VAT = {"GB": "20", "DE": "19", "IE": "23", "FR": "20", "NL": "21",
                   "ES": "21", "IT": "22", "CH": "8.1", "JP": "10", "AU": "10",
                   "US": "0", "NO": "25", "SE": "25"}

    def generate(self, category, case):
        if category == "date_parse":
            # weakness: always assumes US MM/DD for slash dates, never says INVALID
            return json.dumps({"answer": self._mock_date(case)})
        if category == "vat_rate":
            # weakness: returns today's rate, ignoring the date
            return json.dumps({"answer": self.CURRENT_VAT.get(case["country"], "20")})
        if category == "currency_format":
            # weakness: US-style formatting regardless of locale
            sym = {"EUR": "€", "GBP": "£", "USD": "$", "JPY": "¥", "CHF": "CHF ",
                   "BRL": "R$", "INR": "₹", "SEK": "kr", "NOK": "kr",
                   "AUD": "$", "CAD": "$"}.get(case["currency"], "")
            amt = f"{case['amount']:,.2f}"
            return json.dumps({"answer": f"{sym}{amt}"})
        if category == "phone":
            return json.dumps({"answer": self._mock_phone(case)})
        if category == "holiday":
            # weakness: over-calls holidays it has seen globally
            globally_famous = {"2025-12-26", "2025-07-04", "2025-12-25"}
            ans = "YES" if (case["expected"] == "YES" or case["date"] in globally_famous) else "NO"
            return json.dumps({"answer": ans})
        if category == "address_parse":
            return json.dumps(self._mock_address(case))
        return "{}"

    def _mock_date(self, case):
        s = case["input"]
        m = re.match(r"^(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})$", s)
        if m:
            a, b, y = m.groups()
            # US assumption: first field = month
            return f"{y}-{int(a):02d}-{int(b):02d}"
        # fall back to correct answer for written/kanji forms it 'gets'
        return case["expected"] if case["expected"] != "INVALID" else "2025-01-01"

    def _mock_phone(self, case):
        exp = case["expected"]
        # weakness: fails to reject some invalid numbers, passes valid ones
        if exp == "INVALID":
            return "+440000000000" if "GB" in case["region"] else "INVALID"
        return exp

    def _mock_address(self, case):
        exp = dict(case["expected"])
        # weakness: garbles postcode/city for non-Latin / unusual formats
        if case["id"] in ("addr-jp-1", "addr-br-1", "addr-in-1", "addr-nl-1"):
            exp["postcode"] = "00000"
        return exp


class AnthropicProvider:
    def __init__(self, model):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = model
        self.name = f"anthropic:{model}"

    def generate(self, category, case):
        prompt = build_prompt(category, case)
        msg = self.client.messages.create(
            model=self.model, max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text


class OpenAIProvider:
    def __init__(self, model):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model
        self.name = f"openai:{model}"

    def generate(self, category, case):
        prompt = build_prompt(category, case)
        resp = self.client.chat.completions.create(
            model=self.model, max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content


def get_provider(name, model):
    if name == "mock":
        return MockProvider()
    if name == "anthropic":
        return AnthropicProvider(model or "claude-sonnet-4-6")
    if name == "openai":
        return OpenAIProvider(model or "gpt-4o")
    sys.exit(f"unknown provider {name}")


# ---------- driver ----------

def load_cases():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))
    if not files:
        sys.exit("No data files. Run: python generate_dataset.py")
    buckets = {}
    for f in files:
        with open(f, encoding="utf-8") as fh:
            payload = json.load(fh)
        cat = payload["category"]
        buckets.setdefault(cat, []).extend(payload["cases"])
    return buckets


def run(provider, buckets):
    results = {}
    failures = []
    for cat, cases in buckets.items():
        correct = 0
        for case in cases:
            try:
                if isinstance(provider, MockProvider):
                    raw = provider.generate(cat, case)
                else:
                    raw = provider.generate(cat, case)
                answer = parse_answer(cat, raw)
                ok, detail = score_case(cat, case, answer)
            except Exception as e:
                ok, detail = False, f"ERROR: {e}"
            if ok:
                correct += 1
            else:
                failures.append({"category": cat, "id": case.get("id"), "detail": detail})
        total = len(cases)
        err = 100.0 * (total - correct) / total if total else 0.0
        results[cat] = {"total": total, "correct": correct,
                        "error_rate": round(err, 1)}
    return results, failures


def write_reports(provider_name, results, failures):
    overall_total = sum(r["total"] for r in results.values())
    overall_correct = sum(r["correct"] for r in results.values())
    overall_err = round(100.0 * (overall_total - overall_correct) / overall_total, 1)

    report = {"provider": provider_name, "overall_error_rate": overall_err,
              "overall_total": overall_total, "categories": results,
              "failures": failures}
    with open(os.path.join(HERE, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    lines = [f"# Locale-correctness eval report",
             "", f"**Provider:** {provider_name}  ",
             f"**Overall error rate:** {overall_err}%  ({overall_total} cases)  ",
             f"**Kill threshold:** {KILL_THRESHOLD}% (categories below this are not worth building)",
             "", "## Error rate by category", "",
             "| Category | Cases | Errors | Error rate | Worth building? |",
             "|---|---|---|---|---|"]
    for cat, r in sorted(results.items(), key=lambda kv: -kv[1]["error_rate"]):
        verdict = "✅ yes" if r["error_rate"] >= KILL_THRESHOLD else "—  skip"
        errs = r["total"] - r["correct"]
        lines.append(f"| {cat} | {r['total']} | {errs} | {r['error_rate']}% | {verdict} |")
    lines += ["", "## Sample failures", ""]
    for fl in failures[:40]:
        lines.append(f"- `{fl['category']}` **{fl['id']}** — {fl['detail']}")
    if not failures:
        lines.append("_No failures._")
    with open(os.path.join(HERE, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return overall_err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="mock",
                    choices=["mock", "anthropic", "openai"])
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    provider = get_provider(args.provider, args.model)
    buckets = load_cases()
    results, failures = run(provider, buckets)
    overall = write_reports(provider.name, results, failures)

    print(f"\nProvider: {provider.name}")
    print(f"{'category':<18}{'cases':>7}{'errors':>8}{'error%':>9}")
    print("-" * 42)
    for cat, r in sorted(results.items(), key=lambda kv: -kv[1]["error_rate"]):
        print(f"{cat:<18}{r['total']:>7}{r['total']-r['correct']:>8}{r['error_rate']:>8}%")
    print("-" * 42)
    print(f"{'OVERALL':<18}{'':>7}{'':>8}{overall:>8}%")
    print(f"\nWrote report.md and report.json")
    if provider.name.startswith("mock"):
        print("\nNOTE: mock output is SIMULATED to illustrate the pipeline.")
        print("Run with --provider anthropic or --provider openai for real numbers.")


if __name__ == "__main__":
    main()
