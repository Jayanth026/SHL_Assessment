import re
import requests
import trafilatura

def is_url(text: str) -> bool:
    return bool(re.match(r"https?://", text.strip()))

def fetch_jd_text(url: str) -> str:
    html = requests.get(url, timeout=20).text
    extracted = trafilatura.extract(html)
    return extracted if extracted else html
