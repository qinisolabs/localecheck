"""localecheck — a locale-correctness API for AI agents (UK + USA v1).

Wraps authoritative libraries (phonenumbers, babel/CLDR, python-holidays,
dateutil) plus hand-curated tax data so agents get international "boring data"
right instead of hallucinating it.
"""
__version__ = "0.1.0"
SUPPORTED_COUNTRIES = ["GB", "US"]
