import re

PHONE_RE = re.compile(r"^[0-9+\-\s]{7,20}$")


def is_valid_phone(value):
    if not value:
        return True  # optional field
    return bool(PHONE_RE.match(value))


def is_strong_enough_password(value):
    return len(value or "") >= 6
