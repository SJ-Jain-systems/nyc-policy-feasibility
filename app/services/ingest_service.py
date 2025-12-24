import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

class IngestError(Exception):
    pass

def fetch_and_clean(url: str) -> str:
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        raise IngestError("URL must start with http:// or https://")

    try:
        r = requests.get(
            url,
            timeout=25,
            headers=DEFAULT_HEADERS,
            allow_redirects=True,
        )
    except requests.RequestException as e:
        raise IngestError(f"Request failed: {e}") from e

    # Common “blocked” statuses
    if r.status_code in (401, 403):
        raise IngestError(f"Blocked by site (HTTP {r.status_code}). Try a different source URL.")
    if r.status_code >= 400:
        raise IngestError(f"HTTP error {r.status_code} while fetching URL.")

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    text = " ".join(text.split())

    if len(text) < 200:
        raise IngestError("Fetched page, but extracted very little text (might be JS-rendered).")

    return text
