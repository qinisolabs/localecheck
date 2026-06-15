"""Phone validation + E.164 normalisation via libphonenumber."""
import phonenumbers
from phonenumbers import PhoneNumberFormat, NumberParseException, number_type
from phonenumbers.phonenumberutil import PhoneNumberType

_TYPE_NAMES = {
    PhoneNumberType.MOBILE: "mobile",
    PhoneNumberType.FIXED_LINE: "fixed_line",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed_line_or_mobile",
    PhoneNumberType.TOLL_FREE: "toll_free",
    PhoneNumberType.PREMIUM_RATE: "premium_rate",
    PhoneNumberType.VOIP: "voip",
}


def validate_phone(number: str, region: str = "GB") -> dict:
    """Validate a phone number and normalise to E.164.

    Returns {"valid": bool, "e164": ..., "national": ..., "type": ...}.
    """
    region = (region or "GB").upper()
    try:
        parsed = phonenumbers.parse(str(number), region)
    except NumberParseException as e:
        return {"valid": False, "reason": str(e), "input": number, "region": region}
    valid = phonenumbers.is_valid_number(parsed)
    if not valid:
        return {"valid": False, "reason": "not a valid number for region",
                "input": number, "region": region}
    return {
        "valid": True,
        "e164": phonenumbers.format_number(parsed, PhoneNumberFormat.E164),
        "national": phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL),
        "international": phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL),
        "type": _TYPE_NAMES.get(number_type(parsed), "unknown"),
        "region": region,
        "input": number,
    }
