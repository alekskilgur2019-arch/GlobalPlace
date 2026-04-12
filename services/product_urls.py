import re
from urllib.parse import urlparse
import hashlib


PLACEHOLDER_DOMAINS = {
    "example.com",
    "qa.globalplace.local",
}

SEARCH_URL_MARKERS = (
    "/sch/",
    "/search",
    "?_nkw=",
    "&_nkw=",
    "?keyword=",
    "&keyword=",
    "?q=",
    "&q=",
    "?k=",
    "&k=",
    "/s?",
)

def is_placeholder_product_url(url):
    normalized_url = str(url or "").strip().lower()
    if not normalized_url:
        return True

    return any(domain in normalized_url for domain in PLACEHOLDER_DOMAINS) or "/mock/" in normalized_url


def is_search_results_url(url):
    normalized_url = str(url or "").strip().lower()
    if not normalized_url:
        return False
    return any(marker in normalized_url for marker in SEARCH_URL_MARKERS)


def _legacy_normalize_text(value):
    normalized = str(value or "").strip().lower()
    normalized = re.sub(r"[^\w\s-]", "", normalized)
    normalized = re.sub(r"[\s_]+", "-", normalized).strip("-")
    return normalized or "listing"


def _legacy_stable_numeric_id(name, source, digits=12):
    digest = hashlib.sha256(f"{source}:{name}".encode("utf-8")).hexdigest()
    numeric = str(int(digest[:16], 16))
    return numeric[:digits]


def _legacy_stable_asin(name, source):
    digest = hashlib.sha256(f"{source}:{name}".encode("utf-8")).hexdigest().upper()
    return digest[:10]


def is_generated_listing_url(name, source, url):
    normalized_url = str(url or "").strip()
    normalized_name = str(name or "").strip()
    normalized_source = str(source or "").strip().lower()
    slug = _legacy_normalize_text(normalized_name)

    legacy_candidates = {
        f"https://www.ebay.com/itm/{_legacy_stable_numeric_id(normalized_name, normalized_source)}",
        (
            "https://www.willhaben.at/iad/kaufen-und-verkaufen/d/"
            f"{slug}-{_legacy_stable_numeric_id(normalized_name, normalized_source)}"
        ),
        f"https://www.amazon.com/dp/{_legacy_stable_asin(normalized_name, normalized_source)}",
        f"https://www.apple.com/shop/product/{_legacy_stable_asin(normalized_name, normalized_source)}",
        f"https://www.google.com/url?q={slug}-{_legacy_stable_numeric_id(normalized_name, normalized_source, digits=10)}",
    }
    return normalized_url in legacy_candidates


def is_valid_listing_url(url):
    normalized_url = str(url or "").strip()
    if not normalized_url:
        return False

    parsed = urlparse(normalized_url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if not parsed.netloc:
        return False
    if is_placeholder_product_url(normalized_url):
        return False
    if is_search_results_url(normalized_url):
        return False

    netloc = parsed.netloc.lower()
    path = parsed.path.lower()

    if "ebay." in netloc:
        return path.startswith("/itm/")
    if "willhaben." in netloc:
        return "/d/" in path
    if "amazon." in netloc:
        return path.startswith("/dp/") or "/gp/product/" in path
    if "apple.com" in netloc:
        return "/shop/product/" in path

    return len(path.strip("/")) > 0


def validate_listing_url(url):
    normalized_url = str(url or "").strip()
    if is_valid_listing_url(normalized_url):
        return normalized_url
    return ""


def is_invalid_listing_url(url):
    normalized_url = str(url or "").strip()
    if not normalized_url:
        return True
    return not is_valid_listing_url(normalized_url)
