import re


SEARCH_STOPWORDS = {"the", "for", "and", "with"}
CANONICAL_REPLACEMENTS = (
    (r"\bmac\s+book\b", "macbook"),
)


def get_original_query_for_display(query):
    return str(query or "").strip()


def normalize_search_text(text):
    normalized = get_original_query_for_display(text).lower()
    if not normalized:
        return ""

    normalized = re.sub(r"[.\-_/]+", " ", normalized)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    for pattern, replacement in CANONICAL_REPLACEMENTS:
        normalized = re.sub(pattern, replacement, normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def normalize(text):
    return normalize_search_text(text)


def tokenize(text, apply_stopword_filter=False):
    normalized = normalize(text)
    if not normalized:
        return []

    tokens = [token for token in normalized.split(" ") if token]
    if not apply_stopword_filter or len(tokens) <= 1:
        return tokens

    filtered_tokens = [token for token in tokens if token not in SEARCH_STOPWORDS]
    return filtered_tokens or tokens


def is_exact_match(query, candidate):
    normalized_query = normalize(query)
    normalized_candidate = normalize(candidate)
    if not normalized_query or not normalized_candidate:
        return False
    return normalized_query == normalized_candidate


def is_prefix_token_match(query, candidate):
    query_tokens = tokenize(query, apply_stopword_filter=True)
    candidate_tokens = tokenize(candidate)
    if not query_tokens or not candidate_tokens:
        return False
    if len(query_tokens) > len(candidate_tokens):
        return False

    if len(query_tokens) == 1:
        return len(query_tokens[0]) >= 4 and candidate_tokens[0] == query_tokens[0]

    return candidate_tokens[: len(query_tokens)] == query_tokens
