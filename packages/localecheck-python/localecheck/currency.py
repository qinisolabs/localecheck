"""Locale-correct currency formatting via babel / CLDR."""
from babel.numbers import format_currency as _fmt, UnknownCurrencyError

# sensible defaults for the v1 supported locales
_DEFAULT_LOCALE = {"GBP": "en_GB", "USD": "en_US"}


def format_money(amount: float, currency: str = "GBP", locale: str = None) -> dict:
    """Format a numeric amount as a locale-correct currency string.

    e.g. (1234.5, 'GBP', 'en-GB') -> '£1,234.50'
         (1234.5, 'USD', 'en-US') -> '$1,234.50'
    """
    currency = (currency or "GBP").upper()
    if not locale:
        locale = _DEFAULT_LOCALE.get(currency, "en_US")
    babel_locale = locale.replace("-", "_")
    try:
        formatted = _fmt(amount, currency, locale=babel_locale)
    except (UnknownCurrencyError, Exception) as e:
        return {"ok": False, "reason": str(e), "amount": amount,
                "currency": currency, "locale": locale}
    return {"ok": True, "formatted": formatted, "amount": amount,
            "currency": currency, "locale": locale}
