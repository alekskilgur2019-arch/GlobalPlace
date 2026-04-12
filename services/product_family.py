import re


GENERIC_TOKENS = {
    "the",
    "for",
    "and",
    "with",
    "apple",
    "model",
    "edition",
}


def _normalize_name(name):
    normalized = str(name or "").strip().lower()
    normalized = re.sub(r"[.\-_/]+", " ", normalized)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _is_noise_token(token):
    if not token or token in GENERIC_TOKENS:
        return True
    if token.isdigit():
        numeric_value = int(token)
        if 2000 <= numeric_value <= 2099:
            return True
        if numeric_value in {11, 12, 13, 14, 15, 16}:
            return True
    return False


def _get_family_tokens(name):
    normalized = _normalize_name(name)
    if not normalized:
        return []

    tokens = []
    for token in normalized.split():
        if _is_noise_token(token):
            continue
        tokens.append(token)

    return tokens[:4]


def derive_family_key(name):
    family_tokens = _get_family_tokens(name)
    if not family_tokens:
        fallback = _normalize_name(name)
        return fallback.replace(" ", "-") if fallback else ""
    return "-".join(family_tokens)


def derive_display_name(name):
    family_tokens = _get_family_tokens(name)
    if not family_tokens:
        return str(name or "").strip()

    display_tokens = []
    for token in family_tokens:
        if token in {"m1", "m2", "m3", "ps5", "x1"}:
            display_tokens.append(token.upper())
        elif any(char.isdigit() for char in token) and any(char.isalpha() for char in token):
            display_tokens.append(token.upper())
        else:
            display_tokens.append(token.capitalize())
    return " ".join(display_tokens)
